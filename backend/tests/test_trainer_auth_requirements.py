from models.user import User
from utils.jwt_utils import decode_token


def create_test_user(
    db_session,
    email="trainer@example.com",
    password="password123",
    role="trainer",
):
    user = User(
        email=email,
        full_name="Test User",
        role=role,
        is_active=True,
    )
    user.set_password(password)
    db_session.add(user)
    db_session.commit()
    return user


def test_trainer_login_success(client, db_session, app):
    user = create_test_user(db_session)

    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "password123"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert "token" in payload
    assert payload["user"]["id"] == user.id
    assert payload["user"]["email"] == user.email
    assert payload["user"]["role"] == "trainer"

    with app.app_context():
        claims = decode_token(payload["token"])

    assert claims["user_id"] == user.id
    assert claims["role"] == "trainer"


def test_trainer_login_invalid_credentials(client, db_session):
    create_test_user(db_session)

    response = client.post(
        "/api/auth/login",
        json={"email": "trainer@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Invalid email or password"


def test_trainer_login_missing_fields(client):
    response = client.post("/api/auth/login", json={"email": "trainer@example.com"})

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Email and password are required"

    response = client.post("/api/auth/login", json={"password": "password123"})

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Email and password are required"


def test_protected_route_requires_jwt(client):
    response = client.get("/api/clients")

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Token is missing"


def test_trainee_cannot_access_trainer_routes(client, db_session):
    user = create_test_user(
        db_session,
        email="trainee@example.com",
        password="password123",
        role="trainee",
    )

    login_response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    token = login_response.get_json()["token"]

    response = client.get(
        "/api/clients",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    payload = response.get_json()
    assert payload["error"] == "Insufficient permissions"
