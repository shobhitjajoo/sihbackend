from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Token payloads
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
    role: str

# -----------------------------
# SuperAdmin
# -----------------------------
class SuperAdminBase(BaseModel):
    name: str
    email: EmailStr

class SuperAdminCreate(SuperAdminBase):
    password: str

class SuperAdminUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class SuperAdminOut(SuperAdminBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -----------------------------
# Administrator
# -----------------------------
class AdministratorBase(BaseModel):
    name: str
    email: EmailStr

class AdministratorCreate(AdministratorBase):
    password: str

class AdministratorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class AdministratorOut(AdministratorBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# -----------------------------
# School
# -----------------------------
class SchoolBase(BaseModel):
    name: str
    address: Optional[str] = None

class SchoolCreate(SchoolBase):
    administrator_id: int

class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None

class SchoolOut(SchoolBase):
    id: int
    created_at: datetime
    administrator_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Teacher
# -----------------------------
class TeacherBase(BaseModel):
    name: str
    email: EmailStr

class TeacherCreate(TeacherBase):
    password: str
    school_id: int

class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class TeacherOut(TeacherBase):
    id: int
    created_at: datetime
    school_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Class
# -----------------------------
class ClassBase(BaseModel):
    name: str

class ClassCreate(ClassBase):
    school_id: int
    teacher_id: int

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    school_id: Optional[int] = None
    teacher_id: Optional[int] = None

class ClassOut(ClassBase):
    id: int
    created_at: datetime
    school_id: int
    teacher_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Student
# -----------------------------
class StudentBase(BaseModel):
    name: str
    roll_no: str

class StudentCreate(StudentBase):
    class_id: int
    school_id: int

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    roll_no: Optional[str] = None
    class_id: Optional[int] = None
    school_id: Optional[int] = None
    face_embedding: Optional[list[float]]=None

class StudentOut(StudentBase):
    id: int
    created_at: datetime
    class_id: int
    school_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Attendance
# -----------------------------
class AttendanceBase(BaseModel):
    status: str

class AttendanceCreate(AttendanceBase):
    student_id: int
    teacher_id: int

class AttendanceUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceOut(AttendanceBase):
    id: int
    date: datetime
    student_id: int
    teacher_id: int

    class Config:
        orm_mode = True