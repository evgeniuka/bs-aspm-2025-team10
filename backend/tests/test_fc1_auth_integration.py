from models.user import User


def create_test_user(
    db_session,
    email="trainer@example.com",
    password="password123",
    role="trainer",
):
    user = User(
        email=email,
        full_name="Test Trainer",
        role=role,
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
    db_session.refresh(user)
    assert user.last_login is not None


def test_login_success_for_trainee_returns_token_and_role(client, db_session):
    user = create_test_user(
        db_session,
        email="trainee@example.com",
        password="password123",
        role="trainee",
    )

    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "password123"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert "token" in payload
    assert payload["user"]["id"] == user.id
    assert payload["user"]["email"] == user.email
    assert payload["user"]["role"] == "trainee"


def test_login_wrong_credentials_for_trainee_returns_401(client, db_session):
    create_test_user(
        db_session,
        email="trainee@example.com",
        password="password123",
        role="trainee",
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "trainee@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Invalid email or password"


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


def test_register_success_persists_user_and_hashes_password(client, db_session):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "StrongPass123",
            "full_name": "New User",
            "role": "trainee",
        },
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert "token" in payload
    assert payload["user"]["email"] == "newuser@example.com"
    assert payload["user"]["role"] == "trainee"

    user = db_session.query(User).filter_by(email="newuser@example.com").first()
    assert user is not None
    assert user.password_hash != "StrongPass123"


def test_register_missing_fields_returns_400(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Missing required fields"


def test_me_with_invalid_token_returns_401(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Token is invalid or expired"


def test_me_with_invalid_token_format_returns_401(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer"},
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Invalid token format"


def test_me_with_deleted_user_returns_404(client, db_session):
    user = create_test_user(db_session)
    login_response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    token = login_response.get_json()["token"]

    db_session.delete(user)
    db_session.commit()

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["error"] == "User not found"


def test_logout_returns_success_message(client, db_session):
    user = create_test_user(db_session)
    login_response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    token = login_response.get_json()["token"]

    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["message"] == "Logged out successfully"
