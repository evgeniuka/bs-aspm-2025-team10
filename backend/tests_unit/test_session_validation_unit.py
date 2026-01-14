import types

import pytest

from controllers import session_controller


def _patch_client_query(monkeypatch, existing_ids):
    class DummyQuery:
        def __init__(self):
            self._client_id = None

        def filter_by(self, id):
            self._client_id = id
            return self

        def first(self):
            if self._client_id in existing_ids:
                return types.SimpleNamespace(id=self._client_id)
            return None

    class DummyClient:
        query = DummyQuery()

    monkeypatch.setattr(session_controller, "Client", DummyClient)


def _patch_program_get(monkeypatch, existing_ids):
    def fake_get(model, program_id):
        if program_id in existing_ids:
            return types.SimpleNamespace(id=program_id)
        return None

    monkeypatch.setattr(session_controller.db, "session", types.SimpleNamespace(get=fake_get))


def test_validate_session_data_requires_min_clients(monkeypatch):
    _patch_client_query(monkeypatch, existing_ids={1})
    _patch_program_get(monkeypatch, existing_ids={10})

    errors = session_controller.validate_session_data({"client_ids": [1], "program_ids": [10]})

    assert "At least 2 clients are required" in errors


def test_validate_session_data_limits_max_clients(monkeypatch):
    _patch_client_query(monkeypatch, existing_ids={1, 2, 3, 4, 5})
    _patch_program_get(monkeypatch, existing_ids={10, 11, 12, 13, 14})

    errors = session_controller.validate_session_data(
        {"client_ids": [1, 2, 3, 4, 5], "program_ids": [10, 11, 12, 13, 14]}
    )

    assert "Maximum 4 clients allowed" in errors


def test_validate_session_data_requires_program_per_client(monkeypatch):
    _patch_client_query(monkeypatch, existing_ids={1, 2})
    _patch_program_get(monkeypatch, existing_ids={10})

    errors = session_controller.validate_session_data({"client_ids": [1, 2], "program_ids": [10]})

    assert "Each selected client must have a program assigned" in errors


def test_validate_session_data_missing_client(monkeypatch):
    _patch_client_query(monkeypatch, existing_ids={1})
    _patch_program_get(monkeypatch, existing_ids={10, 11})

    errors = session_controller.validate_session_data({"client_ids": [1, 2], "program_ids": [10, 11]})

    assert "Client ID 2 not found" in errors


def test_validate_session_data_missing_program(monkeypatch):
    _patch_client_query(monkeypatch, existing_ids={1, 2})
    _patch_program_get(monkeypatch, existing_ids={10})

    errors = session_controller.validate_session_data({"client_ids": [1, 2], "program_ids": [10, 11]})

    assert "Program ID 11 not found" in errors


def test_validate_session_data_success(monkeypatch):
    _patch_client_query(monkeypatch, existing_ids={1, 2})
    _patch_program_get(monkeypatch, existing_ids={10, 11})

    errors = session_controller.validate_session_data({"client_ids": [1, 2], "program_ids": [10, 11]})

    assert errors == []
