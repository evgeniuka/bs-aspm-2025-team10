from models.user import User
from utils.jwt_utils import decode_token, generate_token


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


def test_generate_and_decode_token(app):
    with app.app_context():
        token = generate_token(user_id=42, role="trainer")
        payload = decode_token(token)

    assert payload is not None
    assert payload["user_id"] == 42
    assert payload["role"] == "trainer"
