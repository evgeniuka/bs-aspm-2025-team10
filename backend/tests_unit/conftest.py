from datetime import timedelta

import pytest
from flask import Flask


@pytest.fixture()
def app():
    flask_app = Flask(__name__)
    flask_app.config.update(
        {
            "TESTING": True,
            "JWT_SECRET_KEY": "unit-test-secret",
            "JWT_ACCESS_TOKEN_EXPIRES": timedelta(minutes=5),
        }
    )
    return flask_app
