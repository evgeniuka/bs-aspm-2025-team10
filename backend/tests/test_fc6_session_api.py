import pytest

from models import db
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from models.session import Session


def seed_clients_programs(app, trainer_id, client_count=2):
    with app.app_context():
        exercise = Exercise(
            name="Squat",
            category="lower_body",
            description="Barbell back squat",
            equipment="barbell",
            difficulty="intermediate",
        )
        db.session.add(exercise)
        db.session.flush()

        clients = []
        programs = []
        for idx in range(client_count):
            client = Client(
                trainer_id=trainer_id,
                user_id=None,
                name=f"Client {idx + 1}",
                age=25 + idx,
                fitness_level="Beginner",
                goals="Strength",
            )
            db.session.add(client)
            db.session.flush()

            program = Program(
                trainer_id=trainer_id,
                client_id=client.id,
                name=f"Program {idx + 1}",
                notes=None,
            )
            db.session.add(program)
            db.session.flush()

            program_exercise = ProgramExercise(
                program_id=program.id,
                exercise_id=exercise.id,
                order=1,
                sets=3,
                reps=8,
                weight_kg=60.0,
                rest_seconds=90,
                notes=None,
            )
            db.session.add(program_exercise)
            clients.append(client)
            programs.append(program)

        db.session.commit()

        return {
            "client_ids": [client.id for client in clients],
            "program_ids": [program.id for program in programs],
        }


def test_end_session_updates_db(client, app, trainer_token):
    payload = seed_clients_programs(app, trainer_token["user_id"], client_count=2)
    create_response = client.post(
        "/api/sessions",
        json=payload,
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )
    session_id = create_response.get_json()["session_id"]

    response = client.post(
        f"/api/sessions/{session_id}/end",
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Session ended successfully"

    with app.app_context():
        session = db.session.get(Session, session_id)
        assert session.status == "completed"
        assert session.end_time is not None


@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("get", "/api/sessions/1"),
        ("post", "/api/sessions/1/end"),
    ],
)
def test_session_endpoints_require_auth(client, method, endpoint):
    response = getattr(client, method)(endpoint, json={})
    assert response.status_code == 401
    assert response.get_json()["error"] == "Token is missing"


@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("get", "/api/sessions/99999"),
        ("post", "/api/sessions/99999/end"),
    ],
)
def test_session_not_found_returns_json(client, trainer_token, method, endpoint):
    response = getattr(client, method)(
        endpoint,
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )
    assert response.status_code == 404
    assert response.get_json()["error"] == "Session not found"
