import os
import sys
from pathlib import Path

import pytest
from flask import jsonify, request

_db_url = os.getenv("DATABASE_URL_TEST") or os.getenv("DATABASE_URL")
if not _db_url:
    raise RuntimeError(
        "DATABASE_URL_TEST or DATABASE_URL must be set for FC-3 tests. "
        "CI should provide DATABASE_URL_TEST."
    )

os.environ["DATABASE_URL"] = _db_url
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ.setdefault("FLASK_ENV", "testing")

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from models import db
from utils.jwt_utils import role_required, token_required


@pytest.fixture()
def app_client():
    app, _socketio = create_app()
    app.config["TESTING"] = True

    @app.route("/test/protected", methods=["GET"])
    @token_required
    def protected_test_route():
        return jsonify(
            {"ok": True, "user_id": request.user_id, "role": request.user_role}
        ), 200

    @app.route("/test/admin", methods=["GET"])
    @token_required
    @role_required("trainer")
    def admin_test_route():
        return jsonify({"ok": True, "role": request.user_role}), 200

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

    with app.test_client() as client:
        yield app, client

    with app.app_context():
        db.session.remove()
        db.drop_all()
