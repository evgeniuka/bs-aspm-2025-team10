from utils.validation import validate_login_payload, validate_register_payload


def test_validate_login_data_requires_payload():
    assert validate_login_payload(None) == "Email and password are required"


def test_validate_login_data_requires_email():
    assert validate_login_payload({"password": "Secretpass1"}) == "Email and password are required"


def test_validate_login_data_requires_password():
    assert validate_login_payload({"email": "user@example.com"}) == "Email and password are required"


def test_validate_login_data_accepts_valid_payload():
    assert (
        validate_login_payload({"email": "user@example.com", "password": "Secretpass1"}) is None
    )


def test_validate_register_data_requires_payload():
    assert validate_register_payload(None) == "Missing required fields"


def test_validate_register_data_requires_all_fields():
    assert (
        validate_register_payload({"email": "user@example.com", "password": "Secretpass1"})
        == "Missing required fields"
    )


def test_validate_register_data_rejects_invalid_role():
    assert (
        validate_register_payload(
            {
                "email": "user@example.com",
                "password": "Secretpass1",
                "full_name": "Test User",
                "role": "manager",
            }
        )
        == "Invalid role. Must be trainer or trainee"
    )


def test_validate_register_data_rejects_non_string_role():
    assert (
        validate_register_payload(
            {
                "email": "user@example.com",
                "password": "Secretpass1",
                "full_name": "Test User",
                "role": 123,
            }
        )
        == "Invalid role. Must be trainer or trainee"
    )


def test_validate_register_data_rejects_short_password():
    assert (
        validate_register_payload(
            {
                "email": "user@example.com",
                "password": "short",
                "full_name": "Test User",
                "role": "trainer",
            }
        )
        == "Password must be at least 8 characters long"
    )


def test_validate_register_data_accepts_valid_payload():
    assert (
        validate_register_payload(
            {
                "email": "user@example.com",
                "password": "Secretpass1",
                "full_name": "Test User",
                "role": "trainer",
            }
        )
        is None
    )
