from datetime import timedelta
import sys
from pathlib import Path

import pytest
from flask import Flask

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


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
