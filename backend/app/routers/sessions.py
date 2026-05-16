from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import COOKIE_NAME, get_user_from_token, require_role
from app.config import get_settings
from app.database import SessionLocal, get_db
from app.models import (
    Client,
    Program,
    ProgramExercise,
    SessionClient,
    SessionClientStatus,
    SessionStatus,
    TrainingSession,
    User,
    UserRole,
)
from app.realtime import manager
from app.schemas import (
    CompleteSetRequest,
    RealtimeEvent,
    SessionClientSummaryUpdate,
    SessionCreate,
    SessionCreated,
    SessionSummaryRead,
    TrainingSessionRead,
)
from app.services import session_service
from app.services.session_service import CompleteSetCommand
from app.serializers import session_summary_to_read, session_to_read

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _session_load_options():
    return (
        selectinload(TrainingSession.clients)
        .selectinload(SessionClient.program)
        .selectinload(Program.exercises)
        .selectinload(ProgramExercise.exercise),
        selectinload(TrainingSession.clients).selectinload(SessionClient.client),
    )


def _session_query(session_id: int, trainer_id: int):
    return (
        select(TrainingSession)
        .options(*_session_load_options())
        .where(TrainingSession.id == session_id, TrainingSession.trainer_id == trainer_id)
    )


def _active_session_query(trainer_id: int):
    return (
        select(TrainingSession)
        .options(*_session_load_options())
        .where(TrainingSession.trainer_id == trainer_id, TrainingSession.status == SessionStatus.active)
        .order_by(TrainingSession.started_at.desc())
    )


