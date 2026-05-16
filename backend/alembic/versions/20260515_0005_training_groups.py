"""add saved training groups

Revision ID: 20260515_0005
Revises: 20260515_0004
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260515_0005"
down_revision = "20260515_0004"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("training_groups"):
        op.create_table(
            "training_groups",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("trainer_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("focus", sa.String(length=80), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["trainer_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("training_group_members"):
        op.create_table(
            "training_group_members",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("group_id", sa.Integer(), nullable=False),
            sa.Column("client_id", sa.Integer(), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
            sa.ForeignKeyConstraint(["group_id"], ["training_groups.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("group_id", "client_id", name="uq_training_group_client"),
        )

    if not _has_table("training_group_exercises"):
        op.create_table(
            "training_group_exercises",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("group_id", sa.Integer(), nullable=False),
            sa.Column("exercise_id", sa.Integer(), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False),
            sa.Column("sets", sa.Integer(), nullable=False),
            sa.Column("reps", sa.Integer(), nullable=False),
            sa.Column("weight_kg", sa.Float(), nullable=False),
            sa.Column("rest_seconds", sa.Integer(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
            sa.ForeignKeyConstraint(["group_id"], ["training_groups.id"]),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    if _has_table("training_group_exercises"):
        op.drop_table("training_group_exercises")
    if _has_table("training_group_members"):
        op.drop_table("training_group_members")
    if _has_table("training_groups"):
        op.drop_table("training_groups")
