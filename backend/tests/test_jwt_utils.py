from flask import jsonify

from utils.jwt_utils import generate_token, role_required, token_required


def test_token_required_missing_token(client, app):
    @token_required
    def protected():
        return jsonify({"ok": True}), 200

    app.add_url_rule("/test/protected-missing", "protected_missing", protected)

    response = client.get("/test/protected-missing")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Token is missing"


def test_token_required_invalid_format(client, app):
    @token_required
    def protected():
        return jsonify({"ok": True}), 200

    app.add_url_rule("/test/protected-format", "protected_format", protected)

    response = client.get(
        "/test/protected-format", headers={"Authorization": "Bearer"}
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid token format"


def test_token_required_invalid_token(client, app):
    @token_required
    def protected():
        return jsonify({"ok": True}), 200

    app.add_url_rule("/test/protected-invalid", "protected_invalid", protected)

    response = client.get(
        "/test/protected-invalid", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "Token is invalid or expired"


def test_role_required_branches(client, app):
    @role_required("trainer")
    def role_only():
        return jsonify({"ok": True}), 200

    @token_required
    @role_required("trainer")
    def role_protected():
        return jsonify({"ok": True}), 200

    app.add_url_rule("/test/role-only", "role_only", role_only)
    app.add_url_rule("/test/role-protected", "role_protected", role_protected)

    response = client.get("/test/role-only")
    assert response.status_code == 403
    assert response.get_json()["error"] == "Insufficient permissions"

    with app.app_context():
        trainee_token = generate_token(1, "trainee")
        trainer_token = generate_token(2, "trainer")

    response = client.get(
        "/test/role-protected",
        headers={"Authorization": f"Bearer {trainee_token}"},
    )
    assert response.status_code == 403

    response = client.get(
        "/test/role-protected",
        headers={"Authorization": f"Bearer {trainer_token}"},
    )
    assert response.status_code == 200
