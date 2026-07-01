import jwt
import pytest
from fastapi.testclient import TestClient

from app.auth import ALGORITHM, COOKIE_NAME
from app.config import Settings, get_settings
from app.main import app


def _login(client, seeded_trainer):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": seeded_trainer.email, "password": "password123"},
    )
    assert response.status_code == 200


def test_token_with_non_numeric_sub_returns_401(client):
    token = jwt.encode({"sub": "not-an-int", "role": "trainer"}, get_settings().secret_key, algorithm=ALGORITHM)
    client.cookies.set(COOKIE_NAME, token)
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_token_without_sub_returns_401(client):
    token = jwt.encode({"role": "trainer"}, get_settings().secret_key, algorithm=ALGORITHM)
    client.cookies.set(COOKIE_NAME, token)
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_mutation_without_csrf_header_is_rejected(seeded_trainer):
    bare_client = TestClient(app)  # intentionally omits X-Requested-With
    response = bare_client.post(
        "/api/v1/auth/login",
        json={"email": seeded_trainer.email, "password": "password123"},
    )
    assert response.status_code == 403


def test_safe_methods_do_not_require_csrf_header():
    bare_client = TestClient(app)
    assert bare_client.get("/api/v1/auth/me").status_code == 401  # 401, not 403


def test_client_creation_validates_bounds(client, seeded_trainer):
    _login(client, seeded_trainer)
    response = client.post(
        "/api/v1/clients",
        json={"name": "Ab", "age": 5, "fitness_level": "Beginner", "goals": "short"},
    )
    assert response.status_code == 422


def test_trainer_analytics_handles_no_data(client, seeded_trainer):
    _login(client, seeded_trainer)
    response = client.get("/api/v1/analytics/trainer")
    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 0
    assert data["completion_rate"] == 0
    assert data["total_volume_kg"] == 0


def test_weak_secret_rejected_outside_development(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("SECRET_KEY", "too-short")
    with pytest.raises(ValueError):
        Settings()


def test_strong_secret_accepted_outside_development(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("SECRET_KEY", "x" * 40)
    Settings()  # should not raise


def test_development_allows_default_secret(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("SECRET_KEY", "dev-secret-change-me")
    Settings()  # should not raise
