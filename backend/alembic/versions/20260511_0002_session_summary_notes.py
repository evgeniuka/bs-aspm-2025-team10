"""add session summary notes

Revision ID: 20260511_0002
Revises: 20260511_0001
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260511_0002"
down_revision = "20260511_0001"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    return column_name in {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if not _has_column("session_clients", "coach_notes"):
        op.add_column("session_clients", sa.Column("coach_notes", sa.Text(), nullable=True))
    if not _has_column("session_clients", "next_focus"):
        op.add_column("session_clients", sa.Column("next_focus", sa.String(length=180), nullable=True))


def downgrade() -> None:
    if _has_column("session_clients", "next_focus"):
        op.drop_column("session_clients", "next_focus")
    if _has_column("session_clients", "coach_notes"):
        op.drop_column("session_clients", "coach_notes")
