from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/employees", tags=["employees"])


def _get_or_404(db: Session, employee_id: int):
    employee = crud.get_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.get("/", response_model=list[schemas.EmployeeOut])
def list_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_employees(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(data: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    if crud.get_employee_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this email already exists",
        )
    return crud.create_employee(db, data)


@router.get("/{employee_id}", response_model=schemas.EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, employee_id)


@router.patch("/{employee_id}", response_model=schemas.EmployeeOut)
def update_employee(
    employee_id: int, data: schemas.EmployeeUpdate, db: Session = Depends(get_db)
):
    employee = _get_or_404(db, employee_id)
    if data.email and data.email != employee.email:
        if crud.get_employee_by_email(db, data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An employee with this email already exists",
            )
    return crud.update_employee(db, employee, data)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = _get_or_404(db, employee_id)
    crud.delete_employee(db, employee)
