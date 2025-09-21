from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app import database, models


# ==============================
# Config
# ==============================
SECRET_KEY = "your_secret_key_here"   # 🔒 change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simple Bearer scheme (not OAuth2)
bearer_scheme = HTTPBearer()


# ==============================
# Password utils
# ==============================
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ==============================
# JWT utils
# ==============================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==============================
# DB session
# ==============================
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================
# Current user utils
# ==============================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials  # extract Bearer token

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # find user by role
    if role == "superadmin":
        user = db.query(models.SuperAdmin).filter(models.SuperAdmin.id == user_id).first()
    elif role == "administrator":
        user = db.query(models.Administrator).filter(models.Administrator.id == user_id).first()
    elif role == "teacher":
        user = db.query(models.Teacher).filter(models.Teacher.id == user_id).first()
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    return {"id": user.id, "role": role, "name": user.name, "email": user.email}


# ==============================
# Role checker
# ==============================
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user=Depends(get_current_user)):
        if current_user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions",
            )
        return current_user