import os
import sys
from pathlib import Path

from sqlalchemy.engine import make_url

TEST_DATABASE_URL = os.getenv("DATABASE_URL_TEST")
if not TEST_DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL_TEST environment variable must be set to a Postgres test database."
    )

try:
    parsed_url = make_url(TEST_DATABASE_URL)
except Exception as exc:
    raise RuntimeError(
        "DATABASE_URL_TEST must be a valid SQLAlchemy Postgres URL."
    ) from exc

if not parsed_url.drivername.startswith("postgresql"):
    raise RuntimeError("Tests require Postgres. DATABASE_URL_TEST must start with 'postgresql'.")

if parsed_url.database and "test" not in parsed_url.database:
    raise RuntimeError("Refusing to run tests against non-test database.")

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from flask import jsonify, request

from app import create_app
from models import db
from models.user import User
from utils.jwt_utils import generate_token, role_required, token_required


@pytest.fixture(scope="session")
def app():
    flask_app, _socketio = create_app()
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )

    @flask_app.route("/test/protected", methods=["GET"])
    @token_required
    def protected_test_route():
        return jsonify(
            {"ok": True, "user_id": request.user_id, "role": request.user_role}
        ), 200

    @flask_app.route("/test/admin", methods=["GET"])
    @token_required
    @role_required("trainer")
    def admin_test_route():
        return jsonify({"ok": True, "role": request.user_role}), 200

    with flask_app.app_context():
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()


@pytest.fixture(autouse=True)
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_session(app):
    with app.app_context():
        yield db.session


@pytest.fixture()
def trainer_token(app):
    with app.app_context():
        user = User(
            email="trainer.token@example.com",
            full_name="Trainer Token",
            role="trainer",
            is_active=True,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.id, user.role)
        return {"user_id": user.id, "token": token}
