import os
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(BACKEND_ROOT))

database_url = os.environ.get("DATABASE_URL_TEST")
if not database_url:
    pytest.skip("DATABASE_URL_TEST is not set", allow_module_level=True)

os.environ["DATABASE_URL"] = database_url

from models import db
from models.user import User
from models.client import Client


def _build_app():
    import config as app_config

    app_config.Config.SQLALCHEMY_DATABASE_URI = database_url

    from app import create_app

    app, _ = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def app():
    app = _build_app()
    ctx = app.app_context()
    ctx.push()
    db.drop_all()
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()
    ctx.pop()


@pytest.fixture()
def client(app):
    return app.test_client()


def _create_user(email, role, full_name="Test User", password="password123"):
    user = User(email=email, full_name=full_name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def _auth_headers(user):
    from utils.jwt_utils import generate_token

    token = generate_token(user.id, user.role)
    return {"Authorization": f"Bearer {token}"}


def test_trainer_can_create_client(client, app):
    trainer = _create_user("trainer@example.com", "trainer", full_name="Trainer One")
    headers = _auth_headers(trainer)

    payload = {
        "name": "Alex Client",
        "age": 28,
        "fitness_level": "Intermediate",
        "goals": "Build strength and endurance"
    }
    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == payload["name"]
    assert data["age"] == payload["age"]
    assert data["fitness_level"] == payload["fitness_level"]
    assert data["goals"] == payload["goals"]
    assert data["active"] is True
    assert data["user_id"] is None

    db_client = Client.query.filter_by(id=data["id"]).first()
    assert db_client is not None
    assert db_client.trainer_id == trainer.id
    assert db_client.name == payload["name"]


def test_trainer_can_list_clients(client, app):
    trainer = _create_user("trainer.list@example.com", "trainer", full_name="Trainer Two")
    headers = _auth_headers(trainer)

    active_client = Client(
        trainer_id=trainer.id,
        name="Active Client",
        age=30,
        fitness_level="Beginner",
        goals="Improve flexibility and balance"
    )
    inactive_client = Client(
        trainer_id=trainer.id,
        name="Inactive Client",
        age=34,
        fitness_level="Advanced",
        goals="Run a marathon next year",
        active=False
    )
    db.session.add_all([active_client, inactive_client])
    db.session.commit()

    response = client.get("/api/clients", headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Active Client"
    assert data[0]["active"] is True
    assert "id" in data[0]
    assert "created_at" in data[0]


def test_create_client_missing_required_field_returns_400(client, app):
    trainer = _create_user("trainer.missing@example.com", "trainer", full_name="Trainer Three")
    headers = _auth_headers(trainer)

    payload = {
        "age": 22,
        "fitness_level": "Beginner",
        "goals": "Lose weight safely"
    }

    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_create_client_invalid_field_format_returns_400(client, app):
    trainer = _create_user("trainer.invalid@example.com", "trainer", full_name="Trainer Four")
    headers = _auth_headers(trainer)

    payload = {
        "name": "Casey Client",
        "age": 27,
        "fitness_level": "Expert",
        "goals": "Increase endurance over time"
    }

    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid fitness level"


def test_update_nonexistent_client_returns_404(client, app):
    trainer = _create_user("trainer.notfound@example.com", "trainer", full_name="Trainer Five")
    headers = _auth_headers(trainer)

    response = client.put("/api/clients/9999", json={"name": "New Name"}, headers=headers)

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Client not found"
