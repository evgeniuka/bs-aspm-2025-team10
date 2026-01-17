from utils.validation import validate_client_create_payload, validate_client_update_payload


def test_validate_client_payload_missing_name():
    data = {
        "age": 25,
        "fitness_level": "Beginner",
        "goals": "Improve overall fitness"
    }
    assert validate_client_create_payload(data) == "Name must be 2-50 characters"


def test_validate_client_payload_name_too_short():
    data = {
        "name": "A",
        "age": 25,
        "fitness_level": "Beginner",
        "goals": "Improve overall fitness"
    }
    assert validate_client_create_payload(data) == "Name must be 2-50 characters"


def test_validate_client_payload_invalid_age_low():
    data = {
        "name": "Alex",
        "age": 15,
        "fitness_level": "Beginner",
        "goals": "Improve overall fitness"
    }
    assert validate_client_create_payload(data) == "Age must be between 16 and 100"


def test_validate_client_payload_invalid_fitness_level():
    data = {
        "name": "Alex",
        "age": 25,
        "fitness_level": "Expert",
        "goals": "Improve overall fitness"
    }
    assert validate_client_create_payload(data) == "Invalid fitness level"


def test_validate_client_payload_short_goals():
    data = {
        "name": "Alex",
        "age": 25,
        "fitness_level": "Beginner",
        "goals": "Too short"
    }
    assert validate_client_create_payload(data) == "Goals must be at least 10 characters"


def test_validate_client_payload_success():
    data = {
        "name": "Alex",
        "age": 25,
        "fitness_level": "Intermediate",
        "goals": "Improve overall fitness"
    }
    assert validate_client_create_payload(data) is None


def test_validate_client_update_payload_invalid_name():
    data = {"name": "Z"}
    assert validate_client_update_payload(data) == "Name must be 2-50 characters"


def test_validate_client_update_payload_invalid_age():
    data = {"age": 101}
    assert validate_client_update_payload(data) == "Age must be between 1 6  and 100"


def test_validate_client_update_payload_invalid_fitness_level():
    data = {"fitness_level": "Expert"}
    assert validate_client_update_payload(data) == "Invalid fitness level"


def test_validate_client_update_payload_invalid_goals():
    data = {"goals": "Short"}
    assert validate_client_update_payload(data) == "Goals must be at least 10 characters"


def test_validate_client_update_payload_success():
    data = {"name": "Valid Name", "age": 30}
    assert validate_client_update_payload(data) is None
