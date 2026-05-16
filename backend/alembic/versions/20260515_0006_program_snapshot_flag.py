"""add program session snapshot flag

Revision ID: 20260515_0006
Revises: 20260515_0005
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260515_0006"
down_revision = "20260515_0005"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    return column_name in {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if not _has_column("programs", "is_session_snapshot"):
        op.add_column(
            "programs",
            sa.Column("is_session_snapshot", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
        op.execute("UPDATE programs SET is_session_snapshot = FALSE WHERE is_session_snapshot IS NULL")


def downgrade() -> None:
    if _has_column("programs", "is_session_snapshot"):
        op.drop_column("programs", "is_session_snapshot")
