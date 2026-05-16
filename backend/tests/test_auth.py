def test_login_sets_http_only_cookie(client, seeded_trainer):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": seeded_trainer.email, "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == seeded_trainer.email
    assert "fitcoach_token" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]


def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
