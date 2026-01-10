import os
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app
from models import db


@pytest.fixture
def app():
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key")
    os.environ.setdefault("FLASK_ENV", "testing")

    database_url = os.getenv("DATABASE_URL_TEST") or os.getenv("DATABASE_URL")
    if database_url:
        os.environ["DATABASE_URL"] = database_url

    app, _ = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()
