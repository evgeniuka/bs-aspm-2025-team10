from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Client,
    ClientCheckIn,
    Exercise,
    Program,
    ProgramExercise,
    SessionClient,
    TrainingGroup,
    TrainingSession,
    WorkoutLog,
    utc_today,
)
from app.schemas import (
    ClientAnalyticsRead,
    ClientCheckInRead,
    ClientExerciseBreakdownRead,
    ClientRead,
    ClientReadinessRead,
    ClientSessionSummaryRead,
    ClientVolumePoint,
    ExerciseRead,
    ExerciseSummaryRead,
    ProgramExerciseRead,
    ProgramRead,
    SessionClientRead,
    SessionClientSummaryRead,
    SessionSummaryRead,
    TrainingGroupExerciseRead,
    TrainingGroupRead,
    TrainingSessionRead,
    WorkoutLogRead,
)


def program_to_read(program: Program) -> ProgramRead:
    return ProgramRead(
        id=program.id,
        client_id=program.client_id,
        name=program.name,
        focus=program.focus,
        notes=program.notes,
        is_session_snapshot=program.is_session_snapshot,
        created_at=program.created_at,
        exercises=[
            ProgramExerciseRead(
                id=item.id,
                order_index=item.order_index,
                sets=item.sets,
                reps=item.reps,
                weight_kg=item.weight_kg,
                rest_seconds=item.rest_seconds,
                notes=item.notes,
                exercise=ExerciseRead.model_validate(item.exercise),
            )
            for item in sorted(program.exercises, key=lambda exercise: exercise.order_index)
        ],
    )


def group_to_read(group: TrainingGroup) -> TrainingGroupRead:
    return TrainingGroupRead(
        id=group.id,
        name=group.name,
        focus=group.focus,
        notes=group.notes,
        active=group.active,
        created_at=group.created_at,
        updated_at=group.updated_at,
        clients=[ClientRead.model_validate(member.client) for member in sorted(group.members, key=lambda item: item.order_index)],
        exercises=[
            TrainingGroupExerciseRead(
                id=item.id,
                order_index=item.order_index,
                sets=item.sets,
                reps=item.reps,
                weight_kg=item.weight_kg,
                rest_seconds=item.rest_seconds,
                notes=item.notes,
                exercise=ExerciseRead.model_validate(item.exercise),
            )
            for item in sorted(group.exercises, key=lambda exercise: exercise.order_index)
        ],
    )


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


def check_in_risk_flags(check_in: ClientCheckIn) -> list[str]:
    flags: list[str] = []
    if check_in.energy_level <= 2:
        flags.append("low energy")
    if check_in.sleep_quality <= 2:
        flags.append("poor sleep")
    if check_in.soreness_level >= 4:
        flags.append("high soreness")
    if check_in.pain_notes:
        flags.append("pain noted")
    return flags


def check_in_readiness_status(check_in: ClientCheckIn) -> str:
    flags = check_in_risk_flags(check_in)
    if flags:
        return "attention"
    if check_in.energy_level == 3 or check_in.sleep_quality == 3 or check_in.soreness_level == 3:
        return "caution"
    return "ready"


def check_in_to_read(check_in: ClientCheckIn) -> ClientCheckInRead:
    return ClientCheckInRead(
        id=check_in.id,
        client_id=check_in.client_id,
        submitted_on=check_in.submitted_on,
        energy_level=check_in.energy_level,
        sleep_quality=check_in.sleep_quality,
        soreness_level=check_in.soreness_level,
        pain_notes=check_in.pain_notes,
        training_goal=check_in.training_goal,
        readiness_status=check_in_readiness_status(check_in),
        risk_flags=check_in_risk_flags(check_in),
        created_at=check_in.created_at,
        updated_at=check_in.updated_at,
    )


def today_check_ins_by_client_id(db: Session, client_ids: list[int]) -> dict[int, ClientCheckIn]:
    if not client_ids:
        return {}
    return {
        check_in.client_id: check_in
        for check_in in db.scalars(
            select(ClientCheckIn).where(
                ClientCheckIn.client_id.in_(client_ids),
                ClientCheckIn.submitted_on == utc_today(),
            )
        )
    }


