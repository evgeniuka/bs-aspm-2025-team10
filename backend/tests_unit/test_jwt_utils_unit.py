from datetime import timedelta

from utils import jwt_utils


class DummyApp:
    config = {
        "JWT_ACCESS_TOKEN_EXPIRES": timedelta(minutes=5),
        "JWT_SECRET_KEY": "unit-test-secret",
    }


def _patch_current_app(monkeypatch):
    monkeypatch.setattr(jwt_utils, "current_app", DummyApp())


def test_generate_and_decode_token_round_trip(monkeypatch):
    _patch_current_app(monkeypatch)
    token = jwt_utils.generate_token(user_id=42, role="trainer")
    payload = jwt_utils.decode_token(token)
    assert payload["user_id"] == 42
    assert payload["role"] == "trainer"


def test_decode_token_returns_none_for_invalid_token(monkeypatch):
    _patch_current_app(monkeypatch)
    payload = jwt_utils.decode_token("not-a-token")
    assert payload is None
