from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field


# ── Employee schemas ──────────────────────────────────────────────────────────

class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    department: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    department: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None


class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Attendance schemas ────────────────────────────────────────────────────────

class CheckInRequest(BaseModel):
    notes: str | None = Field(None, max_length=500)


class CheckOutRequest(BaseModel):
    notes: str | None = Field(None, max_length=500)


class AttendanceRecordOut(BaseModel):
    id: int
    employee_id: int
    work_date: date
    check_in: datetime | None
    check_out: datetime | None
    notes: str | None
    duration_minutes: int | None = None

    model_config = {"from_attributes": True}


class AttendanceSummary(BaseModel):
    employee_id: int
    employee_name: str
    total_days: int
    total_minutes: int
