from controllers.auth_controller import validate_login_data, validate_register_data


def test_validate_login_data_requires_payload():
    assert validate_login_data(None) == "Email and password are required"


def test_validate_login_data_requires_email():
    assert validate_login_data({"password": "Secretpass1"}) == "Email and password are required"


def test_validate_login_data_requires_password():
    assert validate_login_data({"email": "user@example.com"}) == "Email and password are required"


def test_validate_login_data_rejects_non_string_email():
    assert (
        validate_login_data({"email": 123, "password": "Secretpass1"})
        == "Email and password are required"
    )


def test_validate_login_data_rejects_non_string_password():
    assert (
        validate_login_data({"email": "user@example.com", "password": 123})
        == "Email and password are required"
    )


def test_validate_login_data_accepts_valid_payload():
    assert validate_login_data({"email": "user@example.com", "password": "Secretpass1"}) is None


def test_validate_register_data_requires_payload():
    assert validate_register_data(None) == "Missing required fields"


def test_validate_register_data_requires_all_fields():
    assert (
        validate_register_data({"email": "user@example.com", "password": "Secretpass1"})
        == "Missing required fields"
    )


def test_validate_register_data_rejects_invalid_role():
    assert (
        validate_register_data(
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
        validate_register_data(
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
        validate_register_data(
            {
                "email": "user@example.com",
                "password": "short",
                "full_name": "Test User",
                "role": "trainer",
            }
        )
        == "Password must be at least 8 characters long"
    )


def test_validate_register_data_rejects_non_string_password():
    assert (
        validate_register_data(
            {
                "email": "user@example.com",
                "password": 12345678,
                "full_name": "Test User",
                "role": "trainer",
            }
        )
        == "Password must be at least 8 characters long"
    )


def test_validate_register_data_accepts_valid_payload():
    assert (
        validate_register_data(
            {
                "email": "user@example.com",
                "password": "Secretpass1",
                "full_name": "Test User",
                "role": "trainer",
            }
        )
        is None
    )
