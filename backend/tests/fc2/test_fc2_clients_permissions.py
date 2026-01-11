import os
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(BACKEND_ROOT))

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    pytest.fail("DATABASE_URL is not set")

from models import db
from models.user import User


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


def test_missing_token_returns_401(client):
    response = client.get("/api/clients")

    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Token is missing"


def test_wrong_role_returns_403(client, app):
    trainee = _create_user("trainee@example.com", "trainee", full_name="Trainee User")
    headers = _auth_headers(trainee)

    payload = {
        "name": "Blocked Client",
        "age": 25,
        "fitness_level": "Beginner",
        "goals": "Improve core strength"
    }

    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 403
    data = response.get_json()
    assert data["error"] == "Insufficient permissions"


def test_invalid_authorization_format_returns_401(client, app):
    response = client.get("/api/clients", headers={"Authorization": "Bearer"})

    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Invalid token format"


def test_invalid_token_returns_401(client, app):
    response = client.get("/api/clients", headers={"Authorization": "Bearer invalid.token.value"})

    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Token is invalid or expired"


def test_trainer_cannot_access_trainee_client_profile(client, app):
    trainer = _create_user("trainer.profile.block@example.com", "trainer", full_name="Trainer Block")
    headers = _auth_headers(trainer)

    response = client.get("/api/clients/my", headers=headers)

    assert response.status_code == 403
    data = response.get_json()
    assert data["error"] == "Insufficient permissions"
