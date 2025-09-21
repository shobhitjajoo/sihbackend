from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth,superadmin, administrator, teacher, classes, attendance

# Create tables in dev only (disable in production, use Alembic instead)
# Base.metadata.create_all(bind=engine)

# Initialize app
app = FastAPI(
    title="Smart Attendance API",
    description="Backend for Attendance System with SuperAdmins, Schools, Teachers, and Students",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(superadmin.router)
app.include_router(administrator.router)
app.include_router(teacher.router)
app.include_router(classes.router)
app.include_router(attendance.router)

# Health check
@app.get("/")
def root():
    return {"message": "Welcome to Smart Attendance API 🚀"}