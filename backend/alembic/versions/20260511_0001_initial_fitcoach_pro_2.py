"""initial FitCoach Pro 2 schema

Revision ID: 20260511_0001
Revises:
Create Date: 2026-05-11
"""

from alembic import op

from app.database import Base
import app.models  # noqa: F401

revision = "20260511_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
