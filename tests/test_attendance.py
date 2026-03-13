import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


# ── Helper ────────────────────────────────────────────────────────────────────

def create_employee(client, name="Alice", department="Engineering", email="alice@example.com"):
    resp = client.post(
        "/employees/",
        json={"name": name, "department": department, "email": email},
    )
    assert resp.status_code == 201
    return resp.json()


# ── Health check ──────────────────────────────────────────────────────────────

def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── Employee endpoints ────────────────────────────────────────────────────────

def test_create_employee(client):
    data = create_employee(client)
    assert data["name"] == "Alice"
    assert data["department"] == "Engineering"
    assert data["email"] == "alice@example.com"
    assert "id" in data


def test_create_duplicate_email_returns_409(client):
    create_employee(client)
    resp = client.post(
        "/employees/",
        json={"name": "Bob", "department": "HR", "email": "alice@example.com"},
    )
    assert resp.status_code == 409


def test_list_employees(client):
    create_employee(client)
    resp = client.get("/employees/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_employee(client):
    emp = create_employee(client)
    resp = client.get(f"/employees/{emp['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == emp["id"]


def test_get_employee_not_found(client):
    resp = client.get("/employees/9999")
    assert resp.status_code == 404


def test_update_employee(client):
    emp = create_employee(client)
    resp = client.patch(f"/employees/{emp['id']}", json={"department": "Product"})
    assert resp.status_code == 200
    assert resp.json()["department"] == "Product"


def test_delete_employee(client):
    emp = create_employee(client)
    resp = client.delete(f"/employees/{emp['id']}")
    assert resp.status_code == 204
    resp = client.get(f"/employees/{emp['id']}")
    assert resp.status_code == 404


# ── Attendance endpoints ──────────────────────────────────────────────────────

def test_check_in(client):
    emp = create_employee(client)
    resp = client.post(f"/attendance/check-in/{emp['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_id"] == emp["id"]
    assert data["check_in"] is not None
    assert data["check_out"] is None


def test_check_out(client):
    emp = create_employee(client)
    client.post(f"/attendance/check-in/{emp['id']}")
    resp = client.post(f"/attendance/check-out/{emp['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["check_out"] is not None
    assert data["duration_minutes"] is not None
    assert data["duration_minutes"] >= 0


def test_check_out_without_check_in_returns_400(client):
    emp = create_employee(client)
    resp = client.post(f"/attendance/check-out/{emp['id']}")
    assert resp.status_code == 400


def test_check_in_unknown_employee_returns_404(client):
    resp = client.post("/attendance/check-in/9999")
    assert resp.status_code == 404


def test_list_attendance(client):
    emp = create_employee(client)
    client.post(f"/attendance/check-in/{emp['id']}")
    resp = client.get("/attendance/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_list_attendance_filter_by_employee(client):
    emp1 = create_employee(client, name="Alice", email="alice@example.com")
    emp2 = create_employee(client, name="Bob", email="bob@example.com")
    client.post(f"/attendance/check-in/{emp1['id']}")
    client.post(f"/attendance/check-in/{emp2['id']}")
    resp = client.get(f"/attendance/?employee_id={emp1['id']}")
    assert resp.status_code == 200
    records = resp.json()
    assert len(records) == 1
    assert records[0]["employee_id"] == emp1["id"]


def test_attendance_summary(client):
    emp = create_employee(client)
    client.post(f"/attendance/check-in/{emp['id']}")
    client.post(f"/attendance/check-out/{emp['id']}")
    resp = client.get("/attendance/summary")
    assert resp.status_code == 200
    summaries = resp.json()
    assert len(summaries) == 1
    assert summaries[0]["employee_id"] == emp["id"]
    assert summaries[0]["total_days"] == 1


def test_check_in_with_notes(client):
    emp = create_employee(client)
    resp = client.post(
        f"/attendance/check-in/{emp['id']}", json={"notes": "Working from home"}
    )
    assert resp.status_code == 200
    assert resp.json()["notes"] == "Working from home"
