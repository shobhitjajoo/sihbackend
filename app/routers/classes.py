from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("/", response_model=List[schemas.ClassOut])
def list_classes(db: Session = Depends(get_db)):
    return db.query(models.Class).all()


@router.get("/{class_id}", response_model=schemas.ClassOut)
def get_class(class_id: int, db: Session = Depends(get_db)):
    cl = db.query(models.Class).get(class_id)
    if not cl:
        raise HTTPException(status_code=404, detail="Class not found")
    return cl


@router.put("/{class_id}", response_model=schemas.ClassOut)
def update_class(class_id: int, payload: schemas.ClassBase, db: Session = Depends(get_db)):
    cl = db.query(models.Class).get(class_id)
    if not cl:
        raise HTTPException(status_code=404, detail="Class not found")
    cl.name = payload.name
    db.commit()
    db.refresh(cl)
    return cl


@router.delete("/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db)):
    cl = db.query(models.Class).get(class_id)
    if not cl:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(cl)
    db.commit()
    return {"detail": "Class deleted"}