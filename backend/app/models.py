from datetime import UTC, date, datetime
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_today() -> date:
    return datetime.now(UTC).date()


class UserRole(StrEnum):
    trainer = "trainer"
    trainee = "trainee"


class FitnessLevel(StrEnum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"


class SessionStatus(StrEnum):
    active = "active"
    completed = "completed"


class SessionClientStatus(StrEnum):
    ready = "ready"
    working = "working"
    resting = "resting"
    completed = "completed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    trained_clients: Mapped[list["Client"]] = relationship(
        foreign_keys="Client.trainer_id",
        back_populates="trainer",
    )


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    fitness_level: Mapped[FitnessLevel] = mapped_column(Enum(FitnessLevel), nullable=False)
    goals: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_workout_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    trainer: Mapped[User] = relationship(foreign_keys=[trainer_id], back_populates="trained_clients")
    user: Mapped[User | None] = relationship(foreign_keys=[user_id])
    programs: Mapped[list["Program"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    check_ins: Mapped[list["ClientCheckIn"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class ClientCheckIn(Base):
    __tablename__ = "client_check_ins"
    __table_args__ = (UniqueConstraint("client_id", "submitted_on", name="uq_client_check_in_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    submitted_on: Mapped[date] = mapped_column(Date, default=utc_today, nullable=False)
    energy_level: Mapped[int] = mapped_column(Integer, nullable=False)
    sleep_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    soreness_level: Mapped[int] = mapped_column(Integer, nullable=False)
    pain_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    training_goal: Mapped[str | None] = mapped_column(String(220), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    client: Mapped[Client] = relationship(back_populates="check_ins")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    equipment: Mapped[str] = mapped_column(String(120), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(primary_key=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    focus: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_session_snapshot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    client: Mapped[Client] = relationship(back_populates="programs")
    exercises: Mapped[list["ProgramExercise"]] = relationship(
        back_populates="program",
        cascade="all, delete-orphan",
        order_by="ProgramExercise.order_index",
    )


class ProgramExercise(Base):
    __tablename__ = "program_exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    sets: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    rest_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    program: Mapped[Program] = relationship(back_populates="exercises")
    exercise: Mapped[Exercise] = relationship()


class TrainingGroup(Base):
    __tablename__ = "training_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    focus: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    trainer: Mapped[User] = relationship()
    members: Mapped[list["TrainingGroupMember"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        order_by="TrainingGroupMember.order_index",
    )
    exercises: Mapped[list["TrainingGroupExercise"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        order_by="TrainingGroupExercise.order_index",
    )


class TrainingGroupMember(Base):
    __tablename__ = "training_group_members"
    __table_args__ = (UniqueConstraint("group_id", "client_id", name="uq_training_group_client"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("training_groups.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    group: Mapped[TrainingGroup] = relationship(back_populates="members")
    client: Mapped[Client] = relationship()


class TrainingGroupExercise(Base):
    __tablename__ = "training_group_exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("training_groups.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    sets: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    rest_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    group: Mapped[TrainingGroup] = relationship(back_populates="exercises")
    exercise: Mapped[Exercise] = relationship()


class TrainingSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.active, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    trainer: Mapped[User] = relationship()
    clients: Mapped[list["SessionClient"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionClient.id",
    )


class SessionClient(Base):
    __tablename__ = "session_clients"
    __table_args__ = (UniqueConstraint("session_id", "client_id", name="uq_session_client"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), nullable=False)
    current_exercise_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_set: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[SessionClientStatus] = mapped_column(
        Enum(SessionClientStatus),
        default=SessionClientStatus.ready,
        nullable=False,
    )
    completed_exercises: Mapped[list[int]] = mapped_column(MutableList.as_mutable(JSON), default=list, nullable=False)
    rest_time_remaining: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coach_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_focus: Mapped[str | None] = mapped_column(String(180), nullable=True)

    session: Mapped[TrainingSession] = relationship(back_populates="clients")
    client: Mapped[Client] = relationship()
    program: Mapped[Program] = relationship()


class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    __table_args__ = (
        UniqueConstraint("session_id", "client_id", "program_exercise_id", "set_number", name="uq_workout_program_set"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    program_exercise_id: Mapped[int | None] = mapped_column(ForeignKey("program_exercises.id"), nullable=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reps_completed: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    program_exercise: Mapped[ProgramExercise | None] = relationship()
