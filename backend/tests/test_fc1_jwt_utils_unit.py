from datetime import datetime, timedelta

import jwt
from flask import jsonify, request

from utils.jwt_utils import generate_token, token_required


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


def test_token_required_empty_bearer_token_returns_401(app):
    with app.test_request_context(headers={"Authorization": "Bearer "}):
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


def test_token_required_expired_token_returns_401(app):
    with app.app_context():
        payload = {
            "user_id": 3,
            "role": "trainer",
            "exp": datetime.utcnow() - timedelta(minutes=5),
            "iat": datetime.utcnow() - timedelta(minutes=10),
        }
        token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")

    with app.test_request_context(headers={"Authorization": f"Bearer {token}"}):
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


def test_token_required_accepts_raw_token_header(app):
    with app.app_context():
        token = generate_token(user_id=11, role="trainer")

    with app.test_request_context(headers={"Authorization": token}):
        @token_required
        def handler():
            return jsonify({"user_id": request.user_id, "role": request.user_role}), 200

        response, status = handler()

    assert status == 200
    assert response.get_json() == {"user_id": 11, "role": "trainer"}
