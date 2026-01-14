from types import SimpleNamespace

from controllers.client_controller import (
    resolve_client_user_id,
    validate_client_payload,
    validate_client_update_payload,
)
from controllers import client_controller


class DummyQuery:
    def __init__(self, user=None):
        self._user = user
        self.filters = None

    def filter_by(self, **kwargs):
        self.filters = kwargs
        return self

    def first(self):
        return self._user


def test_validate_client_payload_missing_name():
    data = {
        "age": 25,
        "fitness_level": "Beginner",
        "goals": "Improve overall fitness"
    }
    assert validate_client_payload(data) == "Name must be 2-50 characters"


def test_validate_client_payload_name_too_short():
    data = {
        "name": "A",
        "age": 25,
        "fitness_level": "Beginner",
        "goals": "Improve overall fitness"
    }
    assert validate_client_payload(data) == "Name must be 2-50 characters"


def test_validate_client_payload_invalid_age_low():
    data = {
        "name": "Alex",
        "age": 15,
        "fitness_level": "Beginner",
        "goals": "Improve overall fitness"
    }
    assert validate_client_payload(data) == "Age must be between 16 and 100"


def test_validate_client_payload_invalid_fitness_level():
    data = {
        "name": "Alex",
        "age": 25,
        "fitness_level": "Expert",
        "goals": "Improve overall fitness"
    }
    assert validate_client_payload(data) == "Invalid fitness level"


def test_validate_client_payload_short_goals():
    data = {
        "name": "Alex",
        "age": 25,
        "fitness_level": "Beginner",
        "goals": "Too short"
    }
    assert validate_client_payload(data) == "Goals must be at least 10 characters"


def test_validate_client_payload_success():
    data = {
        "name": "Alex",
        "age": 25,
        "fitness_level": "Intermediate",
        "goals": "Improve overall fitness"
    }
    assert validate_client_payload(data) is None


def test_validate_client_update_payload_invalid_name():
    data = {"name": "Z"}
    assert validate_client_update_payload(data) == "Name must be 2-50 characters"


def test_validate_client_update_payload_invalid_age():
    data = {"age": 101}
    assert validate_client_update_payload(data) == "Age must be between 16 and 100"


def test_validate_client_update_payload_invalid_fitness_level():
    data = {"fitness_level": "Expert"}
    assert validate_client_update_payload(data) == "Invalid fitness level"


def test_validate_client_update_payload_invalid_goals():
    data = {"goals": "Short"}
    assert validate_client_update_payload(data) == "Goals must be at least 10 characters"


def test_validate_client_update_payload_success():
    data = {"name": "Valid Name", "age": 30}
    assert validate_client_update_payload(data) is None


def test_resolve_client_user_id_returns_none_without_email():
    assert resolve_client_user_id(None) is None


def test_resolve_client_user_id_returns_none_for_missing_user(monkeypatch):
    monkeypatch.setattr(client_controller.User, "query", DummyQuery())
    assert resolve_client_user_id("missing@example.com") is None


def test_resolve_client_user_id_returns_none_for_non_trainee(monkeypatch):
    user = SimpleNamespace(id=10, role="trainer")
    monkeypatch.setattr(client_controller.User, "query", DummyQuery(user))
    assert resolve_client_user_id("trainer@example.com") is None


def test_resolve_client_user_id_returns_id_for_trainee(monkeypatch):
    user = SimpleNamespace(id=12, role="trainee")
    monkeypatch.setattr(client_controller.User, "query", DummyQuery(user))
    assert resolve_client_user_id("trainee@example.com") == 12
