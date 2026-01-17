from models.user import User


def test_register_invalid_role_returns_400(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "invalidrole@example.com",
            "password": "StrongPass123",
            "full_name": "Invalid Role",
            "role": "manager",
        },
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Invalid role. Must be trainer or trainee"


def test_register_short_password_returns_400(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "shortpass@example.com",
            "password": "short",
            "full_name": "Short Password",
            "role": "trainer",
        },
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Password must be at least 8 characters long"


def test_register_duplicate_email_returns_409(client, db_session):
    user = User(email="dup@example.com", full_name="Dup User", role="trainer")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/auth/register",
        json={
            "email": "dup@example.com",
            "password": "StrongPass123",
            "full_name": "Dup User",
            "role": "trainer",
        },
    )

    assert response.status_code == 409
    payload = response.get_json()
    assert payload["error"] == "Email already registered"
