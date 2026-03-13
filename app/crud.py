from datetime import date, datetime, timezone
from sqlalchemy import Integer, case, func, select
from sqlalchemy.orm import Session
from app import models, schemas


# ── Employee CRUD ─────────────────────────────────────────────────────────────

def get_employee(db: Session, employee_id: int) -> models.Employee | None:
    return db.get(models.Employee, employee_id)


def get_employee_by_email(db: Session, email: str) -> models.Employee | None:
    return db.scalar(select(models.Employee).where(models.Employee.email == email))


def list_employees(db: Session, skip: int = 0, limit: int = 100) -> list[models.Employee]:
    return list(db.scalars(select(models.Employee).offset(skip).limit(limit)))


def create_employee(db: Session, data: schemas.EmployeeCreate) -> models.Employee:
    employee = models.Employee(**data.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def update_employee(
    db: Session, employee: models.Employee, data: schemas.EmployeeUpdate
) -> models.Employee:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee: models.Employee) -> None:
    db.delete(employee)
    db.commit()


# ── Attendance CRUD ───────────────────────────────────────────────────────────

def get_record_for_today(
    db: Session, employee_id: int, work_date: date
) -> models.AttendanceRecord | None:
    return db.scalar(
        select(models.AttendanceRecord).where(
            models.AttendanceRecord.employee_id == employee_id,
            models.AttendanceRecord.work_date == work_date,
        )
    )


def check_in(
    db: Session, employee_id: int, notes: str | None = None
) -> models.AttendanceRecord:
    today = datetime.now(timezone.utc).date()
    record = get_record_for_today(db, employee_id, today)
    if record is None:
        record = models.AttendanceRecord(
            employee_id=employee_id,
            work_date=today,
            check_in=datetime.now(timezone.utc),
            notes=notes,
        )
        db.add(record)
    else:
        record.check_in = datetime.now(timezone.utc)
        if notes is not None:
            record.notes = notes
    db.commit()
    db.refresh(record)
    return record


def check_out(
    db: Session, employee_id: int, notes: str | None = None
) -> models.AttendanceRecord | None:
    today = datetime.now(timezone.utc).date()
    record = get_record_for_today(db, employee_id, today)
    if record is None:
        return None
    record.check_out = datetime.now(timezone.utc)
    if notes is not None:
        record.notes = notes
    db.commit()
    db.refresh(record)
    return record


def list_records(
    db: Session,
    employee_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[models.AttendanceRecord]:
    stmt = select(models.AttendanceRecord)
    if employee_id is not None:
        stmt = stmt.where(models.AttendanceRecord.employee_id == employee_id)
    if from_date is not None:
        stmt = stmt.where(models.AttendanceRecord.work_date >= from_date)
    if to_date is not None:
        stmt = stmt.where(models.AttendanceRecord.work_date <= to_date)
    stmt = stmt.order_by(models.AttendanceRecord.work_date.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def attendance_summary(
    db: Session,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[schemas.AttendanceSummary]:
    """Return per-employee attendance totals using a single aggregated query."""
    # Use julianday to compute duration in minutes (SQLite built-in)
    duration_expr = func.sum(
        case(
            (
                models.AttendanceRecord.check_out.is_not(None)
                & models.AttendanceRecord.check_in.is_not(None),
                func.cast(
                    (
                        func.julianday(models.AttendanceRecord.check_out)
                        - func.julianday(models.AttendanceRecord.check_in)
                    )
                    * 24
                    * 60,
                    Integer,
                ),
            ),
            else_=0,
        )
    )

    stmt = (
        select(
            models.Employee.id,
            models.Employee.name,
            func.count(models.AttendanceRecord.id).label("total_days"),
            func.coalesce(duration_expr, 0).label("total_minutes"),
        )
        .outerjoin(
            models.AttendanceRecord,
            models.AttendanceRecord.employee_id == models.Employee.id,
        )
        .group_by(models.Employee.id, models.Employee.name)
    )
    if from_date is not None:
        stmt = stmt.where(
            (models.AttendanceRecord.work_date >= from_date)
            | models.AttendanceRecord.id.is_(None)
        )
    if to_date is not None:
        stmt = stmt.where(
            (models.AttendanceRecord.work_date <= to_date)
            | models.AttendanceRecord.id.is_(None)
        )

    rows = db.execute(stmt).all()
    return [
        schemas.AttendanceSummary(
            employee_id=row.id,
            employee_name=row.name,
            total_days=row.total_days,
            total_minutes=row.total_minutes,
        )
        for row in rows
    ]
