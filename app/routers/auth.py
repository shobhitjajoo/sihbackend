from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app import models
from app.utils.auth_utils import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_db,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login with email (username) + password.
    Works for superadmins, administrators, and teachers.
    """

    user = None
    role = None

    # 🔹 1. Try superadmin
    user = db.query(models.SuperAdmin).filter(models.SuperAdmin.email == form_data.username).first()
    if user:
        role = "superadmin"

    # 🔹 2. Try administrator
    if not user:
        user = db.query(models.Administrator).filter(models.Administrator.email == form_data.username).first()
        if user:
            role = "administrator"

    # 🔹 3. Try teacher
    if not user:
        user = db.query(models.Teacher).filter(models.Teacher.email == form_data.username).first()
        if user:
            role = "teacher"

    # 🔹 Validate credentials
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # 🔹 Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": role},  # 👈 sub must be string
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role,
        "email": user.email,
        "name": user.name,
    }