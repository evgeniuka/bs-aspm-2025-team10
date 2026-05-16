import os
from collections.abc import Generator

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-thirty-two-bytes"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.database import Base, SessionLocal, engine, get_db
from app.main import app
from app.models import Client, Exercise, FitnessLevel, Program, ProgramExercise, User, UserRole


def override_get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def seeded_trainer(db: Session) -> User:
    trainer = User(
        email="trainer@example.com",
        password_hash=hash_password("password123"),
        full_name="Test Trainer",
        role=UserRole.trainer,
    )
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    return trainer


@pytest.fixture
def seeded_product(db: Session, seeded_trainer: User) -> dict:
    exercises = [
        Exercise(name="Squat", category="Strength", equipment="Barbell", difficulty="Intermediate", description="Squat"),
        Exercise(name="Row", category="Strength", equipment="Cable", difficulty="Beginner", description="Row"),
        Exercise(name="Plank", category="Core", equipment="Mat", difficulty="Beginner", description="Core hold"),
    ]
    db.add_all(exercises)
    db.flush()
    clients = [
        Client(
            trainer_id=seeded_trainer.id,
            name="Client One",
            age=30,
            fitness_level=FitnessLevel.beginner,
            goals="Get stronger",
        ),
        Client(
            trainer_id=seeded_trainer.id,
            name="Client Two",
            age=32,
            fitness_level=FitnessLevel.intermediate,
            goals="Improve consistency",
        ),
    ]
    db.add_all(clients)
    db.flush()
    programs = []
    for client_item in clients:
        program = Program(trainer_id=seeded_trainer.id, client_id=client_item.id, name=f"{client_item.name} Plan")
        db.add(program)
        db.flush()
        for index, exercise in enumerate(exercises):
            db.add(
                ProgramExercise(
                    program_id=program.id,
                    exercise_id=exercise.id,
                    order_index=index,
                    sets=2,
                    reps=8,
                    weight_kg=20,
                    rest_seconds=30,
                )
            )
        programs.append(program)
    db.commit()
    return {"clients": clients, "programs": programs, "exercises": exercises}
