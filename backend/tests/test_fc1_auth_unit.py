from datetime import datetime, timedelta

import jwt
from flask import jsonify

from models.user import User
from utils.jwt_utils import decode_token, generate_token, role_required


def test_password_hashing_and_verification():
    user = User(
        email="unit@example.com",
        full_name="Unit Test",
        role="trainer",
        is_active=True,
    )
    user.set_password("StrongPass123")

    assert user.check_password("StrongPass123") is True
    assert user.check_password("WrongPass") is False


def test_generate_and_decode_token(app):
    with app.app_context():
        token = generate_token(user_id=42, role="trainer")
        payload = decode_token(token)

    assert payload is not None
    assert payload["user_id"] == 42
    assert payload["role"] == "trainer"


def test_decode_token_invalid_signature_returns_none(app):
    with app.app_context():
        token = jwt.encode(
            {"user_id": 1, "role": "trainer", "exp": datetime.utcnow() + timedelta(minutes=5)},
            "wrong-secret",
            algorithm="HS256",
        )
        payload = decode_token(token)

    assert payload is None


def test_decode_token_expired_returns_none(app):
    with app.app_context():
        token = jwt.encode(
            {"user_id": 1, "role": "trainer", "exp": datetime.utcnow() - timedelta(minutes=1)},
            app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )
        payload = decode_token(token)

    assert payload is None


def test_role_required_denies_wrong_role(app):
    with app.test_request_context():
        def handler():
            return jsonify({"ok": True}), 200

        protected = role_required("trainer")(handler)
        response, status = protected()

    assert status == 403
    assert response.get_json()["error"] == "Insufficient permissions"
