from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models import FitnessLevel, SessionClientStatus, SessionStatus, UserRole

MAX_SESSION_CLIENTS = 10


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: UserRole


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)


class AuthResponse(BaseModel):
    user: UserRead


class ClientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    age: int = Field(ge=13, le=100)
    fitness_level: FitnessLevel
    goals: str = Field(min_length=8, max_length=500)


class ClientUpdate(ClientCreate):
    pass


class ClientRead(ClientCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    last_workout_date: datetime | None = None
    created_at: datetime


class ClientCheckInUpsert(BaseModel):
    energy_level: int = Field(ge=1, le=5)
    sleep_quality: int = Field(ge=1, le=5)
    soreness_level: int = Field(ge=0, le=5)
    pain_notes: str | None = Field(default=None, max_length=500)
    training_goal: str | None = Field(default=None, max_length=220)


class ClientCheckInRead(BaseModel):
    id: int
    client_id: int
    submitted_on: date
    energy_level: int
    sleep_quality: int
    soreness_level: int
    pain_notes: str | None = None
    training_goal: str | None = None
    readiness_status: Literal["ready", "caution", "attention"]
    risk_flags: list[str]
    created_at: datetime
    updated_at: datetime


class ClientReadinessRead(BaseModel):
    client: ClientRead
    check_in: ClientCheckInRead | None = None
    readiness_status: Literal["ready", "caution", "attention", "missing"]
    risk_flags: list[str]


class ExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    equipment: str
    difficulty: str
    description: str


class ProgramExerciseCreate(BaseModel):
    exercise_id: int
    sets: int = Field(ge=1, le=10)
    reps: int = Field(ge=1, le=50)
    weight_kg: float = Field(ge=0, le=500)
    rest_seconds: int = Field(ge=0, le=600)
    notes: str | None = None


class ProgramCreate(BaseModel):
    client_id: int
    name: str = Field(min_length=3, max_length=120)
    focus: str | None = Field(default=None, max_length=80)
    notes: str | None = None
    exercises: list[ProgramExerciseCreate] = Field(min_length=3, max_length=20)


class ProgramUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    focus: str | None = Field(default=None, max_length=80)
    notes: str | None = None
    exercises: list[ProgramExerciseCreate] = Field(min_length=3, max_length=20)


class ProgramExerciseRead(BaseModel):
    id: int
    order_index: int
    sets: int
    reps: int
    weight_kg: float
    rest_seconds: int
    notes: str | None
    exercise: ExerciseRead


class ProgramRead(BaseModel):
    id: int
    client_id: int
    name: str
    focus: str | None
    notes: str | None
    is_session_snapshot: bool
    created_at: datetime
    exercises: list[ProgramExerciseRead]


class TrainingGroupExerciseRead(BaseModel):
    id: int
    order_index: int
    sets: int
    reps: int
    weight_kg: float
    rest_seconds: int
    notes: str | None = None
    exercise: ExerciseRead


class TrainingGroupCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    focus: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=1000)
    client_ids: list[int] = Field(min_length=1, max_length=MAX_SESSION_CLIENTS)
    exercises: list[ProgramExerciseCreate] = Field(min_length=3, max_length=20)


class TrainingGroupUpdate(TrainingGroupCreate):
    pass


class TrainingGroupRead(BaseModel):
    id: int
    name: str
    focus: str | None
    notes: str | None
    active: bool
    created_at: datetime
    updated_at: datetime
    clients: list[ClientRead]
    exercises: list[TrainingGroupExerciseRead]


class TrainingGroupSessionClient(BaseModel):
    client_id: int
    program_id: int | None = None


class TrainingGroupSessionCreate(BaseModel):
    clients: list[TrainingGroupSessionClient] | None = Field(default=None, min_length=1, max_length=MAX_SESSION_CLIENTS)


class SessionCreate(BaseModel):
    client_ids: list[int] = Field(min_length=1, max_length=MAX_SESSION_CLIENTS)
    program_ids: list[int] = Field(min_length=1, max_length=MAX_SESSION_CLIENTS)


class CompleteSetRequest(BaseModel):
    program_exercise_id: int | None = None
    exercise_id: int | None = None
    set_number: int | None = Field(default=None, ge=1, le=100)
    reps_completed: int | None = Field(default=None, ge=0, le=100)
    weight_kg: float | None = Field(default=None, ge=0, le=500)


class WorkoutLogRead(BaseModel):
    program_exercise_id: int | None = None
    exercise_id: int
    exercise_name: str
    set_number: int
    reps_completed: int
    weight_kg: float
    volume_kg: float
    created_at: datetime


class SessionClientRead(BaseModel):
    id: int
    client_id: int
    client_name: str
    program: ProgramRead
    current_exercise_index: int
    current_set: int
    status: SessionClientStatus
    completed_exercises: list[int]
    rest_time_remaining: int
    coach_notes: str | None = None
    next_focus: str | None = None
    today_check_in: ClientCheckInRead | None = None
    sets_completed: list[WorkoutLogRead]