def _validate_session_payload(db: Session, trainer_id: int, payload: SessionCreate) -> list[tuple[int, int]]:
    if len(payload.client_ids) != len(payload.program_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Each client must have a program")
    pairs = list(zip(payload.client_ids, payload.program_ids, strict=True))
    if len({client_id for client_id, _ in pairs}) != len(pairs):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Clients must be unique")

    for client_id, program_id in pairs:
        client = db.scalar(select(Client).where(Client.id == client_id, Client.trainer_id == trainer_id))
        program = db.scalar(
            select(Program).where(
                Program.id == program_id,
                Program.trainer_id == trainer_id,
                Program.client_id == client_id,
            )
        )
        if not client or not program:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid client/program assignment")
        if not program.exercises:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Programs must include exercises")
    return pairs


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


async def _broadcast_session(db: Session, session: TrainingSession, event_type: str) -> TrainingSessionRead:
    session_read = session_to_read(db, session)
    payload = RealtimeEvent(type=event_type, session=session_read).model_dump(mode="json")
    await manager.broadcast(session.id, payload)
    return session_read


@router.post("", response_model=SessionCreated, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> SessionCreated:
    active_session = db.scalar(_active_session_query(current_user.id))
    if active_session:
        return SessionCreated(session_id=active_session.id, session=session_to_read(db, active_session))

    pairs = _validate_session_payload(db, current_user.id, payload)
    session = TrainingSession(trainer_id=current_user.id)
    db.add(session)
    db.flush()
    for client_id, program_id in pairs:
        db.add(
            SessionClient(
                session_id=session.id,
                client_id=client_id,
                program_id=program_id,
                status=SessionClientStatus.ready,
            )
        )
    db.commit()
    session = db.scalar(_session_query(session.id, current_user.id))
    return SessionCreated(session_id=session.id, session=session_to_read(db, session))


@router.get("/active", response_model=TrainingSessionRead | None)
def get_active_session(
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> TrainingSessionRead | None:
    session = db.scalar(_active_session_query(current_user.id))
    return session_to_read(db, session) if session else None


@router.get("/{session_id}", response_model=TrainingSessionRead)
def get_session(
    session_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> TrainingSessionRead:
    session = db.scalar(_session_query(session_id, current_user.id))
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session_to_read(db, session)


@router.get("/{session_id}/summary", response_model=SessionSummaryRead)
def get_session_summary(
    session_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> SessionSummaryRead:
    session = db.scalar(_session_query(session_id, current_user.id))
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session_summary_to_read(db, session)


@router.post("/{session_id}/clients/{client_id}/start-next-set", response_model=TrainingSessionRead)
async def start_next_set(
    session_id: int,
    client_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> TrainingSessionRead:
    session = db.scalar(_session_query(session_id, current_user.id))
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    result = session_service.start_next_set(session, client_id)
    db.commit()
    session = db.scalar(_session_query(session_id, current_user.id))
    return await _broadcast_session(db, session, result.event_type)


@router.post("/{session_id}/clients/{client_id}/complete-set", response_model=TrainingSessionRead)
async def complete_set(
    session_id: int,
    client_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
    payload: CompleteSetRequest | None = Body(default=None),
) -> TrainingSessionRead:
    session = db.scalar(_session_query(session_id, current_user.id))
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    command = CompleteSetCommand(**payload.model_dump()) if payload else CompleteSetCommand()
    result = session_service.complete_set(db, session, client_id, command)
    db.commit()
    session = db.scalar(_session_query(session_id, current_user.id))
    return await _broadcast_session(db, session, result.event_type)


@router.post("/{session_id}/clients/{client_id}/undo-last-set", response_model=TrainingSessionRead)
async def undo_last_set(
    session_id: int,
    client_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> TrainingSessionRead:
    session = db.scalar(_session_query(session_id, current_user.id))
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    result = session_service.undo_last_set(db, session, client_id)
    db.commit()
    session = db.scalar(_session_query(session_id, current_user.id))
    return await _broadcast_session(db, session, result.event_type)


@router.post("/{session_id}/end", response_model=TrainingSessionRead)
async def end_session(
    session_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> TrainingSessionRead:
    session = db.scalar(_session_query(session_id, current_user.id))
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    result = session_service.end_session(session)
    db.commit()
    session = db.scalar(_session_query(session_id, current_user.id))
    return await _broadcast_session(db, session, result.event_type)


@router.patch("/{session_id}/clients/{client_id}/summary", response_model=SessionSummaryRead)
def update_session_client_summary(
    session_id: int,
    client_id: int,
    payload: SessionClientSummaryUpdate,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> SessionSummaryRead:
    session = db.scalar(_session_query(session_id, current_user.id))
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    session_client = next((item for item in session.clients if item.client_id == client_id), None)
    if not session_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session client not found")

    if "coach_notes" in payload.model_fields_set:
        session_client.coach_notes = _clean_optional_text(payload.coach_notes)
    if "next_focus" in payload.model_fields_set:
        session_client.next_focus = _clean_optional_text(payload.next_focus)

    db.commit()
    session = db.scalar(_session_query(session_id, current_user.id))
    return session_summary_to_read(db, session)


@router.websocket("/ws/{session_id}")
async def session_socket(websocket: WebSocket, session_id: int) -> None:
    origin = websocket.headers.get("origin")
    if origin and origin not in get_settings().frontend_origins:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    token = websocket.cookies.get(COOKIE_NAME)
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    with SessionLocal() as db:
        try:
            current_user = get_user_from_token(db, token)
        except HTTPException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        if current_user.role != UserRole.trainer:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        session = db.scalar(_session_query(session_id, current_user.id))
        if not session:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    connected = False
    try:
        await manager.connect(session_id, websocket)
        connected = True
        with SessionLocal() as db:
            session = db.scalar(_session_query(session_id, current_user.id))
            if session:
                await websocket.send_json(
                    RealtimeEvent(
                        type="session_joined",
                        session=session_to_read(db, session),
                    ).model_dump(mode="json")
                )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if connected:
            manager.disconnect(session_id, websocket)
    except Exception:
        if connected:
            manager.disconnect(session_id, websocket)
        raise
