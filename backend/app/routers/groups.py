from typing import Annotated
from types import SimpleNamespace

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import require_role
from app.database import get_db
from app.models import (
    Client,
    Exercise,
    Program,
    ProgramExercise,
    SessionClient,
    SessionClientStatus,
    SessionStatus,
    TrainingGroup,
    TrainingGroupExercise,
    TrainingGroupMember,
    TrainingSession,
    User,
    UserRole,
)
from app.schemas import MAX_SESSION_CLIENTS, SessionCreated, TrainingGroupCreate, TrainingGroupRead, TrainingGroupSessionCreate, TrainingGroupUpdate
from app.serializers import group_to_read, session_to_read

router = APIRouter(prefix="/groups", tags=["groups"])


def _group_load_options():
    return (
        selectinload(TrainingGroup.members).selectinload(TrainingGroupMember.client),
        selectinload(TrainingGroup.exercises).selectinload(TrainingGroupExercise.exercise),
    )


def _session_load_options():
    return (
        selectinload(TrainingSession.clients)
        .selectinload(SessionClient.program)
        .selectinload(Program.exercises)
        .selectinload(ProgramExercise.exercise),
        selectinload(TrainingSession.clients).selectinload(SessionClient.client),
    )


def _group_query(group_id: int, trainer_id: int):
    return (
        select(TrainingGroup)
        .options(*_group_load_options())
        .where(TrainingGroup.id == group_id, TrainingGroup.trainer_id == trainer_id, TrainingGroup.active.is_(True))
    )


def _active_session_query(trainer_id: int):
    return (
        select(TrainingSession)
        .options(*_session_load_options())
        .where(TrainingSession.trainer_id == trainer_id, TrainingSession.status == SessionStatus.active)
        .order_by(TrainingSession.started_at.desc())
    )


def _session_query(session_id: int, trainer_id: int):
    return (
        select(TrainingSession)
        .options(*_session_load_options())
        .where(TrainingSession.id == session_id, TrainingSession.trainer_id == trainer_id)
    )


