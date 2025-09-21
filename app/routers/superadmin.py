from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app import models, schemas
from app.utils.auth_utils import get_db, RoleChecker
from app.utils.auth_utils import get_password_hash
from app.utils.excel_utils import export_students_to_excel, export_attendance_to_excel

router = APIRouter(
    prefix="/superadmin",
    tags=["SuperAdmin"],
)

superadmin_required = RoleChecker(["superadmin"])

# -----------------------------
# SuperAdmin CRUD
# -----------------------------
@router.post("/", response_model=schemas.SuperAdminOut, dependencies=[Depends(superadmin_required)])
def create_superadmin(superadmin: schemas.SuperAdminCreate, db: Session = Depends(get_db)):
    if db.query(models.SuperAdmin).filter(models.SuperAdmin.email == superadmin.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_superadmin = models.SuperAdmin(**superadmin.dict())
    db.add(new_superadmin)
    db.commit()
    db.refresh(new_superadmin)
    return new_superadmin


@router.get("/", response_model=List[schemas.SuperAdminOut], dependencies=[Depends(superadmin_required)])
def list_superadmins(db: Session = Depends(get_db)):
    return db.query(models.SuperAdmin).all()


@router.put("/{superadmin_id}", response_model=schemas.SuperAdminOut, dependencies=[Depends(superadmin_required)])
def update_superadmin(superadmin_id: int, update: schemas.SuperAdminCreate, db: Session = Depends(get_db)):
    superadmin = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == superadmin_id).first()
    if not superadmin:
        raise HTTPException(status_code=404, detail="SuperAdmin not found")
    for key, value in update.dict().items():
        setattr(superadmin, key, value)
    db.commit()
    db.refresh(superadmin)
    return superadmin


@router.delete("/{superadmin_id}", dependencies=[Depends(superadmin_required)])
def delete_superadmin(superadmin_id: int, db: Session = Depends(get_db)):
    superadmin = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == superadmin_id).first()
    if not superadmin:
        raise HTTPException(status_code=404, detail="SuperAdmin not found")
    db.delete(superadmin)
    db.commit()
    return {"message": "SuperAdmin deleted successfully"}