def client_readiness_to_read(client: Client, check_in: ClientCheckIn | None) -> ClientReadinessRead:
    if not check_in:
        return ClientReadinessRead(
            client=ClientRead.model_validate(client),
            check_in=None,
            readiness_status="missing",
            risk_flags=["not submitted"],
        )
    check_in_read = check_in_to_read(check_in)
    return ClientReadinessRead(
        client=ClientRead.model_validate(client),
        check_in=check_in_read,
        readiness_status=check_in_read.readiness_status,
        risk_flags=check_in_read.risk_flags,
    )


def _workout_log_rows(db: Session, session_id: int, client_id: int) -> list[tuple[WorkoutLog, str]]:
    return [
        (log, exercise_name)
        for log, exercise_name in db.execute(
            select(WorkoutLog, Exercise.name)
            .join(Exercise, Exercise.id == WorkoutLog.exercise_id)
            .where(WorkoutLog.session_id == session_id, WorkoutLog.client_id == client_id)
            .order_by(WorkoutLog.program_exercise_id, WorkoutLog.exercise_id, WorkoutLog.set_number, WorkoutLog.created_at)
        )
    ]


def _workout_logs_to_read(rows: list[tuple[WorkoutLog, str]]) -> list[WorkoutLogRead]:
    return [
        WorkoutLogRead(
            program_exercise_id=log.program_exercise_id,
            exercise_id=log.exercise_id,
            exercise_name=exercise_name,
            set_number=log.set_number,
            reps_completed=log.reps_completed,
            weight_kg=log.weight_kg,
            volume_kg=log.reps_completed * log.weight_kg,
            created_at=log.created_at,
        )
        for log, exercise_name in rows
    ]


def _log_matches_program_exercise(log: WorkoutLog, planned: ProgramExercise) -> bool:
    if log.program_exercise_id is not None:
        return log.program_exercise_id == planned.id
    return log.exercise_id == planned.exercise_id


def _exercise_summaries(item: SessionClient, rows: list[tuple[WorkoutLog, str]]) -> list[ExerciseSummaryRead]:
    summaries: list[ExerciseSummaryRead] = []
    for planned in sorted(item.program.exercises, key=lambda exercise: exercise.order_index):
        planned_rows = [(log, exercise_name) for log, exercise_name in rows if _log_matches_program_exercise(log, planned)]
        summaries.append(
            ExerciseSummaryRead(
                exercise_id=planned.exercise_id,
                exercise_name=planned.exercise.name,
                sets_completed=len(planned_rows),
                planned_sets=planned.sets,
                reps_completed=sum(log.reps_completed for log, _ in planned_rows),
                volume_kg=sum(log.reps_completed * log.weight_kg for log, _ in planned_rows),
                sets=_workout_logs_to_read(planned_rows),
            )
        )
    return summaries


def session_client_to_read(db: Session, item: SessionClient) -> SessionClientRead:
    rows = _workout_log_rows(db, item.session_id, item.client_id)
    check_in = today_check_ins_by_client_id(db, [item.client_id]).get(item.client_id)
    return SessionClientRead(
        id=item.id,
        client_id=item.client_id,
        client_name=item.client.name,
        program=program_to_read(item.program),
        current_exercise_index=item.current_exercise_index,
        current_set=item.current_set,
        status=item.status,
        completed_exercises=item.completed_exercises or [],
        rest_time_remaining=item.rest_time_remaining,
        coach_notes=item.coach_notes,
        next_focus=item.next_focus,
        today_check_in=check_in_to_read(check_in) if check_in else None,
        sets_completed=_workout_logs_to_read(rows),
    )


def session_to_read(db: Session, session: TrainingSession) -> TrainingSessionRead:
    return TrainingSessionRead(
        id=session.id,
        status=session.status,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_minutes=_duration_minutes(session),
        clients=[session_client_to_read(db, item) for item in session.clients],
    )


def session_client_summary_to_read(db: Session, item: SessionClient) -> SessionClientSummaryRead:
    rows = _workout_log_rows(db, item.session_id, item.client_id)
    volume_kg = sum(log.reps_completed * log.weight_kg for log, _ in rows)
    return SessionClientSummaryRead(
        session_client_id=item.id,
        client_id=item.client_id,
        client_name=item.client.name,
        program_id=item.program_id,
        program_name=item.program.name,
        status=item.status,
        sets_completed=len(rows),
        planned_sets=_planned_sets(item),
        volume_kg=volume_kg,
        coach_notes=item.coach_notes,
        next_focus=item.next_focus,
        exercises=_exercise_summaries(item, rows),
    )


