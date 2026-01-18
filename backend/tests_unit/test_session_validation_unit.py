from controllers import session_controller


class DummyClientQuery:
    def __init__(self, existing_ids):
        self._existing_ids = set(existing_ids)
        self._last_id = None

    def filter_by(self, **kwargs):
        self._last_id = kwargs.get("id")
        return self

    def first(self):
        if self._last_id in self._existing_ids:
            return object()
        return None


class DummyProgramQuery:
    def __init__(self, existing_ids):
        self._existing_ids = set(existing_ids)

    def get(self, program_id):
        if program_id in self._existing_ids:
            program = type("Program", (), {})()
            program.client_id = {10: 1, 20: 2}.get(program_id)
            program.trainer_id = 99
            return program
        return None


class DummyClientModel:
    def __init__(self, query):
        self.query = query


class DummyProgramModel:
    def __init__(self, query):
        self.query = query


def _base_payload():
    return {"client_ids": [1, 2], "program_ids": [10, 20]}


def _patch_queries(monkeypatch, client_ids, program_ids):
    monkeypatch.setattr(
        session_controller,
        "Client",
        DummyClientModel(DummyClientQuery(existing_ids=client_ids)),
    )
    monkeypatch.setattr(
        session_controller,
        "Program",
        DummyProgramModel(DummyProgramQuery(existing_ids=program_ids)),
    )


def test_validate_session_data_requires_clients_and_programs(monkeypatch):
    _patch_queries(monkeypatch, client_ids=set(), program_ids=set())
    payload = {"client_ids": [], "program_ids": []}
    errors = session_controller.validate_session_data(payload)
    assert "At least 1 client is required" in errors
    assert "Each selected client must have a program assigned" in errors


def test_validate_session_data_rejects_too_many_clients(monkeypatch):
    _patch_queries(monkeypatch, client_ids={1, 2, 3, 4, 5}, program_ids={10, 11, 12, 13, 14})
    payload = {"client_ids": [1, 2, 3, 4, 5], "program_ids": [10, 11, 12, 13, 14]}
    errors = session_controller.validate_session_data(payload)
    assert "Maximum 4 clients allowed" in errors


def test_validate_session_data_requires_matching_programs(monkeypatch):
    _patch_queries(monkeypatch, client_ids={1, 2}, program_ids={10})
    payload = {"client_ids": [1, 2], "program_ids": [10]}
    errors = session_controller.validate_session_data(payload)
    assert "Each selected client must have a program assigned" in errors


def test_validate_session_data_flags_missing_clients(monkeypatch):
    _patch_queries(monkeypatch, client_ids={1}, program_ids={10, 20})
    payload = _base_payload()
    errors = session_controller.validate_session_data(payload)
    assert "Client ID 2 not found" in errors


def test_validate_session_data_flags_missing_programs(monkeypatch):
    _patch_queries(monkeypatch, client_ids={1, 2}, program_ids={10})
    payload = _base_payload()
    errors = session_controller.validate_session_data(payload)
    assert "Program ID 20 not found" in errors


def test_validate_session_data_accepts_valid_payload(monkeypatch):
    _patch_queries(monkeypatch, client_ids={1, 2}, program_ids={10, 20})
    payload = _base_payload()
    errors = session_controller.validate_session_data(payload)
    assert errors == []


def test_validate_session_data_rejects_program_mismatch(monkeypatch):
    _patch_queries(monkeypatch, client_ids={1, 2}, program_ids={10, 20})
    payload = {"client_ids": [2, 1], "program_ids": [10, 20]}
    errors = session_controller.validate_session_data(payload)
    assert "Program ID 10 is not assigned to Client ID 2" in errors
