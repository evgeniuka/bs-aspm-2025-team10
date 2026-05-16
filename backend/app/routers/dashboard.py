from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.auth import require_role
from app.database import get_db
from app.models import Client, Program, ProgramExercise, SessionClient, SessionStatus, TrainingSession, User, UserRole
from app.schemas import DashboardOverview
from app.serializers import client_readiness_to_read, session_to_read, today_check_ins_by_client_id

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOverview)
def get_dashboard(
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> DashboardOverview:
    clients = list(
        db.scalars(
            select(Client)
            .where(Client.trainer_id == current_user.id, Client.active.is_(True))
            .order_by(Client.name)
        )
    )
    active_session = db.scalar(
        select(TrainingSession)
        .options(
            selectinload(TrainingSession.clients)
            .selectinload(SessionClient.program)
            .selectinload(Program.exercises)
            .selectinload(ProgramExercise.exercise),
            selectinload(TrainingSession.clients).selectinload(SessionClient.client),
        )
        .where(TrainingSession.trainer_id == current_user.id, TrainingSession.status == SessionStatus.active)
        .order_by(TrainingSession.started_at.desc())
    )
    recent_sessions = list(
        db.scalars(
            select(TrainingSession)
            .options(
                selectinload(TrainingSession.clients)
                .selectinload(SessionClient.program)
                .selectinload(Program.exercises)
                .selectinload(ProgramExercise.exercise),
                selectinload(TrainingSession.clients).selectinload(SessionClient.client),
            )
            .where(TrainingSession.trainer_id == current_user.id)
            .order_by(TrainingSession.started_at.desc())
            .limit(5)
        )
    )
    total_programs = db.scalar(select(func.count(Program.id)).where(Program.trainer_id == current_user.id)) or 0
    completed_sessions = (
        db.scalar(
            select(func.count(TrainingSession.id)).where(
                TrainingSession.trainer_id == current_user.id,
                TrainingSession.status == SessionStatus.completed,
            )
        )
        or 0
    )
    check_ins_by_client_id = today_check_ins_by_client_id(db, [client.id for client in clients])
    return DashboardOverview(
        total_clients=len(clients),
        total_programs=total_programs,
        completed_sessions=completed_sessions,
        active_session=session_to_read(db, active_session) if active_session else None,
        clients=clients,
        recent_sessions=[session_to_read(db, session) for session in recent_sessions],
        today_readiness=[client_readiness_to_read(client, check_ins_by_client_id.get(client.id)) for client in clients],
    )
