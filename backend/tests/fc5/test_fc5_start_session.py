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
