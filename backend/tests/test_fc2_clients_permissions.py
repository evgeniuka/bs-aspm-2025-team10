from models import db
from models.user import User


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


def test_missing_token_on_deactivate_returns_401(client):
    response = client.post("/api/clients/1/deactivate")

    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Token is missing"


def test_wrong_role_returns_403(client):
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


def test_invalid_authorization_format_returns_401(client):
    response = client.get("/api/clients", headers={"Authorization": "Bearer"})

    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Invalid token format"


def test_invalid_token_returns_401(client):
    response = client.get("/api/clients", headers={"Authorization": "Bearer invalid.token.value"})

    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Token is invalid or expired"


def test_trainer_cannot_access_trainee_client_profile(client):
    trainer = _create_user("trainer.profile.block@example.com", "trainer", full_name="Trainer Block")
    headers = _auth_headers(trainer)

    response = client.get("/api/clients/my", headers=headers)

    assert response.status_code == 403
    data = response.get_json()
    assert data["error"] == "Insufficient permissions"
