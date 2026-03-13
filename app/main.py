from fastapi import FastAPI
from app.database import Base, engine
from app.routers import employees, attendance

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Workplace Attendance Record System",
    description="A simple MVP API for managing workplace attendance.",
    version="1.0.0",
)

app.include_router(employees.router)
app.include_router(attendance.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "Attendance Record System is running"}
