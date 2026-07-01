"""Shared SQLAlchemy query builders for training sessions.

Several routers (sessions, groups, dashboard, trainee) need the same eager-load shape and
ownership-scoped session lookups; keeping them here avoids copy-pasted query builders.
"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Program, ProgramExercise, SessionClient, SessionStatus, TrainingSession


def session_load_options():
    return (
        selectinload(TrainingSession.clients)
        .selectinload(SessionClient.program)
        .selectinload(Program.exercises)
        .selectinload(ProgramExercise.exercise),
        selectinload(TrainingSession.clients).selectinload(SessionClient.client),
    )


def session_query(session_id: int, trainer_id: int):
    return (
        select(TrainingSession)
        .options(*session_load_options())
        .where(TrainingSession.id == session_id, TrainingSession.trainer_id == trainer_id)
    )


def active_session_query(trainer_id: int):
    return (
        select(TrainingSession)
        .options(*session_load_options())
        .where(TrainingSession.trainer_id == trainer_id, TrainingSession.status == SessionStatus.active)
        .order_by(TrainingSession.started_at.desc())
    )
