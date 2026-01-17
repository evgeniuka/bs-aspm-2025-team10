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
from app import create_app
from models import db
from models.user import User
from utils.jwt_utils import generate_token


@pytest.fixture(scope="session")
def app():
    flask_app, _socketio = create_app()
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )

    with flask_app.app_context():
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture(autouse=True)
def clean_db(app_context):
    db.drop_all()
    db.create_all()
    yield
    db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_session(app):
    with app.app_context():
        yield db.session


@pytest.fixture()
def create_user(db_session):
    def _create_user(email, role, full_name="Test User", password="password123"):
        user = User(email=email, full_name=full_name, role=role)
        user.set_password(password)
        db_session.add(user)
        db_session.commit()
        return user

    return _create_user


@pytest.fixture()
def auth_headers():
    def _auth_headers(user):
        token = generate_token(user.id, user.role)
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers
