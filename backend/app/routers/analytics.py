from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import require_role
from app.database import get_db
from app.models import (
    Client,
    ClientCheckIn,
    Exercise,
    Program,
    SessionClient,
    SessionStatus,
    TrainingSession,
    User,
    UserRole,
    WorkoutLog,
    utc_today,
)
from app.schemas import (
    ClientLoadRead,
    TrainerAnalyticsRead,
    TrainerAttentionClientRead,
    TrainerExerciseLoadRead,
    TrainerFocusRead,
    TrainerReadinessStatusRead,
    TrainerVolumePoint,
    TrainerWeeklyVolumePoint,
)
from app.serializers import check_in_readiness_status, check_in_risk_flags

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _duration_minutes(session: TrainingSession) -> int:
    end = session.ended_at or datetime.now(UTC)
    started_at = session.started_at
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=UTC)
    if end.tzinfo is None:
        end = end.replace(tzinfo=UTC)
    return max(0, int((end - started_at).total_seconds() // 60))


def _planned_sets(item: SessionClient) -> int:
    return sum(exercise.sets for exercise in item.program.exercises)


def _completion_rate(completed: int, planned: int) -> int:
    return round((completed / planned) * 100) if planned else 0


def _week_start(value: datetime) -> str:
    return (value.date() - timedelta(days=value.date().weekday())).isoformat()


def _days_since(value: datetime | None) -> int | None:
    if not value:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return max(0, (datetime.now(UTC).date() - value.date()).days)


@router.get("/trainer", response_model=TrainerAnalyticsRead)
def get_trainer_analytics(
    current_user: Annotated[User, Depends(require_role(UserRole.trainer))],
    db: Annotated[Session, Depends(get_db)],
) -> TrainerAnalyticsRead:
    clients = list(
        db.scalars(
            select(Client)
            .where(Client.trainer_id == current_user.id, Client.active.is_(True))
            .order_by(Client.name)
        )
    )
    sessions = list(
        db.scalars(
            select(TrainingSession)
            .where(TrainingSession.trainer_id == current_user.id)
            .order_by(TrainingSession.started_at)
        )
    )
    session_clients = list(
        db.scalars(
            select(SessionClient)
            .options(
                selectinload(SessionClient.session),
                selectinload(SessionClient.client),
                selectinload(SessionClient.program).selectinload(Program.exercises),
            )
            .join(TrainingSession, TrainingSession.id == SessionClient.session_id)
            .where(TrainingSession.trainer_id == current_user.id)
        )
    )
    workout_logs = list(
        db.scalars(
            select(WorkoutLog)
            .join(TrainingSession, TrainingSession.id == WorkoutLog.session_id)
            .where(TrainingSession.trainer_id == current_user.id)
            .order_by(WorkoutLog.created_at)
        )
    )
    exercise_names = {exercise_id: name for exercise_id, name in db.execute(select(Exercise.id, Exercise.name)).all()}
    today_check_ins = {
        check_in.client_id: check_in
        for check_in in db.scalars(
            select(ClientCheckIn).where(
                ClientCheckIn.client_id.in_([client.id for client in clients] or [0]),
                ClientCheckIn.submitted_on == utc_today(),
            )
        )
    }

    planned_sets_by_client: dict[int, int] = defaultdict(int)
    sessions_by_client: dict[int, set[int]] = defaultdict(set)
    client_names = {client.id: client.name for client in clients}
    last_workout_by_client = {client.id: client.last_workout_date for client in clients}
    planned_sets_by_focus: dict[str, int] = defaultdict(int)
    client_sessions_by_focus: dict[str, int] = defaultdict(int)
    focus_by_session_client: dict[tuple[int, int], str] = {}
    for item in session_clients:
        planned_sets = _planned_sets(item)
        focus = item.program.focus or "Custom"
        planned_sets_by_client[item.client_id] += planned_sets
        sessions_by_client[item.client_id].add(item.session_id)
        client_names[item.client_id] = item.client.name
        last_workout_by_client[item.client_id] = item.client.last_workout_date
        planned_sets_by_focus[focus] += planned_sets
        client_sessions_by_focus[focus] += 1
        focus_by_session_client[(item.session_id, item.client_id)] = focus

    volume_by_day: dict[str, dict[str, float | int]] = defaultdict(lambda: {"volume_kg": 0.0, "sets_completed": 0})
    volume_by_week: dict[str, dict[str, float | int | set[int]]] = defaultdict(
        lambda: {"volume_kg": 0.0, "sets_completed": 0, "sessions": set()}
    )
    sets_by_client: dict[int, int] = defaultdict(int)
    volume_by_client: dict[int, float] = defaultdict(float)
    sets_by_focus: dict[str, int] = defaultdict(int)
    volume_by_focus: dict[str, float] = defaultdict(float)
    exercise_sets: dict[int, int] = defaultdict(int)
    exercise_volume: dict[int, float] = defaultdict(float)
    exercise_clients: dict[int, set[int]] = defaultdict(set)
    total_volume_kg = 0.0
    for log in workout_logs:
        volume_kg = log.reps_completed * log.weight_kg
        focus = focus_by_session_client.get((log.session_id, log.client_id), "Custom")
        total_volume_kg += volume_kg
        sets_by_client[log.client_id] += 1
        volume_by_client[log.client_id] += volume_kg
        sets_by_focus[focus] += 1
        volume_by_focus[focus] += volume_kg
        exercise_sets[log.exercise_id] += 1
        exercise_volume[log.exercise_id] += volume_kg
        exercise_clients[log.exercise_id].add(log.client_id)
        day = log.created_at.date().isoformat()
        volume_by_day[day]["volume_kg"] = float(volume_by_day[day]["volume_kg"]) + volume_kg
        volume_by_day[day]["sets_completed"] = int(volume_by_day[day]["sets_completed"]) + 1
        week = _week_start(log.created_at)
        volume_by_week[week]["volume_kg"] = float(volume_by_week[week]["volume_kg"]) + volume_kg
        volume_by_week[week]["sets_completed"] = int(volume_by_week[week]["sets_completed"]) + 1
        week_sessions = volume_by_week[week]["sessions"]
        if isinstance(week_sessions, set):
            week_sessions.add(log.session_id)

    total_planned_sets = sum(planned_sets_by_client.values())
    total_sets_completed = len(workout_logs)
    completed_sessions = [session for session in sessions if session.status == SessionStatus.completed]
    completed_duration = sum(_duration_minutes(session) for session in completed_sessions)
    readiness_counts: dict[str, int] = {"ready": 0, "caution": 0, "attention": 0, "missing": 0}
    attention_clients: list[TrainerAttentionClientRead] = []
    for client in clients:
        check_in = today_check_ins.get(client.id)
        risk_flags = ["not submitted"]
        readiness_status = "missing"
        if check_in:
            readiness_status = check_in_readiness_status(check_in)
            risk_flags = check_in_risk_flags(check_in)
        readiness_counts[readiness_status] += 1

        completion_rate = _completion_rate(sets_by_client[client.id], planned_sets_by_client[client.id])
        days_since_last_workout = _days_since(client.last_workout_date)
        risk_set = list(risk_flags)
        if planned_sets_by_client[client.id] and completion_rate < 75:
            risk_set.append("low completion")
        if days_since_last_workout is None:
            risk_set.append("no workout history")
        elif days_since_last_workout >= 10:
            risk_set.append("inactive 10+ days")
        risk_set = list(dict.fromkeys(risk_set))
        if readiness_status != "ready" or risk_set:
            attention_clients.append(
                TrainerAttentionClientRead(
                    client_id=client.id,
                    client_name=client.name,
                    readiness_status=readiness_status,  # type: ignore[arg-type]
                    risk_flags=risk_set,
                    completion_rate=completion_rate,
                    last_workout_date=client.last_workout_date,
                    days_since_last_workout=days_since_last_workout,
                )
            )

    return TrainerAnalyticsRead(
        total_sessions=len(sessions),
        completed_sessions=len(completed_sessions),
        active_sessions=sum(1 for session in sessions if session.status == SessionStatus.active),
        total_sets_completed=total_sets_completed,
        total_planned_sets=total_planned_sets,
        total_volume_kg=total_volume_kg,
        completion_rate=_completion_rate(total_sets_completed, total_planned_sets),
        average_sets_per_session=round(total_sets_completed / len(completed_sessions), 1) if completed_sessions else 0,
        average_session_minutes=round(completed_duration / len(completed_sessions)) if completed_sessions else 0,
        volume_by_day=[
            TrainerVolumePoint(
                date=day,
                volume_kg=float(values["volume_kg"]),
                sets_completed=int(values["sets_completed"]),
            )
            for day, values in sorted(volume_by_day.items())
        ],
        weekly_volume=[
            TrainerWeeklyVolumePoint(
                week_start=week,
                volume_kg=float(values["volume_kg"]),
                sets_completed=int(values["sets_completed"]),
                sessions=len(values["sessions"]) if isinstance(values["sessions"], set) else 0,
            )
            for week, values in sorted(volume_by_week.items())
        ],
        focus_mix=[
            TrainerFocusRead(
                focus=focus,
                client_sessions=client_sessions_by_focus[focus],
                sets_completed=sets_by_focus[focus],
                planned_sets=planned_sets_by_focus[focus],
                volume_kg=volume_by_focus[focus],
                completion_rate=_completion_rate(sets_by_focus[focus], planned_sets_by_focus[focus]),
            )
            for focus in sorted(planned_sets_by_focus, key=lambda item: (-volume_by_focus[item], item))
        ],
        top_exercises=[
            TrainerExerciseLoadRead(
                exercise_id=exercise_id,
                exercise_name=exercise_names.get(exercise_id, "Unknown exercise"),
                sets_completed=exercise_sets[exercise_id],
                volume_kg=exercise_volume[exercise_id],
                clients=len(exercise_clients[exercise_id]),
            )
            for exercise_id in sorted(exercise_sets, key=lambda id_: (-exercise_volume[id_], exercise_names.get(id_, "")))[:6]
        ],
        readiness_mix=[
            TrainerReadinessStatusRead(status=status, clients=readiness_counts[status])  # type: ignore[arg-type]
            for status in ["ready", "caution", "attention", "missing"]
        ],
        attention_clients=sorted(
            attention_clients,
            key=lambda item: (
                0 if item.readiness_status == "attention" else 1 if item.readiness_status == "caution" else 2,
                -(item.days_since_last_workout or 0),
                item.client_name,
            ),
        )[:8],
        client_load=[
            ClientLoadRead(
                client_id=client_id,
                client_name=client_names[client_id],
                sessions=len(sessions_by_client[client_id]),
                sets_completed=sets_by_client[client_id],
                planned_sets=planned_sets_by_client[client_id],
                volume_kg=volume_by_client[client_id],
                completion_rate=_completion_rate(sets_by_client[client_id], planned_sets_by_client[client_id]),
                last_workout_date=last_workout_by_client[client_id],
            )
            for client_id in sorted(client_names, key=lambda id_: (-volume_by_client[id_], client_names[id_]))
        ],
    )
