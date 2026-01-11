from models import db
from models.client import Client
from models.program import Program
from models.session import Session, SessionClient
from models.user import User
from utils.jwt_utils import generate_token


def _create_trainer(app, email="trainer@example.com"):
    with app.app_context():
        trainer = User(email=email, full_name="Test Trainer", role="trainer")
        trainer.set_password("password123")
        db.session.add(trainer)
        db.session.commit()
        trainer_id = trainer.id
        token = generate_token(trainer_id, trainer.role)
    return trainer_id, token


def _create_clients_and_programs(app, trainer_id):
    with app.app_context():
        clients = []
        programs = []
        for idx in range(2):
            client = Client(
                trainer_id=trainer_id,
                name=f"Client {idx + 1}",
                age=25 + idx,
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
                notes="Intro program",
            )
            db.session.add(program)
            clients.append(client)
            programs.append(program)
        db.session.commit()
        client_ids = [client.id for client in clients]
        program_ids = [program.id for program in programs]
    return client_ids, program_ids


def test_fc5_start_training_session_creates_session(client, app):
    trainer_id, token = _create_trainer(app)
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)

    response = client.post(
        "/api/sessions",
        json={"client_ids": client_ids, "program_ids": program_ids},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["message"] == "Session created"
    assert "session_id" in payload

    session_id = payload["session_id"]
    with app.app_context():
        session = db.session.get(Session, session_id)
        assert session is not None
        assert session.trainer_id == trainer_id
        session_clients = SessionClient.query.filter_by(session_id=session_id).all()
        assert len(session_clients) == 2
        expected_pairs = set(zip(client_ids, program_ids))
        actual_pairs = {(sc.client_id, sc.program_id) for sc in session_clients}
        assert actual_pairs == expected_pairs


def test_fc5_start_training_session_requires_auth(client, app):
    response = client.post(
        "/api/sessions",
        json={"client_ids": [1, 2], "program_ids": [1, 2]},
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Token is missing"


def test_fc5_start_training_session_rejects_malformed_token(client, app):
    response = client.post(
        "/api/sessions",
        json={"client_ids": [1, 2], "program_ids": [1, 2]},
        headers={"Authorization": "Bearer"},
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Invalid token format"


def test_fc5_start_training_session_rejects_invalid_token(client, app):
    response = client.post(
        "/api/sessions",
        json={"client_ids": [1, 2], "program_ids": [1, 2]},
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Token is invalid or expired"


def test_fc5_start_training_session_rejects_empty_clients(client, app):
    trainer_id, token = _create_trainer(app)

    response = client.post(
        "/api/sessions",
        json={"client_ids": [], "program_ids": []},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Validation failed"
    assert "At least 2 clients are required" in payload["details"]
    assert "Each selected client must have a program assigned" in payload["details"]


def test_fc5_start_training_session_rejects_too_many_clients(client, app):
    trainer_id, token = _create_trainer(app)
    with app.app_context():
        clients = []
        programs = []
        for idx in range(5):
            client_obj = Client(
                trainer_id=trainer_id,
                name=f"Client {idx + 1}",
                age=30 + idx,
                fitness_level="Beginner",
                goals="Strength",
                active=True,
            )
            db.session.add(client_obj)
            db.session.flush()
            program_obj = Program(
                trainer_id=trainer_id,
                client_id=client_obj.id,
                name=f"Program {idx + 1}",
                notes="Overflow program",
            )
            db.session.add(program_obj)
            clients.append(client_obj)
            programs.append(program_obj)
        db.session.commit()
        client_ids = [client_obj.id for client_obj in clients]
        program_ids = [program_obj.id for program_obj in programs]

    response = client.post(
        "/api/sessions",
        json={"client_ids": client_ids, "program_ids": program_ids},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Validation failed"
    assert payload["details"] == ["Maximum 4 clients allowed"]


def test_fc5_start_training_session_rejects_program_mismatch(client, app):
    trainer_id, token = _create_trainer(app)
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)

    response = client.post(
        "/api/sessions",
        json={"client_ids": client_ids, "program_ids": program_ids[:1]},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Validation failed"
    assert payload["details"] == ["Each selected client must have a program assigned"]


def test_fc5_start_training_session_rejects_unknown_client(client, app):
    trainer_id, token = _create_trainer(app)
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)
    missing_client_id = max(client_ids) + 999

    response = client.post(
        "/api/sessions",
        json={
            "client_ids": [client_ids[0], missing_client_id],
            "program_ids": program_ids,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Validation failed"
    assert payload["details"] == [f"Client ID {missing_client_id} not found"]


def test_fc5_start_training_session_rejects_unknown_program(client, app):
    trainer_id, token = _create_trainer(app)
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)
    missing_program_id = max(program_ids) + 999

    response = client.post(
        "/api/sessions",
        json={
            "client_ids": client_ids,
            "program_ids": [program_ids[0], missing_program_id],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Validation failed"
    assert payload["details"] == [f"Program ID {missing_program_id} not found"]


def test_fc5_get_session_returns_details(client, app):
    trainer_id, token = _create_trainer(app)
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)

    create_response = client.post(
        "/api/sessions",
        json={"client_ids": client_ids, "program_ids": program_ids},
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = create_response.get_json()["session_id"]

    response = client.get(
        f"/api/sessions/{session_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == session_id
    assert payload["trainer_id"] == trainer_id
    assert payload["status"] == "active"
    assert len(payload["clients"]) == 2
    expected_pairs = set(zip(client_ids, program_ids))
    actual_pairs = {(entry["client_id"], entry["program_id"]) for entry in payload["clients"]}
    assert actual_pairs == expected_pairs


def test_fc5_get_session_rejects_other_trainer(client, app):
    trainer_id, token = _create_trainer(app)
    _, other_token = _create_trainer(app, email="trainer2@example.com")
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)

    create_response = client.post(
        "/api/sessions",
        json={"client_ids": client_ids, "program_ids": program_ids},
        headers={"Authorization": f"Bearer {token}"},
    )
    session_id = create_response.get_json()["session_id"]

    response = client.get(
        f"/api/sessions/{session_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["error"] == "Session not found"
