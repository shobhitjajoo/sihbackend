from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import DateTime, JSON
from sqlalchemy.sql import func

# -----------------------------
# Super Admin
# -----------------------------
class SuperAdmin(Base):
    __tablename__ = "superadmins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships


# -----------------------------
# Administrator
# -----------------------------
class Administrator(Base):
    __tablename__ = "administrators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    # Relationships
    schools = relationship("School", back_populates="administrator")


# -----------------------------
# School
# -----------------------------
class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    address = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    administrator_id = Column(Integer, ForeignKey("administrators.id"), nullable=False)
    # Relationships
    administrator = relationship("Administrator", back_populates="schools")
    teachers = relationship("Teacher", back_populates="school")
    classes = relationship("Class", back_populates="school")


# -----------------------------
# Teacher
# -----------------------------
class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)

    # Relationships
    school = relationship("School", back_populates="teachers")
    classes = relationship("Class", back_populates="teacher")
    attendances = relationship("Attendance", back_populates="teacher")


# -----------------------------
# Class
# -----------------------------
class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # e.g., "10th Grade A"
    created_at = Column(DateTime, server_default=func.now())

    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    # Relationships
    school = relationship("School", back_populates="classes")
    teacher = relationship("Teacher", back_populates="classes")
    students = relationship("Student", back_populates="class_")  # class_ to avoid keyword clash


# -----------------------------
# Student
# -----------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    roll_no = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    face_embedding=Column(JSON,nullable=True)

    # Relationships
    class_ = relationship("Class", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")


# -----------------------------
# Attendance
# -----------------------------
    
class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, server_default=func.now())
    status = Column(String(10), nullable=False)  # Present/Absent
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
# Relationships
    student = relationship("Student", back_populates="attendances")
    teacher = relationship("Teacher", back_populates="attendances")

