import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from getpass import getpass
from app import models
from app.database import SessionLocal
from app.utils.auth_utils import get_password_hash


def create_superadmin(email: str, password: str, name: str = "spd"):
    db = SessionLocal()
    try:
        existing = db.query(models.SuperAdmin).first()
        if existing:
            print("❌ Superadmin already exists:", existing.email)
            return

        hashed_pw = get_password_hash(password)
        new_superadmin = models.SuperAdmin(
            email=email,
            password=hashed_pw,
            name=name
        )
        db.add(new_superadmin)
        db.commit()
        db.refresh(new_superadmin)
        print(f"✅ Superadmin created successfully: {new_superadmin.email}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_superadmin.py <email>")
        sys.exit(1)

    email = sys.argv[1]
    password = getpass("Enter password: ")
    create_superadmin(email, password)