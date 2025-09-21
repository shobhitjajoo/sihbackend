"""add face_embedding to student

Revision ID: 0f58c3d8a45e
Revises: 58587514da1d
Create Date: 2025-09-21 10:39:03.515597

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f58c3d8a45e'
down_revision: Union[str, Sequence[str], None] = '58587514da1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('students', sa.Column('face_embedding', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('students', 'face_embedding')
