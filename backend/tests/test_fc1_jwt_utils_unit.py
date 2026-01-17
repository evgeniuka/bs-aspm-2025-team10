from datetime import datetime, timedelta

import jwt
from flask import jsonify, request

from utils.jwt_utils import decode_token, generate_token, role_required, token_required


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


def test_token_required_missing_header_returns_401(app):
    with app.test_request_context():
        @token_required
        def handler():
            return jsonify({"ok": True}), 200

        response, status = handler()

    assert status == 401
    assert response.get_json()["error"] == "Token is missing"


def test_token_required_invalid_format_returns_401(app):
    with app.test_request_context(headers={"Authorization": "Bearer"}):
        @token_required
        def handler():
            return jsonify({"ok": True}), 200

        response, status = handler()

    assert status == 401
    assert response.get_json()["error"] == "Invalid token format"


def test_token_required_invalid_token_returns_401(app):
    with app.test_request_context(headers={"Authorization": "Bearer invalid.token"}):
        @token_required
        def handler():
            return jsonify({"ok": True}), 200

        response, status = handler()

    assert status == 401
    assert response.get_json()["error"] == "Token is invalid or expired"


def test_token_required_sets_request_user_data(app):
    with app.app_context():
        token = generate_token(user_id=7, role="trainer")

    with app.test_request_context(headers={"Authorization": f"Bearer {token}"}):
        @token_required
        def handler():
            return jsonify({"user_id": request.user_id, "role": request.user_role}), 200

        response, status = handler()

    assert status == 200
    assert response.get_json() == {"user_id": 7, "role": "trainer"}
