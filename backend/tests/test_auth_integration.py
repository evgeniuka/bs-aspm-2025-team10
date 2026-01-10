from models.user import User


def create_test_user(db_session, email="trainer@example.com", password="password123"):
    user = User(
        email=email,
        full_name="Test Trainer",
        role="trainer",
        is_active=True,
    )
    user.set_password(password)
    db_session.add(user)
    db_session.commit()
    return user


def test_login_missing_fields_returns_400(client):
    response = client.post("/api/auth/login", json={})

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Email and password are required"


def test_login_wrong_credentials_returns_401(client, db_session):
    create_test_user(db_session)

    response = client.post(
        "/api/auth/login",
        json={"email": "trainer@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Invalid email or password"


def test_login_success_returns_token_and_user(client, db_session):
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
    assert payload["user"]["role"] == user.role


def test_me_requires_token(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Token is missing"


def test_me_with_token_returns_user(client, db_session):
    user = create_test_user(db_session)

    login_response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    token = login_response.get_json()["token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == user.id
    assert payload["email"] == user.email
    assert payload["role"] == user.role
