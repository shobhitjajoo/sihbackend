from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/mark", response_model=schemas.AttendanceOut)
def mark_attendance(payload: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    # verify student exists
    student = db.query(models.Student).get(payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    # verify teacher exists
    teacher = db.query(models.Teacher).get(payload.teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    # Optionally: ensure teacher is allowed to mark this student's class (not enforced here)
    att = models.Attendance(student_id=payload.student_id, teacher_id=payload.teacher_id, status=payload.status)
    db.add(att)
    db.commit()
    db.refresh(att)
    return att


@router.get("/", response_model=List[schemas.AttendanceOut])
def list_attendance(student_id: Optional[int] = Query(None), class_id: Optional[int] = Query(None), school_id: Optional[int] = Query(None), start: Optional[str] = Query(None), end: Optional[str] = Query(None), db: Session = Depends(get_db)):
    q = db.query(models.Attendance)
    if student_id:
        q = q.filter(models.Attendance.student_id == student_id)
    elif class_id:
        q = q.join(models.Student).filter(models.Student.class_id == class_id)
    elif school_id:
        q = q.join(models.Student).filter(models.Student.school_id == school_id)

    if start:
        q = q.filter(models.Attendance.date >= datetime.fromisoformat(start))
    if end:
        q = q.filter(models.Attendance.date <= datetime.fromisoformat(end))
    return q.all()