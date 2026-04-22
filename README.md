# Workplace Attendance Record System

A minimal viable product (MVP) workplace attendance record system built with **Python** and **FastAPI**.

## Features

- **Employee management** – create, read, update and delete employees
- **Check-in / Check-out** – record daily attendance with optional notes
- **Attendance history** – query records filtered by employee and/or date range
- **Attendance summary** – total days present and total minutes worked per employee
- **Auto-generated docs** – interactive Swagger UI at `/docs`

## Tech stack

| Layer | Technology |
|-------|-----------|
| API framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy 2](https://docs.sqlalchemy.org/) |
| Database | SQLite (file `attendance.db`) |
| Validation | Pydantic v2 |
| Server | Uvicorn |

## Project structure

```
.
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── database.py      # SQLAlchemy engine / session / Base
│   ├── models.py        # ORM models (Employee, AttendanceRecord)
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── crud.py          # Database access helpers
│   └── routers/
│       ├── employees.py # Employee CRUD endpoints
│       └── attendance.py# Check-in/out and reporting endpoints
├── tests/
│   └── test_attendance.py
├── requirements.txt
└── README.md
```

## Getting started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the server

```bash
uvicorn app.main:app --reload
```

The API will be available at <http://localhost:8000>.
Interactive docs (Swagger UI) at <http://localhost:8000/docs>.

## API reference

### Employees

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/employees/` | List all employees |
| `POST` | `/employees/` | Create a new employee |
| `GET` | `/employees/{id}` | Get a single employee |
| `PATCH` | `/employees/{id}` | Update an employee |
| `DELETE` | `/employees/{id}` | Delete an employee |

**Create employee body**

```json
{
  "name": "Jane Smith",
  "department": "Engineering",
  "email": "jane@example.com"
}
```

### Attendance

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/attendance/check-in/{employee_id}` | Record check-in for today |
| `POST` | `/attendance/check-out/{employee_id}` | Record check-out for today |
| `GET` | `/attendance/` | List records (filter by `employee_id`, `from_date`, `to_date`) |
| `GET` | `/attendance/summary` | Aggregate totals per employee |

**Check-in body (optional)**

```json
{ "notes": "Working from home" }
```

## Running tests

```bash
pytest tests/ -v
```

