from utils.validation import validate_client_create_payload, validate_client_update_payload


def test_validate_client_create_missing_name():
    payload = {
        "age": 25,
        "fitness_level": "Beginner",
        "goals": "Improve overall strength",
    }
    assert validate_client_create_payload(payload) == "Name must be 2-50 characters"


def test_validate_client_create_name_too_short():
    payload = {
        "name": "A",
        "age": 25,
        "fitness_level": "Beginner",
        "goals": "Improve overall strength",
    }
    assert validate_client_create_payload(payload) == "Name must be 2-50 characters"


def test_validate_client_create_name_too_long():
    payload = {
        "name": "A" * 51,
        "age": 25,
        "fitness_level": "Beginner",
        "goals": "Improve overall strength",
    }
    assert validate_client_create_payload(payload) == "Name must be 2-50 characters"


def test_validate_client_create_age_too_low():
    payload = {
        "name": "Client One",
        "age": 15,
        "fitness_level": "Beginner",
        "goals": "Improve overall strength",
    }
    assert validate_client_create_payload(payload) == "Age must be between 16 and 100"


def test_validate_client_create_age_too_high():
    payload = {
        "name": "Client One",
        "age": 101,
        "fitness_level": "Beginner",
        "goals": "Improve overall strength",
    }
    assert validate_client_create_payload(payload) == "Age must be between 16 and 100"


def test_validate_client_create_invalid_fitness_level():
    payload = {
        "name": "Client One",
        "age": 30,
        "fitness_level": "Expert",
        "goals": "Improve overall strength",
    }
    assert validate_client_create_payload(payload) == "Invalid fitness level"


def test_validate_client_create_goals_too_short():
    payload = {
        "name": "Client One",
        "age": 30,
        "fitness_level": "Beginner",
        "goals": "Too short",
    }
    assert validate_client_create_payload(payload) == "Goals must be at least 10 characters"


def test_validate_client_create_valid():
    payload = {
        "name": "Client One",
        "age": 30,
        "fitness_level": "Beginner",
        "goals": "Improve overall strength",
    }
    assert validate_client_create_payload(payload) is None


def test_validate_client_update_name_too_short():
    assert validate_client_update_payload({"name": "A"}) == "Name must be 2-50 characters"


def test_validate_client_update_name_too_long():
    assert validate_client_update_payload({"name": "A" * 51}) == "Name must be 2-50 characters"


def test_validate_client_update_age_too_low():
    assert validate_client_update_payload({"age": 10}) == "Age must be between 16 and 100"


def test_validate_client_update_age_too_high():
    assert validate_client_update_payload({"age": 120}) == "Age must be between 16 and 100"


def test_validate_client_update_invalid_fitness_level():
    assert validate_client_update_payload({"fitness_level": "Expert"}) == "Invalid fitness level"


def test_validate_client_update_goals_too_short():
    assert validate_client_update_payload({"goals": "Short"}) == "Goals must be at least 10 characters"


def test_validate_client_update_valid_fields():
    payload = {
        "name": "Updated Name",
        "age": 35,
        "fitness_level": "Intermediate",
        "goals": "Train consistently and improve",
    }
    assert validate_client_update_payload(payload) is None


def test_validate_client_update_no_fields():
    assert validate_client_update_payload({}) is None