class TrainingSessionRead(BaseModel):
    id: int
    status: SessionStatus
    started_at: datetime
    ended_at: datetime | None
    duration_minutes: int
    clients: list[SessionClientRead]


class SessionCreated(BaseModel):
    session_id: int
    session: TrainingSessionRead


class DashboardOverview(BaseModel):
    total_clients: int
    total_programs: int
    completed_sessions: int
    active_session: TrainingSessionRead | None
    clients: list[ClientRead]
    recent_sessions: list[TrainingSessionRead]
    today_readiness: list[ClientReadinessRead]


class TrainerVolumePoint(BaseModel):
    date: str
    volume_kg: float
    sets_completed: int


class TrainerWeeklyVolumePoint(BaseModel):
    week_start: str
    volume_kg: float
    sets_completed: int
    sessions: int


class TrainerFocusRead(BaseModel):
    focus: str
    client_sessions: int
    sets_completed: int
    planned_sets: int
    volume_kg: float
    completion_rate: int


class TrainerExerciseLoadRead(BaseModel):
    exercise_id: int
    exercise_name: str
    sets_completed: int
    volume_kg: float
    clients: int


class TrainerReadinessStatusRead(BaseModel):
    status: Literal["ready", "caution", "attention", "missing"]
    clients: int


class TrainerAttentionClientRead(BaseModel):
    client_id: int
    client_name: str
    readiness_status: Literal["ready", "caution", "attention", "missing"]
    risk_flags: list[str]
    completion_rate: int
    last_workout_date: datetime | None = None
    days_since_last_workout: int | None = None


class ClientLoadRead(BaseModel):
    client_id: int
    client_name: str
    sessions: int
    sets_completed: int
    planned_sets: int
    volume_kg: float
    completion_rate: int
    last_workout_date: datetime | None = None


class TrainerAnalyticsRead(BaseModel):
    total_sessions: int
    completed_sessions: int
    active_sessions: int
    total_sets_completed: int
    total_planned_sets: int
    total_volume_kg: float
    completion_rate: int
    average_sets_per_session: float
    average_session_minutes: int
    volume_by_day: list[TrainerVolumePoint]
    weekly_volume: list[TrainerWeeklyVolumePoint]
    focus_mix: list[TrainerFocusRead]
    top_exercises: list[TrainerExerciseLoadRead]
    readiness_mix: list[TrainerReadinessStatusRead]
    attention_clients: list[TrainerAttentionClientRead]
    client_load: list[ClientLoadRead]


class ClientVolumePoint(BaseModel):
    session_id: int
    date: datetime
    volume_kg: float
    sets_completed: int


class ClientExerciseBreakdownRead(BaseModel):
    exercise_id: int
    exercise_name: str
    sets_completed: int
    volume_kg: float
    last_logged_at: datetime | None = None


class ClientAnalyticsRead(BaseModel):
    total_sessions: int
    completed_sessions: int
    total_sets: int
    planned_sets: int
    total_volume_kg: float
    average_volume_kg: float
    best_volume_kg: float
    completion_rate: int
    average_session_minutes: int
    volume_by_session: list[ClientVolumePoint]
    exercise_breakdown: list[ClientExerciseBreakdownRead]


class ClientSessionSummaryRead(BaseModel):
    session_id: int
    status: SessionStatus
    started_at: datetime
    ended_at: datetime | None
    duration_minutes: int
    program_name: str
    sets_completed: int
    planned_sets: int
    volume_kg: float
    coach_notes: str | None = None
    next_focus: str | None = None


class ClientDetailRead(BaseModel):
    client: ClientRead
    programs: list[ProgramRead]
    analytics: ClientAnalyticsRead
    recent_sessions: list[ClientSessionSummaryRead]
    today_check_in: ClientCheckInRead | None = None


class ExerciseSummaryRead(BaseModel):
    exercise_id: int
    exercise_name: str
    sets_completed: int
    planned_sets: int
    reps_completed: int
    volume_kg: float
    sets: list[WorkoutLogRead]


class SessionClientSummaryRead(BaseModel):
    session_client_id: int
    client_id: int
    client_name: str
    program_id: int
    program_name: str
    status: SessionClientStatus
    sets_completed: int
    planned_sets: int
    volume_kg: float
    coach_notes: str | None = None
    next_focus: str | None = None
    exercises: list[ExerciseSummaryRead]


class SessionSummaryRead(BaseModel):
    session_id: int
    status: SessionStatus
    started_at: datetime
    ended_at: datetime | None
    duration_minutes: int
    total_clients: int
    total_sets_completed: int
    total_planned_sets: int
    total_volume_kg: float
    clients: list[SessionClientSummaryRead]


class SessionClientSummaryUpdate(BaseModel):
    coach_notes: str | None = Field(default=None, max_length=1000)
    next_focus: str | None = Field(default=None, max_length=180)


class RealtimeEvent(BaseModel):
    type: Literal[
        "session_joined",
        "set_completed",
        "rest_started",
        "client_status_updated",
        "session_ended",
        "set_undone",
    ]
    session: TrainingSessionRead
