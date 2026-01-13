import pytest

from models import db
from models.client import Client
from models.exercise import Exercise
from models.program import Program, ProgramExercise
from models.session import Session, SessionClient


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


def test_create_session_persists_clients(client, app, trainer_token):
    payload = seed_clients_programs(app, trainer_token["user_id"], client_count=2)
    response = client.post(
        "/api/sessions",
        json=payload,
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Session created"
    assert isinstance(data["session_id"], int)

    with app.app_context():
        session = Session.query.get(data["session_id"])
        assert session is not None
        assert session.status == "active"
        session_clients = SessionClient.query.filter_by(session_id=session.id).all()
        assert len(session_clients) == 2
        assert {sc.client_id for sc in session_clients} == set(payload["client_ids"])
        assert {sc.program_id for sc in session_clients} == set(payload["program_ids"])


def test_get_session_returns_required_contract(client, app, trainer_token):
    payload = seed_clients_programs(app, trainer_token["user_id"], client_count=2)
    create_response = client.post(
        "/api/sessions",
        json=payload,
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )
    session_id = create_response.get_json()["session_id"]

    response = client.get(
        f"/api/sessions/{session_id}",
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == session_id
    assert data["trainer_id"] == trainer_token["user_id"]
    assert data["status"] == "active"
    assert isinstance(data["created_at"], str)
    assert isinstance(data["clients"], list)
    assert len(data["clients"]) == 2

    client_payload = data["clients"][0]
    assert isinstance(client_payload["id"], int)
    assert isinstance(client_payload["name"], str)
    assert isinstance(client_payload["program"], dict)
    assert isinstance(client_payload["program"]["id"], int)
    assert isinstance(client_payload["program"]["name"], str)
    assert isinstance(client_payload["program"]["exercises"], list)
    assert len(client_payload["program"]["exercises"]) > 0

    exercise_payload = client_payload["program"]["exercises"][0]
    assert isinstance(exercise_payload["id"], int)
    assert isinstance(exercise_payload["name"], str)
    assert isinstance(exercise_payload["sets"], int)
    assert isinstance(exercise_payload["reps"], int)

    assert isinstance(client_payload["current_exercise_index"], int)
    assert isinstance(client_payload["current_set"], int)
    assert isinstance(client_payload["status"], str)


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
        session = Session.query.get(session_id)
        assert session.status == "completed"
        assert session.end_time is not None


@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("post", "/api/sessions"),
        ("get", "/api/sessions/1"),
        ("post", "/api/sessions/1/end"),
    ],
)
def test_session_endpoints_require_auth(client, method, endpoint):
    response = getattr(client, method)(endpoint, json={})
    assert response.status_code == 401


def test_create_session_rejects_invalid_payload(client, app, trainer_token):
    payload = seed_clients_programs(app, trainer_token["user_id"], client_count=2)
    response = client.post(
        "/api/sessions",
        json={"client_ids": [payload["client_ids"][0]], "program_ids": []},
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation failed"
    assert isinstance(data["details"], list)


@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("get", "/api/sessions/99999"),
        ("post", "/api/sessions/99999/end"),
    ],
)
def test_session_not_found(client, trainer_token, method, endpoint):
    response = getattr(client, method)(
        endpoint,
        headers={"Authorization": f"Bearer {trainer_token['token']}"},
    )
    assert response.status_code == 404
