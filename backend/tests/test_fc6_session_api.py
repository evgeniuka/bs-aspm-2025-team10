import pytest

from models import db
from models.client import Client
from models.program import Program
from models.session import Session
from models.user import User
from utils.jwt_utils import generate_token


def _create_trainer(app, email_suffix="primary"):
    with app.app_context():
        user = User(
            email=f"trainer.{email_suffix}@example.com",
            full_name=f"Trainer {email_suffix.title()}",
            role="trainer",
            is_active=True,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.id, user.role)
        return user.id, token


def _create_clients_and_programs(app, trainer_id, count=2):
    with app.app_context():
        client_ids = []
        program_ids = []
        for idx in range(count):
            client = Client(
                trainer_id=trainer_id,
                name=f"Client {idx + 1}",
                age=22 + idx,
                fitness_level="Beginner",
                goals="Strength",
                active=True,
            )
            db.session.add(client)
            db.session.flush()
            program = Program(
                trainer_id=trainer_id,
                client_id=client.id,
                name=f"Program {idx + 1}",
                notes="Session prep",
            )
            db.session.add(program)
            db.session.flush()
            client_ids.append(client.id)
            program_ids.append(program.id)
        db.session.commit()
        return client_ids, program_ids


def _create_session_via_api(client, trainer_token, client_ids, program_ids):
    response = client.post(
        "/api/sessions",
        json={"client_ids": client_ids, "program_ids": program_ids},
        headers={"Authorization": f"Bearer {trainer_token}"},
    )
    assert response.status_code == 201
    return response.get_json()["session_id"]


def test_fc6_end_session_marks_completed(client, app):
    trainer_id, token = _create_trainer(app)
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)
    session_id = _create_session_via_api(client, token, client_ids, program_ids)

    response = client.post(
        f"/api/sessions/{session_id}/end",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Session ended successfully"

    with app.app_context():
        session = db.session.get(Session, session_id)
        assert session.status == "completed"
        assert session.end_time is not None
        assert session.end_time >= session.start_time


def test_fc6_end_session_rejects_other_trainer(client, app):
    trainer_id, token = _create_trainer(app)
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)
    session_id = _create_session_via_api(client, token, client_ids, program_ids)

    other_trainer_id, other_token = _create_trainer(app, email_suffix="secondary")

    response = client.post(
        f"/api/sessions/{session_id}/end",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Session not found"

    with app.app_context():
        session = db.session.get(Session, session_id)
        assert session.trainer_id == trainer_id
        assert session.status == "active"
        assert session.end_time is None


@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("get", "/api/sessions/1"),
        ("post", "/api/sessions/1/end"),
    ],
)
def test_fc6_session_endpoints_require_auth(client, method, endpoint):
    response = getattr(client, method)(endpoint)
    assert response.status_code == 401
    assert response.get_json()["error"] == "Token is missing"


def test_fc6_get_session_returns_details(client, app):
    trainer_id, token = _create_trainer(app)
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)
    session_id = _create_session_via_api(client, token, client_ids, program_ids)

    response = client.get(
        f"/api/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == session_id
    assert payload["trainer_id"] == trainer_id
    assert payload["status"] == "active"
    assert payload["clients"]
    assert {"client_id", "client_name", "program_id", "program_name"} <= set(
        payload["clients"][0].keys()
    )


def test_fc6_get_session_not_found_returns_json(client, app):
    _trainer_id, token = _create_trainer(app)
    response = client.get(
        "/api/sessions/99999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Session not found"
