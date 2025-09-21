from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, superadmin, administrator, teacher, classes, attendance

# Initialize app
app = FastAPI(
    title="Smart Attendance API",
    description="Backend for Attendance System with SuperAdmins, Schools, Teachers, and Students",
    version="1.0.0"
)

# ✅ Allow frontend requests (Flutter Web / Desktop running on localhost:55304)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],          # allow all methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],          # allow all headers (Authorization, Content-Type, etc.)
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