import os
import sys
from pathlib import Path

TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL_TEST",
    "postgresql+psycopg2://admin:123@localhost:5432/fitnessClub_test",
)

if "fitnessClub" in TEST_DATABASE_URL and "fitnessClub_test" not in TEST_DATABASE_URL:
    raise RuntimeError("Refusing to run tests against non-test database.")

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from app import create_app
from models.user import db


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
def clean_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_session(app):
    with app.app_context():
        yield db.session
