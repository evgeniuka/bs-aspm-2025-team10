from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    ProgramExercise,
    SessionClient,
    SessionClientStatus,
    SessionStatus,
    TrainingSession,
    WorkoutLog,
)


@dataclass(frozen=True)
class CompleteSetCommand:
    program_exercise_id: int | None = None
    exercise_id: int | None = None
    set_number: int | None = None
    reps_completed: int | None = None
    weight_kg: float | None = None


@dataclass(frozen=True)
class SessionMutationResult:
    session: TrainingSession
    event_type: str


def start_next_set(session: TrainingSession, client_id: int) -> SessionMutationResult:
    session_client = find_session_client(session, client_id)
    if session_client.status != SessionClientStatus.completed:
        session_client.status = SessionClientStatus.working
        session_client.rest_time_remaining = 0
    return SessionMutationResult(session=session, event_type="client_status_updated")


def complete_set(db: Session, session: TrainingSession, client_id: int, command: CompleteSetCommand) -> SessionMutationResult:
    session_client = find_session_client(session, client_id)
    if session_client.status == SessionClientStatus.completed:
        return SessionMutationResult(session=session, event_type="client_status_updated")

    exercises = ordered_program_exercises(session_client)
    if session_client.current_exercise_index >= len(exercises):
        session_client.status = SessionClientStatus.completed
        return SessionMutationResult(session=session, event_type="client_status_updated")

    current = exercises[session_client.current_exercise_index]
    _ensure_expected_set_is_current(session_client, current, command)
    _insert_set_log_if_missing(db, session.id, session_client, current, command)

    if session_client.current_set < current.sets:
        recalculate_client_progress(db, session_client, status_after_active=SessionClientStatus.resting)
        if session_client.status == SessionClientStatus.resting:
            session_client.rest_time_remaining = current.rest_seconds
        event_type = "rest_started"
    else:
        recalculate_client_progress(db, session_client, status_after_active=SessionClientStatus.ready)
        event_type = "set_completed"

    complete_session_if_all_clients_done(session)
    return SessionMutationResult(session=session, event_type=event_type)


def undo_last_set(db: Session, session: TrainingSession, client_id: int) -> SessionMutationResult:
    if session.status == SessionStatus.completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Completed sessions cannot be changed")

    session_client = find_session_client(session, client_id)
    last_log = db.scalar(
        select(WorkoutLog)
        .where(WorkoutLog.session_id == session.id, WorkoutLog.client_id == client_id)
        .order_by(WorkoutLog.created_at.desc(), WorkoutLog.id.desc())
    )
    if not last_log:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No completed set to undo")

    db.delete(last_log)
    db.flush()
    recalculate_client_progress(db, session_client, status_after_active=SessionClientStatus.working)
    return SessionMutationResult(session=session, event_type="set_undone")


def end_session(session: TrainingSession) -> SessionMutationResult:
    session.status = SessionStatus.completed
    session.ended_at = session.ended_at or datetime.now(UTC)
    for item in session.clients:
        item.status = SessionClientStatus.completed
        item.rest_time_remaining = 0
        item.client.last_workout_date = session.ended_at
    return SessionMutationResult(session=session, event_type="session_ended")


def find_session_client(session: TrainingSession, client_id: int) -> SessionClient:
    session_client = next((item for item in session.clients if item.client_id == client_id), None)
    if not session_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session client not found")
    return session_client


def ordered_program_exercises(session_client: SessionClient) -> list[ProgramExercise]:
    return sorted(session_client.program.exercises, key=lambda item: item.order_index)


def recalculate_client_progress(
    db: Session,
    session_client: SessionClient,
    *,
    status_after_active: SessionClientStatus,
) -> None:
    exercises = ordered_program_exercises(session_client)
    logs = _logs_for_session_client(db, session_client.session_id, session_client.client_id)
    counts_by_occurrence = _counts_by_program_exercise(logs)

    completed_exercises: list[int] = []
    next_exercise_index = len(exercises)
    next_set = 1
    all_complete = bool(exercises)

    for index, exercise in enumerate(exercises):
        completed_count = counts_by_occurrence.get(exercise.id, 0)
        if completed_count >= exercise.sets:
            completed_exercises.append(exercise.id)
            continue

        all_complete = False
        next_exercise_index = index
        next_set = completed_count + 1
        break

    session_client.completed_exercises = completed_exercises
    session_client.current_exercise_index = next_exercise_index
    session_client.current_set = next_set
    session_client.rest_time_remaining = 0
    session_client.status = SessionClientStatus.completed if all_complete else status_after_active


def complete_session_if_all_clients_done(session: TrainingSession) -> None:
    if not all(item.status == SessionClientStatus.completed for item in session.clients):
        return
    session.status = SessionStatus.completed
    session.ended_at = datetime.now(UTC)
    for item in session.clients:
        item.client.last_workout_date = session.ended_at


def _ensure_expected_set_is_current(
    session_client: SessionClient,
    current: ProgramExercise,
    command: CompleteSetCommand,
) -> None:
    expected_is_stale = (
        (command.program_exercise_id is not None and command.program_exercise_id != current.id)
        or (command.exercise_id is not None and command.exercise_id != current.exercise_id)
        or (command.set_number is not None and command.set_number != session_client.current_set)
    )
    if expected_is_stale:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session state changed")


def _insert_set_log_if_missing(
    db: Session,
    session_id: int,
    session_client: SessionClient,
    current: ProgramExercise,
    command: CompleteSetCommand,
) -> None:
    existing = db.scalar(
        select(WorkoutLog).where(
            WorkoutLog.session_id == session_id,
            WorkoutLog.client_id == session_client.client_id,
            WorkoutLog.program_exercise_id == current.id,
            WorkoutLog.set_number == session_client.current_set,
        )
    )
    if existing:
        return

    db.add(
        WorkoutLog(
            session_id=session_id,
            client_id=session_client.client_id,
            program_exercise_id=current.id,
            exercise_id=current.exercise_id,
            set_number=session_client.current_set,
            reps_completed=command.reps_completed if command.reps_completed is not None else current.reps,
            weight_kg=command.weight_kg if command.weight_kg is not None else current.weight_kg,
        )
    )
    db.flush()


def _logs_for_session_client(db: Session, session_id: int, client_id: int) -> list[WorkoutLog]:
    return list(
        db.scalars(
            select(WorkoutLog)
            .where(WorkoutLog.session_id == session_id, WorkoutLog.client_id == client_id)
            .order_by(WorkoutLog.created_at, WorkoutLog.id)
        )
    )


def _counts_by_program_exercise(logs: list[WorkoutLog]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for log in logs:
        if log.program_exercise_id is None:
            continue
        counts[log.program_exercise_id] = counts.get(log.program_exercise_id, 0) + 1
    return counts
