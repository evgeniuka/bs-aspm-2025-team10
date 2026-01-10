import os
import sys
from pathlib import Path

import pytest

# --- Make backend imports work ---
BACKEND_ROOT = Path(__file__).resolve().parents[2]  # .../backend
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# --- Require DB URL for tests ---
DATABASE_URL_TEST = os.getenv("DATABASE_URL_TEST")
if not DATABASE_URL_TEST:
    if os.getenv("CI"):
        raise RuntimeError("DATABASE_URL_TEST is not set in CI. Set it in the GitHub Actions workflow env.")
    pytest.skip("DATABASE_URL_TEST not set; skipping FC-4 tests.", allow_module_level=True)

# IMPORTANT: set env BEFORE importing app/config (config may read env at import time)
os.environ["DATABASE_URL"] = DATABASE_URL_TEST

# Provide defaults so create_app won't crash if these are required
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")

from app import create_app  # noqa: E402
from models import db  # noqa: E402
from models.client import Client  # noqa: E402
from models.exercise import Exercise  # noqa: E402
from models.program import Program, ProgramExercise  # noqa: E402
from models.user import User  # noqa: E402
from utils.jwt_utils import generate_token  # noqa: E402


@pytest.fixture()
def app():
    app, _ = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def create_user(email: str, role: str = "trainer") -> User:
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


def create_client_record(trainer_id: int) -> Client:
    client_obj = Client(
        trainer_id=trainer_id,
        name="Test Client",
        age=30,
        fitness_level="Beginner",
        goals="Build strength",
        active=True,
    )
    db.session.add(client_obj)
    db.session.commit()
    return client_obj


def create_exercises(count: int = 5):
    exercises = []
    for idx in range(count):
        ex = Exercise(
            name=f"Exercise {idx}",
            category="upper_body",
            description="Test description",
            equipment="bodyweight",
            difficulty="beginner",
        )
        db.session.add(ex)
        exercises.append(ex)
    db.session.commit()
    return exercises


def make_program_payload(client_id: int, exercises):
    return {
        "name": "Strength Builder",
        "client_id": client_id,
        "notes": "Focus on form",
        "exercises": [
            {
                "exercise_id": ex.id,
                "sets": 3,
                "reps": 10,
                "weight_kg": 20,
                "rest_seconds": 60,
                "notes": "Keep steady pace",
            }
            for ex in exercises
        ],
    }


def _json(response):
    assert response.is_json, f"Expected JSON response, got Content-Type: {response.content_type}"
    return response.get_json()


def _details_text(data) -> str:
    # details may be list[str], list[dict], dict, str, etc.
    details = data.get("details")
    if details is None:
        return ""
    if isinstance(details, str):
        return details
    if isinstance(details, dict):
        return " ".join([f"{k}:{v}" for k, v in details.items()])
    if isinstance(details, list):
        parts = []
        for item in details:
            parts.append(str(item))
        return " ".join(parts)
    return str(details)


def test_create_program_success(client, app):
    with app.app_context():
        trainer = create_user("trainer@example.com")
        client_record = create_client_record(trainer.id)
        exercises = create_exercises(5)
        token = generate_token(trainer.id, trainer.role)

    payload = make_program_payload(client_record.id, exercises)
    resp = client.post(
        "/api/programs",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201
    data = _json(resp)

    # be tolerant to response shape but still meaningful
    assert "program_id" in data or "id" in data
    program_id = data.get("program_id", data.get("id"))
    assert isinstance(program_id, int)

    with app.app_context():
        program = Program.query.get(program_id)
        assert program is not None
        assert program.client_id == client_record.id
        assert ProgramExercise.query.filter_by(program_id=program.id).count() == 5


def test_create_program_validation_missing_fields(client, app):
    with app.app_context():
        trainer = create_user("trainer2@example.com")
        token = generate_token(trainer.id, trainer.role)

    resp = client.post(
        "/api/programs",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 400
    data = _json(resp)

    # check error-ish fields exist
    assert any(k in data for k in ("error", "message"))
    text = (data.get("error") or data.get("message") or "") + " " + _details_text(data)
    # optional: ensure it's about validation
    assert "valid" in text.lower() or "require" in text.lower() or "must" in text.lower()


def test_create_program_validation_invalid_format(client, app):
    with app.app_context():
        trainer = create_user("trainer3@example.com")
        client_record = create_client_record(trainer.id)
        exercises = create_exercises(5)
        token = generate_token(trainer.id, trainer.role)

    payload = make_program_payload(client_record.id, exercises)
    payload["exercises"][0]["sets"] = 0
    payload["exercises"][0]["reps"] = 0
    payload["exercises"][0]["weight_kg"] = 600
    payload["exercises"][0]["rest_seconds"] = 1000

    resp = client.post(
        "/api/programs",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 400
    data = _json(resp)

    text = (data.get("error") or data.get("message") or "") + " " + _details_text(data)
    # at least mentions one of the invalid fields
    lowered = text.lower()
    assert any(x in lowered for x in ("sets", "reps", "weight", "rest"))


def test_create_program_requires_auth(client):
    resp = client.post("/api/programs", json={})

    assert resp.status_code == 401
    data = _json(resp)
    # tolerant to different auth error messages
    msg = (data.get("error") or data.get("message") or "").lower()
    assert any(x in msg for x in ("token", "auth", "authorization", "missing"))


def test_create_program_client_not_owned(client, app):
    with app.app_context():
        trainer = create_user("trainer4@example.com")
        other_trainer = create_user("trainer5@example.com")
        client_record = create_client_record(other_trainer.id)
        exercises = create_exercises(5)
        token = generate_token(trainer.id, trainer.role)

    payload = make_program_payload(client_record.id, exercises)
    resp = client.post(
        "/api/programs",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code in (403, 404)
    data = _json(resp)
    msg = (data.get("error") or data.get("message") or "").lower()
    assert "client" in msg or "not found" in msg or "owned" in msg
