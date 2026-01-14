from utils.validation import validate_login_payload, validate_register_payload


def test_validate_login_payload_none_data():
    assert validate_login_payload(None) == "Email and password are required"


def test_validate_login_payload_empty_dict():
    assert validate_login_payload({}) == "Email and password are required"


def test_validate_login_payload_missing_email():
    assert validate_login_payload({"password": "password123"}) == "Email and password are required"


def test_validate_login_payload_missing_password():
    assert validate_login_payload({"email": "trainer@example.com"}) == "Email and password are required"


def test_validate_login_payload_blank_email():
    assert (
        validate_login_payload({"email": "", "password": "password123"})
        == "Email and password are required"
    )


def test_validate_login_payload_valid():
    assert (
        validate_login_payload({"email": "trainer@example.com", "password": "password123"})
        is None
    )


def test_validate_register_payload_missing_email():
    data = {"password": "password123", "full_name": "Trainer One", "role": "trainer"}
    assert validate_register_payload(data) == "Missing required fields"


def test_validate_register_payload_missing_full_name():
    data = {"email": "trainer@example.com", "password": "password123", "role": "trainer"}
    assert validate_register_payload(data) == "Missing required fields"


def test_validate_register_payload_missing_role():
    data = {"email": "trainer@example.com", "password": "password123", "full_name": "Trainer"}
    assert validate_register_payload(data) == "Missing required fields"


def test_validate_register_payload_invalid_role():
    data = {
        "email": "trainer@example.com",
        "password": "password123",
        "full_name": "Trainer One",
        "role": "admin",
    }
    assert validate_register_payload(data) == "Invalid role. Must be trainer or trainee"


def test_validate_register_payload_short_password():
    data = {
        "email": "trainer@example.com",
        "password": "short",
        "full_name": "Trainer One",
        "role": "trainer",
    }
    assert validate_register_payload(data) == "Password must be at least 8 characters long"


def test_validate_register_payload_valid():
    data = {
        "email": "trainer@example.com",
        "password": "password123",
        "full_name": "Trainer One",
        "role": "trainer",
    }
    assert validate_register_payload(data) is None
