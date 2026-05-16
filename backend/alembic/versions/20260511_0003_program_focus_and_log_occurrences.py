"""add program focus and workout log occurrences

Revision ID: 20260511_0003
Revises: 20260511_0002
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260511_0003"
down_revision = "20260511_0002"
branch_labels = None
depends_on = None


def _inspector():
    return inspect(op.get_bind())


def _has_column(table_name: str, column_name: str) -> bool:
    return column_name in {column["name"] for column in _inspector().get_columns(table_name)}


def _has_unique(table_name: str, constraint_name: str) -> bool:
    return constraint_name in {constraint.get("name") for constraint in _inspector().get_unique_constraints(table_name)}


def _has_foreign_key(table_name: str, constraint_name: str) -> bool:
    return constraint_name in {constraint.get("name") for constraint in _inspector().get_foreign_keys(table_name)}


def upgrade() -> None:
    if not _has_column("programs", "focus"):
        op.add_column("programs", sa.Column("focus", sa.String(length=80), nullable=True))

    op.execute("UPDATE programs SET focus = 'Strength Block' WHERE focus IS NULL AND name LIKE '%Strength Block'")
    op.execute("UPDATE programs SET focus = 'Conditioning Circuit' WHERE focus IS NULL AND name LIKE '%Conditioning Circuit'")
    op.execute("UPDATE programs SET focus = 'Core Stability' WHERE focus IS NULL AND name LIKE '%Core Stability'")

    if not _has_column("workout_logs", "program_exercise_id"):
        with op.batch_alter_table("workout_logs") as batch:
            batch.add_column(sa.Column("program_exercise_id", sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE workout_logs
        SET program_exercise_id = (
            SELECT program_exercises.id
            FROM session_clients
            JOIN program_exercises ON program_exercises.program_id = session_clients.program_id
            WHERE session_clients.session_id = workout_logs.session_id
              AND session_clients.client_id = workout_logs.client_id
              AND program_exercises.exercise_id = workout_logs.exercise_id
            ORDER BY program_exercises.order_index
            LIMIT 1
        )
        WHERE program_exercise_id IS NULL
        """
    )

    has_old_unique = _has_unique("workout_logs", "uq_workout_set")
    has_new_unique = _has_unique("workout_logs", "uq_workout_program_set")
    has_new_fk = _has_foreign_key("workout_logs", "fk_workout_logs_program_exercise_id")
    if has_old_unique or not has_new_unique or not has_new_fk:
        with op.batch_alter_table("workout_logs") as batch:
            if has_old_unique:
                batch.drop_constraint("uq_workout_set", type_="unique")
            if not has_new_fk:
                batch.create_foreign_key(
                    "fk_workout_logs_program_exercise_id",
                    "program_exercises",
                    ["program_exercise_id"],
                    ["id"],
                )
            if not has_new_unique:
                batch.create_unique_constraint(
                    "uq_workout_program_set",
                    ["session_id", "client_id", "program_exercise_id", "set_number"],
                )


def downgrade() -> None:
    has_old_unique = _has_unique("workout_logs", "uq_workout_set")
    has_new_unique = _has_unique("workout_logs", "uq_workout_program_set")
    has_new_fk = _has_foreign_key("workout_logs", "fk_workout_logs_program_exercise_id")
    if has_new_unique or has_new_fk or not has_old_unique:
        with op.batch_alter_table("workout_logs") as batch:
            if has_new_unique:
                batch.drop_constraint("uq_workout_program_set", type_="unique")
            if has_new_fk:
                batch.drop_constraint("fk_workout_logs_program_exercise_id", type_="foreignkey")
            if not has_old_unique:
                batch.create_unique_constraint("uq_workout_set", ["session_id", "client_id", "exercise_id", "set_number"])

    if _has_column("workout_logs", "program_exercise_id"):
        with op.batch_alter_table("workout_logs") as batch:
            batch.drop_column("program_exercise_id")
    if _has_column("programs", "focus"):
        op.drop_column("programs", "focus")
