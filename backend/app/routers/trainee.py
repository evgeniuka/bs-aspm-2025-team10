from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import require_role
from app.database import get_db
from app.models import Client, ClientCheckIn, Program, ProgramExercise, SessionClient, TrainingSession, User, UserRole, utc_today
from app.schemas import ClientCheckInRead, ClientCheckInUpsert, ClientDetailRead, ProgramRead, SessionSummaryRead
from app.serializers import check_in_to_read, client_analytics_to_read, client_session_summary_to_read, program_to_read, session_summary_to_read, today_check_ins_by_client_id

router = APIRouter(prefix="/trainee", tags=["trainee"])


def _current_client(db: Session, current_user: User) -> Client:
    client = db.scalar(
        select(Client).where(
            Client.user_id == current_user.id,
            Client.active.is_(True),
        )
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found")
    return client


def _program_load_options():
    return selectinload(Program.exercises).selectinload(ProgramExercise.exercise)


def _session_load_options():
    return (
        selectinload(TrainingSession.clients)
        .selectinload(SessionClient.program)
        .selectinload(Program.exercises)
        .selectinload(ProgramExercise.exercise),
        selectinload(TrainingSession.clients).selectinload(SessionClient.client),
    )


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


@router.get("/me", response_model=ClientDetailRead)
def get_my_client_portal(
    current_user: Annotated[User, Depends(require_role(UserRole.trainee))],
    db: Annotated[Session, Depends(get_db)],
) -> ClientDetailRead:
    client = _current_client(db, current_user)
    programs = list(
        db.scalars(
            select(Program)
            .options(_program_load_options())
            .where(Program.client_id == client.id, Program.trainer_id == client.trainer_id)
            .order_by(Program.created_at.desc())
        )
    )
    session_clients = list(
        db.scalars(
            select(SessionClient)
            .options(
                selectinload(SessionClient.session),
                selectinload(SessionClient.client),
                selectinload(SessionClient.program).selectinload(Program.exercises).selectinload(ProgramExercise.exercise),
            )
            .join(TrainingSession, TrainingSession.id == SessionClient.session_id)
            .where(SessionClient.client_id == client.id, TrainingSession.trainer_id == client.trainer_id)
            .order_by(TrainingSession.started_at.desc())
        )
    )
    return ClientDetailRead(
        client=client,
        programs=[program_to_read(program) for program in programs],
        analytics=client_analytics_to_read(db, session_clients),
        recent_sessions=[client_session_summary_to_read(db, item) for item in session_clients[:8]],
        today_check_in=(
            check_in_to_read(check_in)
            if (check_in := today_check_ins_by_client_id(db, [client.id]).get(client.id))
            else None
        ),
    )


@router.get("/check-in/today", response_model=ClientCheckInRead | None)
def get_my_today_check_in(
    current_user: Annotated[User, Depends(require_role(UserRole.trainee))],
    db: Annotated[Session, Depends(get_db)],
) -> ClientCheckInRead | None:
    client = _current_client(db, current_user)
    check_in = today_check_ins_by_client_id(db, [client.id]).get(client.id)
    return check_in_to_read(check_in) if check_in else None


@router.put("/check-in/today", response_model=ClientCheckInRead)
def upsert_my_today_check_in(
    payload: ClientCheckInUpsert,
    current_user: Annotated[User, Depends(require_role(UserRole.trainee))],
    db: Annotated[Session, Depends(get_db)],
) -> ClientCheckInRead:
    client = _current_client(db, current_user)
    submitted_on = utc_today()
    check_in = db.scalar(
        select(ClientCheckIn).where(
            ClientCheckIn.client_id == client.id,
            ClientCheckIn.submitted_on == submitted_on,
        )
    )
    if not check_in:
        check_in = ClientCheckIn(client_id=client.id, submitted_on=submitted_on)
        db.add(check_in)

    check_in.energy_level = payload.energy_level
    check_in.sleep_quality = payload.sleep_quality
    check_in.soreness_level = payload.soreness_level
    check_in.pain_notes = _clean_optional_text(payload.pain_notes)
    check_in.training_goal = _clean_optional_text(payload.training_goal)
    db.commit()
    db.refresh(check_in)
    return check_in_to_read(check_in)


@router.get("/programs/{program_id}", response_model=ProgramRead)
def get_my_program(
    program_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainee))],
    db: Annotated[Session, Depends(get_db)],
) -> ProgramRead:
    client = _current_client(db, current_user)
    program = db.scalar(
        select(Program)
        .options(_program_load_options())
        .where(Program.id == program_id, Program.client_id == client.id, Program.trainer_id == client.trainer_id)
    )
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return program_to_read(program)


@router.get("/sessions/{session_id}/summary", response_model=SessionSummaryRead)
def get_my_session_summary(
    session_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainee))],
    db: Annotated[Session, Depends(get_db)],
) -> SessionSummaryRead:
    client = _current_client(db, current_user)
    session = db.scalar(
        select(TrainingSession)
        .options(*_session_load_options())
        .join(SessionClient, SessionClient.session_id == TrainingSession.id)
        .where(
            TrainingSession.id == session_id,
            TrainingSession.trainer_id == client.trainer_id,
            SessionClient.client_id == client.id,
        )
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    summary = session_summary_to_read(db, session)
    summary.clients = [item for item in summary.clients if item.client_id == client.id]
    summary.total_clients = len(summary.clients)
    summary.total_sets_completed = sum(item.sets_completed for item in summary.clients)
    summary.total_planned_sets = sum(item.planned_sets for item in summary.clients)
    summary.total_volume_kg = sum(item.volume_kg for item in summary.clients)
    return summary
