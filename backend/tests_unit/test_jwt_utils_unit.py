from datetime import timedelta

from flask import Flask, jsonify, request

from utils.jwt_utils import decode_token, generate_token, role_required, token_required


def _make_app(expiry_seconds=60):
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "unit-test-secret"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=expiry_seconds)
    return app


def test_generate_and_decode_token_round_trip():
    app = _make_app()
    with app.app_context():
        token = generate_token(user_id=42, role="trainer")
        payload = decode_token(token)

    assert payload["user_id"] == 42
    assert payload["role"] == "trainer"


def test_decode_token_expired_returns_none():
    app = _make_app(expiry_seconds=-1)
    with app.app_context():
        token = generate_token(user_id=1, role="trainer")
        payload = decode_token(token)

    assert payload is None


def test_token_required_missing_token():
    app = _make_app()

    @token_required
    def protected():
        return jsonify({"ok": True}), 200

    with app.test_request_context():
        response, status = protected()

    assert status == 401
    assert response.get_json() == {"error": "Token is missing"}


def test_token_required_invalid_format():
    app = _make_app()

    @token_required
    def protected():
        return jsonify({"ok": True}), 200

    with app.test_request_context(headers={"Authorization": "Bearer"}):
        response, status = protected()

    assert status == 401
    assert response.get_json() == {"error": "Invalid token format"}


def test_token_required_invalid_token():
    app = _make_app()

    @token_required
    def protected():
        return jsonify({"ok": True}), 200

    with app.test_request_context(headers={"Authorization": "Bearer not-a-token"}):
        response, status = protected()

    assert status == 401
    assert response.get_json() == {"error": "Token is invalid or expired"}


def test_token_required_allows_valid_token():
    app = _make_app()

    @token_required
    def protected():
        return jsonify({"ok": True, "user_id": request.user_id, "role": request.user_role}), 200

    with app.app_context():
        token = generate_token(user_id=7, role="trainer")

    with app.test_request_context(headers={"Authorization": f"Bearer {token}"}):
        response, status = protected()

    assert status == 200
    assert response.get_json() == {"ok": True, "user_id": 7, "role": "trainer"}


def test_role_required_rejects_wrong_role():
    app = _make_app()

    @token_required
    @role_required("trainer")
    def protected():
        return jsonify({"ok": True}), 200

    with app.app_context():
        token = generate_token(user_id=10, role="trainee")

    with app.test_request_context(headers={"Authorization": f"Bearer {token}"}):
        response, status = protected()

    assert status == 403
    assert response.get_json() == {"error": "Insufficient permissions"}