def _validate_clients(db: Session, trainer_id: int, client_ids: list[int]) -> list[Client]:
    if len(set(client_ids)) != len(client_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group clients must be unique")

    clients = list(db.scalars(select(Client).where(Client.id.in_(client_ids), Client.trainer_id == trainer_id, Client.active.is_(True))))
    clients_by_id = {client.id: client for client in clients}
    if set(clients_by_id) != set(client_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more clients do not belong to this trainer")
    return [clients_by_id[client_id] for client_id in client_ids]


def _validate_session_clients(db: Session, trainer_id: int, client_ids: list[int]) -> list[Client]:
    if len(set(client_ids)) != len(client_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session clients must be unique")

    clients = list(db.scalars(select(Client).where(Client.id.in_(client_ids), Client.trainer_id == trainer_id, Client.active.is_(True))))
    clients_by_id = {client.id: client for client in clients}
    if set(clients_by_id) != set(client_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more clients do not belong to this trainer")
    return [clients_by_id[client_id] for client_id in client_ids]


def _validate_program_override(db: Session, trainer_id: int, client_id: int, program_id: int | None) -> Program | None:
    if program_id is None:
        return None
    program = db.scalar(
        select(Program)
        .options(selectinload(Program.exercises))
        .where(Program.id == program_id, Program.trainer_id == trainer_id, Program.client_id == client_id)
    )
    if not program:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid client/program assignment")
    if not program.exercises:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Programs must include exercises")
    return program


def _validate_exercises(db: Session, exercise_ids: list[int]) -> None:
    exercises = list(db.scalars(select(Exercise).where(Exercise.id.in_(exercise_ids))))
    if len(exercises) != len(set(exercise_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more exercises do not exist")


def _replace_group_members(group: TrainingGroup, clients: list[Client], db: Session | None = None) -> None:
    group.members.clear()
    if db:
        db.flush()
    for order_index, client in enumerate(clients):
        group.members.append(TrainingGroupMember(client_id=client.id, order_index=order_index))


def _replace_group_exercises(group: TrainingGroup, payload: TrainingGroupCreate | TrainingGroupUpdate, db: Session | None = None) -> None:
    group.exercises.clear()
    if db:
        db.flush()
    for order_index, item in enumerate(payload.exercises):
        group.exercises.append(TrainingGroupExercise(order_index=order_index, **item.model_dump()))


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _create_group_snapshot_program(db: Session, group: TrainingGroup, trainer_id: int, client: Client) -> Program:
    program = Program(
        trainer_id=trainer_id,
        client_id=client.id,
        name=f"{client.name} - {group.name}",
        focus=group.focus,
        notes=f"Session snapshot from saved group: {group.name}.",
        is_session_snapshot=True,
    )
    db.add(program)
    db.flush()
    for order_index, group_exercise in enumerate(sorted(group.exercises, key=lambda item: item.order_index)):
        db.add(
            ProgramExercise(
                program_id=program.id,
                exercise_id=group_exercise.exercise_id,
                order_index=order_index,
                sets=group_exercise.sets,
                reps=group_exercise.reps,
                weight_kg=group_exercise.weight_kg,
                rest_seconds=group_exercise.rest_seconds,
                notes=group_exercise.notes,
            )
        )
    return program


@router.get("", response_model=list[TrainingGroupRead])
def list_groups(
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> list[TrainingGroupRead]:
    groups = list(
        db.scalars(
            select(TrainingGroup)
            .options(*_group_load_options())
            .where(TrainingGroup.trainer_id == current_user.id, TrainingGroup.active.is_(True))
            .order_by(TrainingGroup.created_at.desc())
        )
    )
    return [group_to_read(group) for group in groups]


@router.get("/{group_id}", response_model=TrainingGroupRead)
def get_group(
    group_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> TrainingGroupRead:
    group = db.scalar(_group_query(group_id, current_user.id))
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group_to_read(group)


@router.post("", response_model=TrainingGroupRead, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: TrainingGroupCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> TrainingGroupRead:
    clients = _validate_clients(db, current_user.id, payload.client_ids)
    _validate_exercises(db, [item.exercise_id for item in payload.exercises])

    group = TrainingGroup(
        trainer_id=current_user.id,
        name=payload.name.strip(),
        focus=payload.focus,
        notes=_clean_optional_text(payload.notes),
    )
    db.add(group)
    db.flush()
    _replace_group_members(group, clients)
    _replace_group_exercises(group, payload)
    db.commit()

    group = db.scalar(_group_query(group.id, current_user.id))
    return group_to_read(group)


@router.patch("/{group_id}", response_model=TrainingGroupRead)
def update_group(
    group_id: int,
    payload: TrainingGroupUpdate,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> TrainingGroupRead:
    group = db.scalar(_group_query(group_id, current_user.id))
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    clients = _validate_clients(db, current_user.id, payload.client_ids)
    _validate_exercises(db, [item.exercise_id for item in payload.exercises])
    group.name = payload.name.strip()
    group.focus = payload.focus
    group.notes = _clean_optional_text(payload.notes)
    _replace_group_members(group, clients, db)
    _replace_group_exercises(group, payload, db)
    db.commit()

    group = db.scalar(_group_query(group_id, current_user.id))
    return group_to_read(group)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    group = db.scalar(_group_query(group_id, current_user.id))
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    db.delete(group)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{group_id}/sessions", response_model=SessionCreated, status_code=status.HTTP_201_CREATED)
def start_group_session(
    group_id: int,
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[TrainingGroupSessionCreate | None, Body()] = None,
) -> SessionCreated:
    active_session = db.scalar(_active_session_query(current_user.id))
    if active_session:
        return SessionCreated(session_id=active_session.id, session=session_to_read(db, active_session))

    group = db.scalar(_group_query(group_id, current_user.id))
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    selections = (
        payload.clients
        if payload and payload.clients is not None
        else [SimpleNamespace(client_id=member.client_id, program_id=None) for member in sorted(group.members, key=lambda item: item.order_index)]
    )
    if not selections:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session must include at least one client")
    if len(selections) > MAX_SESSION_CLIENTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Live cockpit supports up to {MAX_SESSION_CLIENTS} clients")
    uses_group_template = any(item.program_id is None for item in selections)
    if uses_group_template and len(group.exercises) < 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group must include at least three exercises")

    clients = _validate_session_clients(db, current_user.id, [item.client_id for item in selections])
    clients_by_id = {client.id: client for client in clients}
    selected_programs = {
        item.client_id: _validate_program_override(db, current_user.id, item.client_id, item.program_id)
        for item in selections
    }

    session = TrainingSession(trainer_id=current_user.id)
    db.add(session)
    db.flush()
    for item in selections:
        client = clients_by_id[item.client_id]
        program = selected_programs[item.client_id] or _create_group_snapshot_program(db, group, current_user.id, client)
        db.add(
            SessionClient(
                session_id=session.id,
                client_id=client.id,
                program_id=program.id,
                status=SessionClientStatus.ready,
            )
        )
    db.commit()

    session = db.scalar(_session_query(session.id, current_user.id))
    return SessionCreated(session_id=session.id, session=session_to_read(db, session))
