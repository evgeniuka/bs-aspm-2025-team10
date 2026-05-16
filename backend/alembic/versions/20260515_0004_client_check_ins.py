"""add client daily check-ins

Revision ID: 20260515_0004
Revises: 20260511_0003
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260515_0004"
down_revision = "20260511_0003"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if _has_table("client_check_ins"):
        return

    op.create_table(
        "client_check_ins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("submitted_on", sa.Date(), nullable=False),
        sa.Column("energy_level", sa.Integer(), nullable=False),
        sa.Column("sleep_quality", sa.Integer(), nullable=False),
        sa.Column("soreness_level", sa.Integer(), nullable=False),
        sa.Column("pain_notes", sa.Text(), nullable=True),
        sa.Column("training_goal", sa.String(length=220), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("client_id", "submitted_on", name="uq_client_check_in_day"),
    )


def downgrade() -> None:
    if _has_table("client_check_ins"):
        op.drop_table("client_check_ins")
