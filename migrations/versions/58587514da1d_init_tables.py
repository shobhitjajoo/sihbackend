"""init tables

Revision ID: 58587514da1d
Revises: 
Create Date: 2025-09-14 11:17:05.140446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58587514da1d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create table for admins
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(120), unique=True, nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Teachers
    op.create_table(
        "teachers",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(120), unique=True, nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Students
    op.create_table(
        "students",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("roll_no", sa.String(50), unique=True, nullable=False),
        sa.Column("class", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Attendance records
    op.create_table(
        "attendance",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("student_id", sa.Integer, sa.ForeignKey("students.id"), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("status", sa.String(10), nullable=False),  # Present/Absent
        sa.Column("marked_by", sa.Integer, sa.ForeignKey("teachers.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("attendance")
    op.drop_table("students")
    op.drop_table("teachers")
    op.drop_table("admins")