# -----------------------------
# Administrators CRUD
# -----------------------------
@router.post("/administrators", response_model=schemas.AdministratorOut, dependencies=[Depends(superadmin_required)])
def create_administrator(admin: schemas.AdministratorCreate, db: Session = Depends(get_db)):
    if db.query(models.Administrator).filter(models.Administrator.email == admin.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_admin = models.Administrator(name=admin.name,
        email=admin.email,
        password=get_password_hash(admin.password),  # ✅ hash here
)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin


@router.get("/administrators", response_model=List[schemas.AdministratorOut], dependencies=[Depends(superadmin_required)])
def list_administrators(db: Session = Depends(get_db)):
    return db.query(models.Administrator).all()


@router.put("/administrators/{admin_id}", response_model=schemas.AdministratorOut, dependencies=[Depends(superadmin_required)])
def update_administrator(admin_id: int, update: schemas.AdministratorCreate, db: Session = Depends(get_db)):
    admin = db.query(models.Administrator).filter(models.Administrator.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Administrator not found")
    admin.name = update.name
    admin.email = update.email
    if update.password:  # ✅ hash on update
        admin.password = get_password_hash(update.password)


    db.commit()
    db.refresh(admin)
    return admin


@router.delete("/administrators/{admin_id}", dependencies=[Depends(superadmin_required)])
def delete_administrator(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(models.Administrator).filter(models.Administrator.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Administrator not found")
    db.delete(admin)
    db.commit()
    return {"message": "Administrator deleted successfully"}


# -----------------------------
# Schools CRUD
# -----------------------------
@router.post("/schools", response_model=schemas.SchoolOut, dependencies=[Depends(superadmin_required)])
def create_school(school: schemas.SchoolCreate, db: Session = Depends(get_db)):
    new_school = models.School(**school.dict())
    db.add(new_school)
    db.commit()
    db.refresh(new_school)
    return new_school


@router.get("/schools", response_model=List[schemas.SchoolOut], dependencies=[Depends(superadmin_required)])
def list_schools(db: Session = Depends(get_db)):
    return db.query(models.School).all()


@router.put("/schools/{school_id}", response_model=schemas.SchoolOut, dependencies=[Depends(superadmin_required)])
def update_school(school_id: int, update: schemas.SchoolCreate, db: Session = Depends(get_db)):
    school = db.query(models.School).filter(models.School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    for key, value in update.dict().items():
        setattr(school, key, value)
    db.commit()
    db.refresh(school)
    return school


@router.delete("/schools/{school_id}", dependencies=[Depends(superadmin_required)])
def delete_school(school_id: int, db: Session = Depends(get_db)):
    school = db.query(models.School).filter(models.School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    db.delete(school)
    db.commit()
    return {"message": "School deleted successfully"}


# -----------------------------
# Teachers CRUD
# -----------------------------
@router.post("/teachers", response_model=schemas.TeacherOut, dependencies=[Depends(superadmin_required)])
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    if db.query(models.Teacher).filter(models.Teacher.email == teacher.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_teacher = models.Teacher(name=teacher.name,
        email=teacher.email,
        password=get_password_hash(teacher.password),
        school_id=teacher.school_id)
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


@router.get("/teachers", response_model=List[schemas.TeacherOut], dependencies=[Depends(superadmin_required)])
def list_teachers(db: Session = Depends(get_db)):
    return db.query(models.Teacher).all()


@router.put("/teachers/{teacher_id}", response_model=schemas.TeacherOut, dependencies=[Depends(superadmin_required)])
def update_teacher(teacher_id: int, update: schemas.TeacherCreate, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    teacher.name = update.name
    teacher.email = update.email
    if update.password:  # ✅ hash only if provided
        teacher.password = get_password_hash(update.password)
    teacher.school_id = update.school_id

    db.commit()
    db.refresh(teacher)
    return teacher


@router.delete("/teachers/{teacher_id}", dependencies=[Depends(superadmin_required)])
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(teacher)
    db.commit()
    return {"message": "Teacher deleted successfully"}


# -----------------------------
# Students CRUD + Excel Export
# -----------------------------
@router.post("/students", response_model=schemas.StudentOut, dependencies=[Depends(superadmin_required)])
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    new_student = models.Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@router.get("/students", response_model=List[schemas.StudentOut], dependencies=[Depends(superadmin_required)])
def list_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


@router.put("/students/{student_id}", response_model=schemas.StudentOut, dependencies=[Depends(superadmin_required)])
def update_student(student_id: int, update: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, value in update.dict().items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/students/{student_id}", dependencies=[Depends(superadmin_required)])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}


@router.get("/students/export-excel", dependencies=[Depends(superadmin_required)])
def export_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    students_data = [
        {"id": s.id, "name": s.name, "roll_no": s.roll_no, "class_name": s.class_name}
        for s in students
    ]
    return export_students_to_excel(students_data)


# -----------------------------
# Attendance Reports (view/export)
# -----------------------------
@router.get("/attendance/report", dependencies=[Depends(superadmin_required)])
def attendance_report(
    db: Session = Depends(get_db),
    school_id: Optional[int] = None,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    query = db.query(models.Attendance)
    if school_id:
        query = query.filter(models.Attendance.school_id == school_id)
    if class_id:
        query = query.filter(models.Attendance.class_id == class_id)
    if student_id:
        query = query.filter(models.Attendance.student_id == student_id)
    if start_date:
        query = query.filter(models.Attendance.date >= start_date)
    if end_date:
        query = query.filter(models.Attendance.date <= end_date)
    return query.all()


@router.get("/attendance/report/excel", dependencies=[Depends(superadmin_required)])
def attendance_report_excel(
    db: Session = Depends(get_db),
    school_id: Optional[int] = None,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    query = db.query(models.Attendance)
    if school_id:
        query = query.filter(models.Attendance.school_id == school_id)
    if class_id:
        query = query.filter(models.Attendance.class_id == class_id)
    if student_id:
        query = query.filter(models.Attendance.student_id == student_id)
    if start_date:
        query = query.filter(models.Attendance.date >= start_date)
    if end_date:
        query = query.filter(models.Attendance.date <= end_date)

    attendances = query.all()
    attendance_data = [
        {"student_name": a.student.name, "date": a.date, "status": a.status}
        for a in attendances
    ]
    return export_attendance_to_excel(attendance_data)