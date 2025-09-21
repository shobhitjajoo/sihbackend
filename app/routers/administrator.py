# app/routers/administrator.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime

from app import models, schemas, database
from app.utils.auth_utils import get_current_user, RoleChecker
from app.utils.excel_utils import (
    read_teachers_excel,
    read_classes_excel,
    read_students_excel,
    generate_attendance_excel,
)

router = APIRouter(prefix="/administrator", tags=["Administrator"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
admin_required = RoleChecker(["administrator"])
get_db = database.get_db


# ----------------------------
# Utility: get admin object
# ----------------------------
def get_admin_user(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "administrator":
        raise HTTPException(status_code=403, detail="Not an administrator")
    admin = db.query(models.Administrator).filter(models.Administrator.id == current_user["id"]).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Administrator not found")
    return admin
def get_admin_school(db: Session, admin_id: int):
    school = db.query(models.School).filter(models.School.administrator_id == admin_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found for this administrator")
    return school



# ----------------------------
# 👩‍🏫 Teacher Management
# ----------------------------
@router.post("/teachers", response_model=schemas.TeacherOut, dependencies=[Depends(admin_required)])
def create_teacher(
    teacher: schemas.TeacherCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    if db.query(models.Teacher).filter(models.Teacher.email == teacher.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = pwd_context.hash(teacher.password)
    new_teacher = models.Teacher(
        name=teacher.name,
        email=teacher.email,
        password=hashed_pw,
        school_id=school.id,
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


@router.get("/teachers", response_model=List[schemas.TeacherOut], dependencies=[Depends(admin_required)])
def list_teachers(db: Session = Depends(get_db), admin=Depends(get_admin_user)):
    school = get_admin_school(db, admin.id)
    return db.query(models.Teacher).filter(models.Teacher.school_id == school.id).all()


@router.put("/teachers/{teacher_id}", response_model=schemas.TeacherOut, dependencies=[Depends(admin_required)])
def update_teacher(
    teacher_id: int,
    teacher: schemas.TeacherUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    db_teacher = db.query(models.Teacher).filter(
        models.Teacher.id == teacher_id, models.Teacher.school_id == school.id
    ).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher.name:
        db_teacher.name = teacher.name
    if teacher.email:
        db_teacher.email = teacher.email
    if teacher.password:
        db_teacher.password = pwd_context.hash(teacher.password)

    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.delete("/teachers/{teacher_id}", dependencies=[Depends(admin_required)])
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    teacher = db.query(models.Teacher).filter(
        models.Teacher.id == teacher_id, models.Teacher.school_id == school.id
    ).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    db.delete(teacher)
    db.commit()
    return {"detail": "Teacher deleted"}


@router.post("/teachers/upload-excel", dependencies=[Depends(admin_required)])
def upload_teachers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    """
    Excel should contain columns: name,email,password (password can be plain; it'll be hashed)
    read_teachers_excel must return an iterable of Pydantic-like objects with .name/.email/.password
    """
    teachers = read_teachers_excel(file.file)
    count = 0
    for t in teachers:
        if not db.query(models.Teacher).filter(models.Teacher.email == t.email).first():
            db_teacher = models.Teacher(
                name=t.name,
                email=t.email,
                password=pwd_context.hash(t.password),
                school_id=school.id,
            )
            db.add(db_teacher)
            count += 1
    db.commit()
    return {"message": f"{count} teachers imported successfully"}


# ----------------------------
# 🏫 Class Management
# ----------------------------
@router.post("/classes", response_model=schemas.ClassOut, dependencies=[Depends(admin_required)])
def create_class(
    new_class: schemas.ClassCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    # ensure teacher belongs to same school
    teacher = db.query(models.Teacher).filter(
        models.Teacher.id == new_class.teacher_id, models.Teacher.school_id == school.id
    ).first()
    if not teacher:
        raise HTTPException(status_code=400, detail="Teacher not in this school")

    db_class = models.Class(name=new_class.name, teacher_id=new_class.teacher_id, school_id=school.id)
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class


@router.get("/classes", response_model=List[schemas.ClassOut], dependencies=[Depends(admin_required)])
def list_classes(db: Session = Depends(get_db), admin=Depends(get_admin_user)):
    school = get_admin_school(db, admin.id)
    return db.query(models.Class).filter(models.Class.school_id == school.id).all()


@router.put("/classes/{class_id}", response_model=schemas.ClassOut, dependencies=[Depends(admin_required)])
def update_class(
    class_id: int,
    update_data: schemas.ClassUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    db_class = db.query(models.Class).filter(
        models.Class.id == class_id, models.Class.school_id == school.id
    ).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")

    if update_data.name:
        db_class.name = update_data.name
    if update_data.teacher_id:
        teacher = db.query(models.Teacher).filter(
            models.Teacher.id == update_data.teacher_id, models.Teacher.school_id == school.id
        ).first()
        if not teacher:
            raise HTTPException(status_code=400, detail="Teacher not in this school")
        db_class.teacher_id = update_data.teacher_id

    db.commit()
    db.refresh(db_class)
    return db_class


@router.delete("/classes/{class_id}", dependencies=[Depends(admin_required)])
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    db_class = db.query(models.Class).filter(
        models.Class.id == class_id, models.Class.school_id == school.id
    ).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")

    db.delete(db_class)
    db.commit()
    return {"detail": "Class deleted"}


@router.post("/classes/upload-excel", dependencies=[Depends(admin_required)])
def upload_classes(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    """
    Excel should contain columns: name,teacher_id
    Note: teacher_id should refer to teacher belonging to same school (we do not enforce here; you can extend)
    read_classes_excel should return objects with .name and .teacher_id
    """
    classes = read_classes_excel(file.file)
    count = 0
    for c in classes:
        db_class = models.Class(name=c.name, teacher_id=c.teacher_id, school_id=school.id)
        db.add(db_class)
        count += 1
    db.commit()
    return {"message": f"{count} classes imported successfully"}


# ----------------------------
# 🎓 Student Management 
# ----------------------------

@router.post("/students", response_model=schemas.StudentOut, dependencies=[Depends(admin_required)])
def create_student(
    student: schemas.StudentCreate,db: Session = Depends(get_db),admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    # Verify that the class belongs to this school
    db_class = db.query(models.Class).filter(
        models.Class.id == student.class_id,
        models.Class.school_id == school.id
    ).first()
    if not db_class:
        raise HTTPException(status_code=400, detail="Class does not belong to your school")
    # Create the student inside that class
    new_student = models.Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@router.get("/students", response_model=List[schemas.StudentOut], dependencies=[Depends(admin_required)])
def list_students(db: Session = Depends(get_db), admin=Depends(get_admin_user)):
    school = get_admin_school(db, admin.id)
    return db.query(models.Student).join(models.Class).filter(models.Class.school_id == school.id).all()


@router.put("/students/{student_id}", response_model=schemas.StudentOut, dependencies=[Depends(admin_required)])
def update_student(
    student_id: int,
    student: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    db_student = db.query(models.Student).join(models.Class).filter(
        models.Student.id == student_id, models.Class.school_id == school.id
    ).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student.name:
        db_student.name = student.name
    if student.roll_no:
        db_student.roll_no = student.roll_no

    db.commit()
    db.refresh(db_student)
    return db_student


@router.post("/students/upload-excel", dependencies=[Depends(admin_required)])
def upload_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    """
    Excel expected to contain student id (existing) and fields to update (name, roll_no).
    read_students_excel should return objects with .id, .name, .roll_no
    """
    students = read_students_excel(file.file)
    count = 0
    for s in students:
        db_student = db.query(models.Student).filter(models.Student.id == s.id).first()
        if db_student:
            school = get_admin_school(db, admin.id)
            # Only update if student belongs to admin's school
            cls = db.query(models.Class).filter(models.Class.id == db_student.class_id).first()
            if not cls or cls.school_id != school.id:
                continue
            db_student.name = s.name
            db_student.roll_no = s.roll_no
            count += 1
    db.commit()
    return {"message": f"{count} students updated successfully"}


# ----------------------------
# 📊 Attendance Stats + Excel
# ----------------------------
def _apply_date_filters(query, date_column, month: Optional[int], year: Optional[int], start_date: Optional[datetime], end_date: Optional[datetime]):
    """
    Helper to apply month/year or start/end filters to a SQLAlchemy query.
    """
    if month and year:
        query = query.filter(func.extract("month", date_column) == month, func.extract("year", date_column) == year)
    if start_date:
        query = query.filter(date_column >= start_date)
    if end_date:
        query = query.filter(date_column <= end_date)
    return query


@router.get("/attendance/student/{student_id}", dependencies=[Depends(admin_required)])
def student_attendance(
    student_id: int,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=1900),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    student = db.query(models.Student).join(models.Class).filter(
        models.Student.id == student_id, models.Class.school_id == school.id
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    q = db.query(models.Attendance).filter(models.Attendance.student_id == student.id)
    q = _apply_date_filters(q, models.Attendance.date, month, year, start_date, end_date)
    records = q.all()
    total = len(records)
    present = len([r for r in records if r.status.lower() == "present"])
    return {
        "student": student.name,
        "total_classes": total,
        "present": present,
        "attendance_%": (present / total * 100) if total else 0,
    }


@router.get("/attendance/class/{class_id}", dependencies=[Depends(admin_required)])
def class_attendance(
    class_id: int,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=1900),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    db_class = db.query(models.Class).filter(
        models.Class.id == class_id, models.Class.school_id == school.id
    ).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")

    students = db.query(models.Student).filter(models.Student.class_id == db_class.id).all()
    stats = []
    for s in students:
        q = db.query(models.Attendance).filter(models.Attendance.student_id == s.id)
        q = _apply_date_filters(q, models.Attendance.date, month, year, start_date, end_date)
        records = q.all()
        total = len(records)
        present = len([r for r in records if r.status.lower() == "present"])
        stats.append({"student": s.name, "present": present, "total": total})
    return {"class": db_class.name, "stats": stats}


@router.get("/attendance/school", dependencies=[Depends(admin_required)])
def school_attendance(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=1900),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    school = get_admin_school(db, admin.id)
    classes = db.query(models.Class).filter(models.Class.school_id == school.id).all()
    school_total, school_present = 0, 0
    summary = []

    for c in classes:
        students = db.query(models.Student).filter(models.Student.class_id == c.id).all()
        class_total, class_present = 0, 0
        for s in students:
            q = db.query(models.Attendance).filter(models.Attendance.student_id == s.id)
            q = _apply_date_filters(q, models.Attendance.date, month, year, start_date, end_date)
            records = q.all()
            class_total += len(records)
            class_present += len([r for r in records if r.status.lower() == "present"])
        school_total += class_total
        school_present += class_present
        summary.append({
            "class": c.name,
            "total": class_total,
            "present": class_present,
            "attendance_%": (class_present / class_total * 100) if class_total else 0
        })

    return {
        "school_id": admin.school_id,
        "summary": summary,
        "overall_%": (school_present / school_total * 100) if school_total else 0
    }


@router.get("/attendance/school/excel", dependencies=[Depends(admin_required)])
def export_school_attendance(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=1900),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    q = (
        db.query(models.Attendance)
        .join(models.Student)
        .join(models.Class)
        .filter(models.Class.school_id == admin.school_id)
    )
    q = _apply_date_filters(q, models.Attendance.date, month, year, start_date, end_date)
    records = q.all()

    # convert attendance rows into serializable records for excel helper
    records_for_excel = []
    for a in records:
        records_for_excel.append({
            "id": a.id,
            "student_id": a.student_id,
            "teacher_id": a.teacher_id,
            "status": a.status,
            "date": a.date.isoformat() if a.date else None,
        })

    buf = generate_attendance_excel(records_for_excel)  # should return BytesIO
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=school_{admin.school_id}_attendance.xlsx"},
    )