def session_summary_to_read(db: Session, session: TrainingSession) -> SessionSummaryRead:
    clients = [session_client_summary_to_read(db, item) for item in session.clients]
    return SessionSummaryRead(
        session_id=session.id,
        status=session.status,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_minutes=_duration_minutes(session),
        total_clients=len(clients),
        total_sets_completed=sum(item.sets_completed for item in clients),
        total_planned_sets=sum(item.planned_sets for item in clients),
        total_volume_kg=sum(item.volume_kg for item in clients),
        clients=clients,
    )


def client_session_summary_to_read(db: Session, item: SessionClient) -> ClientSessionSummaryRead:
    rows = _workout_log_rows(db, item.session_id, item.client_id)
    return ClientSessionSummaryRead(
        session_id=item.session_id,
        status=item.session.status,
        started_at=item.session.started_at,
        ended_at=item.session.ended_at,
        duration_minutes=_duration_minutes(item.session),
        program_name=item.program.name,
        sets_completed=len(rows),
        planned_sets=_planned_sets(item),
        volume_kg=sum(log.reps_completed * log.weight_kg for log, _ in rows),
        coach_notes=item.coach_notes,
        next_focus=item.next_focus,
    )


def client_analytics_to_read(db: Session, session_clients: list[SessionClient]) -> ClientAnalyticsRead:
    session_summaries = [client_session_summary_to_read(db, item) for item in session_clients]
    total_sessions = len(session_summaries)
    total_duration = sum(item.duration_minutes for item in session_summaries)
    total_sets = sum(item.sets_completed for item in session_summaries)
    planned_sets = sum(item.planned_sets for item in session_summaries)
    total_volume_kg = sum(item.volume_kg for item in session_summaries)
    exercise_breakdown: dict[int, dict[str, object]] = {}
    for item in session_clients:
        for log, exercise_name in _workout_log_rows(db, item.session_id, item.client_id):
            current = exercise_breakdown.setdefault(
                log.exercise_id,
                {
                    "exercise_name": exercise_name,
                    "sets_completed": 0,
                    "volume_kg": 0.0,
                    "last_logged_at": None,
                },
            )
            current["sets_completed"] = int(current["sets_completed"]) + 1
            current["volume_kg"] = float(current["volume_kg"]) + log.reps_completed * log.weight_kg
            last_logged_at = current["last_logged_at"]
            if last_logged_at is None or log.created_at > last_logged_at:
                current["last_logged_at"] = log.created_at

    return ClientAnalyticsRead(
        total_sessions=total_sessions,
        completed_sessions=sum(1 for item in session_summaries if item.status == "completed"),
        total_sets=total_sets,
        planned_sets=planned_sets,
        total_volume_kg=total_volume_kg,
        average_volume_kg=round(total_volume_kg / total_sessions, 1) if total_sessions else 0,
        best_volume_kg=max((item.volume_kg for item in session_summaries), default=0),
        completion_rate=round((total_sets / planned_sets) * 100) if planned_sets else 0,
        average_session_minutes=round(total_duration / total_sessions) if total_sessions else 0,
        volume_by_session=[
            ClientVolumePoint(
                session_id=item.session_id,
                date=item.ended_at or item.started_at,
                volume_kg=item.volume_kg,
                sets_completed=item.sets_completed,
            )
            for item in sorted(session_summaries, key=lambda summary: summary.started_at)
        ],
        exercise_breakdown=[
            ClientExerciseBreakdownRead(
                exercise_id=exercise_id,
                exercise_name=str(values["exercise_name"]),
                sets_completed=int(values["sets_completed"]),
                volume_kg=float(values["volume_kg"]),
                last_logged_at=values["last_logged_at"],
            )
            for exercise_id, values in sorted(
                exercise_breakdown.items(),
                key=lambda entry: (-float(entry[1]["volume_kg"]), str(entry[1]["exercise_name"])),
            )
        ],
    )
