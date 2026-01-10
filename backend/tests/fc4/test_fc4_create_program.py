import os
import sys
from pathlib import Path

import pytest

if not os.getenv("DATABASE_URL_TEST"):
    pytest.skip("DATABASE_URL_TEST not set; skipping FC-4 tests.", allow_module_level=True)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app
from models import db
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from models.user import User
from utils.jwt_utils import generate_token


@pytest.fixture()
def app():
    os.environ["DATABASE_URL"] = os.environ["DATABASE_URL_TEST"]
    app, _ = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def create_user(email, role="trainer"):
    user = User(
        email=email,
        full_name="Test User",
        role=role,
        is_active=True,
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def create_client(trainer_id):
    client = Client(
        trainer_id=trainer_id,
        name="Test Client",
        age=30,
        fitness_level="Beginner",
        goals="Build strength",
        active=True,
    )
    db.session.add(client)
    db.session.commit()
    return client


def create_exercises(count=5):
    exercises = []
    for idx in range(count):
        exercise = Exercise(
            name=f"Exercise {idx}",
            category="upper_body",
            description="Test description",
            equipment="bodyweight",
            difficulty="beginner",
        )
        db.session.add(exercise)
        exercises.append(exercise)
    db.session.commit()
    return exercises


def make_program_payload(client_id, exercises):
    return {
        "name": "Strength Builder",
        "client_id": client_id,
        "notes": "Focus on form",
        "exercises": [
            {
                "exercise_id": exercise.id,
                "sets": 3,
                "reps": 10,
                "weight_kg": 20,
                "rest_seconds": 60,
                "notes": "Keep steady pace",
            }
            for exercise in exercises
        ],
    }


def test_create_program_success(client, app):
    with app.app_context():
        trainer = create_user("trainer@example.com")
        client_record = create_client(trainer.id)
        exercises = create_exercises(5)
        token = generate_token(trainer.id, trainer.role)

    payload = make_program_payload(client_record.id, exercises)
    response = client.post(
        "/api/programs",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Program created"
    assert isinstance(data["program_id"], int)

    with app.app_context():
        program = Program.query.get(data["program_id"])
        assert program is not None
        assert program.client_id == client_record.id
        assert ProgramExercise.query.filter_by(program_id=program.id).count() == 5


def test_create_program_validation_missing_fields(client, app):
    with app.app_context():
        trainer = create_user("trainer2@example.com")
        token = generate_token(trainer.id, trainer.role)

    response = client.post(
        "/api/programs",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation failed"
    assert "Program name must be 3-100 characters" in data["details"]
    assert "Client is required" in data["details"]
    assert "At least 5 exercises are required" in data["details"]


def test_create_program_validation_invalid_format(client, app):
    with app.app_context():
        trainer = create_user("trainer3@example.com")
        client_record = create_client(trainer.id)
        exercises = create_exercises(5)
        token = generate_token(trainer.id, trainer.role)

    payload = make_program_payload(client_record.id, exercises)
    payload["exercises"][0]["sets"] = 0
    payload["exercises"][0]["reps"] = 0
    payload["exercises"][0]["weight_kg"] = 600
    payload["exercises"][0]["rest_seconds"] = 1000

    response = client.post(
        "/api/programs",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation failed"
    assert any("Sets must be between 1-10" in detail for detail in data["details"])
    assert any("Reps must be between 1-50" in detail for detail in data["details"])
    assert any("Weight must be between 0-500" in detail for detail in data["details"])
    assert any("Rest must be between 0-600" in detail for detail in data["details"])


def test_create_program_requires_auth(client):
    response = client.post("/api/programs", json={})

    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Token is missing"


def test_create_program_client_not_owned(client, app):
    with app.app_context():
        trainer = create_user("trainer4@example.com")
        other_trainer = create_user("trainer5@example.com")
        client_record = create_client(other_trainer.id)
        exercises = create_exercises(5)
        token = generate_token(trainer.id, trainer.role)

    payload = make_program_payload(client_record.id, exercises)
    response = client.post(
        "/api/programs",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Client not found or not owned by trainer"
