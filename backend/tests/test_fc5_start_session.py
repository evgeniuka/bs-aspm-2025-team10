from models import db
from models.client import Client
from models.program import Program
from models.session import Session, SessionClient
from models.user import User
from utils.jwt_utils import generate_token


def _create_trainer(app):
    with app.app_context():
        trainer = User(email="trainer@example.com", full_name="Test Trainer", role="trainer")
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


def _create_single_client(app, trainer_id, name_suffix="Solo"):
    with app.app_context():
        client = Client(
            trainer_id=trainer_id,
            name=f"Client {name_suffix}",
            age=30,
            fitness_level="Beginner",
            goals="Endurance",
            active=True,
        )
        db.session.add(client)
        db.session.commit()
        return client.id


def _create_program_for_client(app, trainer_id, client_id, name_suffix="Solo"):
    with app.app_context():
        program = Program(
            trainer_id=trainer_id,
            client_id=client_id,
            name=f"Program {name_suffix}",
            notes="Custom program",
        )
        db.session.add(program)
        db.session.commit()
        return program.id


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
    response = client.post("/api/sessions", json={"client_ids": [1, 2], "program_ids": [10, 20]})

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Token is missing"


def test_fc5_start_training_session_rejects_invalid_counts(client, app):
    trainer_id, token = _create_trainer(app)
    response = client.post(
        "/api/sessions",
        json={"client_ids": [], "program_ids": []},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "At least 1 client is required" in payload["details"]


def test_fc5_start_training_session_accepts_single_client(client, app):
    trainer_id, token = _create_trainer(app)
    client_id = _create_single_client(app, trainer_id)
    program_id = _create_program_for_client(app, trainer_id, client_id)

    response = client.post(
        "/api/sessions",
        json={"client_ids": [client_id], "program_ids": [program_id]},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    payload = response.get_json()
    session_id = payload["session_id"]
    with app.app_context():
        session_clients = SessionClient.query.filter_by(session_id=session_id).all()
        assert len(session_clients) == 1
        assert session_clients[0].client_id == client_id
        assert session_clients[0].program_id == program_id


def test_fc5_start_training_session_accepts_four_clients(client, app):
    trainer_id, token = _create_trainer(app)
    with app.app_context():
        clients = []
        programs = []
        for idx in range(4):
            client_record = Client(
                trainer_id=trainer_id,
                name=f"Client {idx + 1}",
                age=20 + idx,
                fitness_level="Beginner",
                goals="Strength",
                active=True,
            )
            db.session.add(client_record)
            db.session.flush()
            program = Program(
                trainer_id=trainer_id,
                client_id=client_record.id,
                name=f"Program {idx + 1}",
                notes="Group program",
            )
            db.session.add(program)
            clients.append(client_record.id)
            programs.append(program.id)
        db.session.commit()

    response = client.post(
        "/api/sessions",
        json={"client_ids": clients, "program_ids": programs},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    session_id = response.get_json()["session_id"]
    with app.app_context():
        session_clients = SessionClient.query.filter_by(session_id=session_id).all()
        assert len(session_clients) == 4


def test_fc5_start_training_session_rejects_other_trainer_clients(client, app):
    trainer_a_id, trainer_a_token = _create_trainer(app)
    with app.app_context():
        trainer_b = User(email="trainer_b@example.com", full_name="Trainer B", role="trainer")
        trainer_b.set_password("password123")
        db.session.add(trainer_b)
        db.session.commit()
        trainer_b_id = trainer_b.id

    client_id = _create_single_client(app, trainer_b_id, name_suffix="Other")
    program_id = _create_program_for_client(app, trainer_b_id, client_id, name_suffix="Other")

    response = client.post(
        "/api/sessions",
        json={"client_ids": [client_id], "program_ids": [program_id]},
        headers={"Authorization": f"Bearer {trainer_a_token}"},
    )

    assert response.status_code == 403
    payload = response.get_json()
    assert "not assigned to trainer" in " ".join(payload["details"])


def test_fc5_start_training_session_rejects_too_many_clients(client, app):
    trainer_id, token = _create_trainer(app)
    with app.app_context():
        clients = []
        programs = []
        for idx in range(5):
            client_record = Client(
                trainer_id=trainer_id,
                name=f"Client {idx + 1}",
                age=20 + idx,
                fitness_level="Beginner",
                goals="Strength",
                active=True,
            )
            db.session.add(client_record)
            db.session.flush()
            program = Program(
                trainer_id=trainer_id,
                client_id=client_record.id,
                name=f"Program {idx + 1}",
                notes="Bulk program",
            )
            db.session.add(program)
            clients.append(client_record.id)
            programs.append(program.id)
        db.session.commit()

    response = client.post(
        "/api/sessions",
        json={"client_ids": clients, "program_ids": programs},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "Maximum 4 clients allowed" in payload["details"]


def test_fc5_start_training_session_rejects_missing_programs(client, app):
    trainer_id, token = _create_trainer(app)
    client_id = _create_single_client(app, trainer_id)
    second_client_id = _create_single_client(app, trainer_id, name_suffix="Second")

    response = client.post(
        "/api/sessions",
        json={"client_ids": [client_id, second_client_id]},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "Each selected client must have a program assigned" in payload["details"]


def test_fc5_start_training_session_rejects_program_mismatch(client, app):
    trainer_id, token = _create_trainer(app)
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)

    response = client.post(
        "/api/sessions",
        json={"client_ids": client_ids, "program_ids": list(reversed(program_ids))},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert f"Program ID {program_ids[1]} is not assigned to Client ID {client_ids[0]}" in payload["details"]


def test_fc5_start_training_session_rejects_missing_entities(client, app):
    trainer_id, token = _create_trainer(app)
    client_ids, program_ids = _create_clients_and_programs(app, trainer_id)
    missing_client = max(client_ids) + 100
    missing_program = max(program_ids) + 200

    response = client.post(
        "/api/sessions",
        json={
            "client_ids": [client_ids[0], missing_client],
            "program_ids": [program_ids[0], missing_program],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert f"Client ID {missing_client} not found" in payload["details"]
    assert f"Program ID {missing_program} not found" in payload["details"]


def test_fc5_get_session_returns_contract(client, app):
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
    assert {"client_id", "client_name", "program_id", "program_name", "current_exercise_index", "current_set", "status"} <= set(
        payload["clients"][0].keys()
    )
