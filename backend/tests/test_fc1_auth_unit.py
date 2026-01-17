from models.user import User


def test_password_hashing_and_verification():
    user = User(
        email="unit@example.com",
        full_name="Unit Test",
        role="trainer",
        is_active=True,
    )
    user.set_password("StrongPass123")

    assert user.check_password("StrongPass123") is True
    assert user.check_password("WrongPass") is False
