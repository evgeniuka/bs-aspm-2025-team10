import os

import pytest

if "DATABASE_URL_TEST" not in os.environ:
    raise RuntimeError("DATABASE_URL_TEST must be set for tests.")

os.environ["DATABASE_URL"] = os.environ["DATABASE_URL_TEST"]

from app import create_app  # noqa: E402
from models import db  # noqa: E402
from models.user import User  # noqa: E402
from utils.jwt_utils import generate_token  # noqa: E402


@pytest.fixture
def app():
    app, _ = create_app()
    app.config.update(TESTING=True)

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def trainer_token(app):
    with app.app_context():
        user = User(
            email="trainer@example.com",
            full_name="Test Trainer",
            role="trainer",
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.id, user.role)
        return {"user_id": user.id, "token": token}
