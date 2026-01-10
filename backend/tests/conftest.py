import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def _test_environment():
    # Ensure tests don't get silently skipped in CI
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key")

    # If app uses DATABASE_URL but tests use DATABASE_URL_TEST
    if "DATABASE_URL" not in os.environ and "DATABASE_URL_TEST" in os.environ:
        os.environ["DATABASE_URL"] = os.environ["DATABASE_URL_TEST"]
