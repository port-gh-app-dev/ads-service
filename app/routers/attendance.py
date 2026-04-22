from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _duration(record) -> int | None:
    if record.check_in and record.check_out:
        delta = record.check_out - record.check_in
        return int(delta.total_seconds() // 60)
    return None


def _to_out(record) -> schemas.AttendanceRecordOut:
    return schemas.AttendanceRecordOut(
        id=record.id,
        employee_id=record.employee_id,
        work_date=record.work_date,
        check_in=record.check_in,
        check_out=record.check_out,
        notes=record.notes,
        duration_minutes=_duration(record),
    )


def _require_employee(db: Session, employee_id: int):
    employee = crud.get_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.post(
    "/check-in/{employee_id}",
    response_model=schemas.AttendanceRecordOut,
    status_code=status.HTTP_200_OK,
)
def check_in(
    employee_id: int, body: schemas.CheckInRequest = schemas.CheckInRequest(), db: Session = Depends(get_db)
):
    _require_employee(db, employee_id)
    record = crud.check_in(db, employee_id, notes=body.notes)
    return _to_out(record)


@router.post(
    "/check-out/{employee_id}",
    response_model=schemas.AttendanceRecordOut,
    status_code=status.HTTP_200_OK,
)
def check_out(
    employee_id: int, body: schemas.CheckOutRequest = schemas.CheckOutRequest(), db: Session = Depends(get_db)
):
    _require_employee(db, employee_id)
    record = crud.check_out(db, employee_id, notes=body.notes)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No check-in found for today. Please check in first.",
        )
    return _to_out(record)


@router.get("/", response_model=list[schemas.AttendanceRecordOut])
def list_attendance(
    employee_id: int | None = Query(None),
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    records = crud.list_records(
        db,
        employee_id=employee_id,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit,
    )
    return [_to_out(r) for r in records]


@router.get("/summary", response_model=list[schemas.AttendanceSummary])
def attendance_summary(
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    db: Session = Depends(get_db),
):
    return crud.attendance_summary(db, from_date=from_date, to_date=to_date)
