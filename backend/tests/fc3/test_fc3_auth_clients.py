import pytest

from models import db
from models.client import Client
from models.user import User
from utils.jwt_utils import generate_token


def _create_user(email, password="password123", full_name="Test User", role="trainer"):
    user = User(email=email, full_name=full_name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def _auth_header(app, user):
    with app.app_context():
        token = generate_token(user.id, user.role)
    return {"Authorization": f"Bearer {token}"}


def test_register_requires_fields(app_client):
    _app, client = app_client

    response = client.post("/api/auth/register", json={"email": "x@example.com"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing required fields"}


def test_register_rejects_short_password(app_client):
    _app, client = app_client

    payload = {
        "email": "trainer@example.com",
        "password": "short",
        "full_name": "Trainer One",
        "role": "trainer",
    }

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"error": "Password must be at least 8 characters long"}


def test_register_creates_user_and_returns_token(app_client):
    app, client = app_client

    payload = {
        "email": "trainer@example.com",
        "password": "password123",
        "full_name": "Trainer One",
        "role": "trainer",
    }

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 201
    body = response.get_json()
    assert "token" in body
    assert body["user"]["email"] == "trainer@example.com"
    assert body["user"]["role"] == "trainer"
    with app.app_context():
        assert User.query.filter_by(email="trainer@example.com").count() == 1


def test_login_updates_last_login_and_returns_user(app_client):
    app, client = app_client

    with app.app_context():
        user = _create_user("login@example.com")
        assert user.last_login is None

    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert "token" in body
    assert body["user"]["email"] == "login@example.com"
    with app.app_context():
        refreshed = User.query.filter_by(email="login@example.com").first()
        assert refreshed.last_login is not None


def test_login_rejects_invalid_credentials(app_client):
    app, client = app_client

    with app.app_context():
        _create_user("fail@example.com")

    response = client.post(
        "/api/auth/login",
        json={"email": "fail@example.com", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid email or password"}


def test_auth_me_requires_existing_user(app_client):
    app, client = app_client

    with app.app_context():
        user = _create_user("me@example.com")
        headers = _auth_header(app, user)
        db.session.delete(user)
        db.session.commit()

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}


def test_logout_success(app_client):
    app, client = app_client

    with app.app_context():
        user = _create_user("logout@example.com")
        headers = _auth_header(app, user)

    response = client.post("/api/auth/logout", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == {"message": "Logged out successfully"}


def test_get_clients_returns_only_active_for_trainer(app_client):
    app, client = app_client

    with app.app_context():
        trainer = _create_user("trainer@example.com", role="trainer")
        other_trainer = _create_user("trainer2@example.com", role="trainer")
        active_client = Client(
            trainer_id=trainer.id,
            user_id=None,
            name="Active Client",
            age=30,
            fitness_level="Beginner",
            goals="Build strength fast",
            active=True,
        )
        inactive_client = Client(
            trainer_id=trainer.id,
            user_id=None,
            name="Inactive Client",
            age=28,
            fitness_level="Intermediate",
            goals="Improve endurance",
            active=False,
        )
        other_client = Client(
            trainer_id=other_trainer.id,
            user_id=None,
            name="Other Client",
            age=40,
            fitness_level="Advanced",
            goals="Stay fit consistently",
            active=True,
        )
        db.session.add_all([active_client, inactive_client, other_client])
        db.session.commit()
        headers = _auth_header(app, trainer)

    response = client.get("/api/clients", headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert [item["name"] for item in data] == ["Active Client"]


def test_create_client_validates_payload(app_client):
    app, client = app_client

    with app.app_context():
        trainer = _create_user("clientcreate@example.com", role="trainer")
        headers = _auth_header(app, trainer)

    response = client.post(
        "/api/clients",
        headers=headers,
        json={
            "name": "A",
            "age": 10,
            "fitness_level": "Unknown",
            "goals": "Too short",
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Name must be 2-50 characters"}


def test_update_client_rejects_invalid_age(app_client):
    app, client = app_client

    with app.app_context():
        trainer = _create_user("update@example.com", role="trainer")
        client_record = Client(
            trainer_id=trainer.id,
            user_id=None,
            name="Client One",
            age=30,
            fitness_level="Beginner",
            goals="Improve strength and mobility",
            active=True,
        )
        db.session.add(client_record)
        db.session.commit()
        headers = _auth_header(app, trainer)

    response = client.put(
        f"/api/clients/{client_record.id}",
        headers=headers,
        json={"age": 10},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Age must be between 1 6  and 100"}


def test_deactivate_client_marks_inactive(app_client):
    app, client = app_client

    with app.app_context():
        trainer = _create_user("deactivate@example.com", role="trainer")
        client_record = Client(
            trainer_id=trainer.id,
            user_id=None,
            name="Client Two",
            age=35,
            fitness_level="Intermediate",
            goals="Stay active and healthy",
            active=True,
        )
        db.session.add(client_record)
        db.session.commit()
        headers = _auth_header(app, trainer)

    response = client.post(f"/api/clients/{client_record.id}/deactivate", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == {"message": "Client deactivated"}
    with app.app_context():
        refreshed = Client.query.get(client_record.id)
        assert refreshed.active is False


def test_get_my_client_returns_not_found(app_client):
    app, client = app_client

    with app.app_context():
        trainee = _create_user("trainee@example.com", role="trainee")
        headers = _auth_header(app, trainee)

    response = client.get("/api/clients/my", headers=headers)

    assert response.status_code == 404
    assert response.get_json() == {"error": "No client profile found"}
