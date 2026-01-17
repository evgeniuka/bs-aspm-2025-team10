import pytest

from models import db
from models.exercise import Exercise
from utils.jwt_utils import generate_token


def create_exercise(name, category="upper_body", equipment="barbell", difficulty="beginner"):
    exercise = Exercise(
        name=name,
        category=category,
        description=f"{name} description",
        equipment=equipment,
        difficulty=difficulty,
    )
    db.session.add(exercise)
    db.session.commit()
    return exercise


def _json_list(response):
    assert response.is_json is True
    data = response.get_json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("exercises", "items", "results", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    pytest.fail(f"Unexpected JSON shape: {type(data)} -> {data}")


def _names(items):
    return {item["name"] for item in items}


def _assert_exercise_payload(item):
    assert set(item.keys()) == {
        "id",
        "name",
        "category",
        "description",
        "equipment",
        "difficulty",
    }
    assert isinstance(item["id"], int)
    assert isinstance(item["name"], str)
    assert isinstance(item["category"], str)
    assert isinstance(item["description"], str)
    assert isinstance(item["equipment"], str)
    assert isinstance(item["difficulty"], str)


def _make_token(user_id=1, role="trainer"):
    return generate_token(user_id=user_id, role=role)


def test_get_exercises_empty_returns_list(client):
    response = client.get("/api/exercises")

    assert response.status_code == 200
    data = _json_list(response)
    assert data == []


def test_get_exercises_returns_all(client):
    create_exercise("Push Up", category="upper_body", equipment="bodyweight", difficulty="beginner")
    create_exercise("Plank", category="core", equipment="bodyweight", difficulty="intermediate")

    response = client.get("/api/exercises")

    assert response.status_code == 200
    data = _json_list(response)
    assert _names(data) == {"Push Up", "Plank"}
    for item in data:
        _assert_exercise_payload(item)
    assert Exercise.query.count() == 2


def test_get_exercises_search_empty_query_returns_all(client):
    create_exercise("Squat", category="lower_body", equipment="barbell", difficulty="beginner")
    create_exercise("Lunge", category="lower_body", equipment="bodyweight", difficulty="beginner")

    response = client.get("/api/exercises?search=")

    assert response.status_code == 200
    data = _json_list(response)
    assert _names(data) == {"Squat", "Lunge"}


def test_get_exercises_search_filters_case_insensitive(client):
    create_exercise("Push Up", category="upper_body", equipment="bodyweight", difficulty="beginner")
    create_exercise("Pull Up", category="upper_body", equipment="bodyweight", difficulty="advanced")
    create_exercise("Squat", category="lower_body", equipment="barbell", difficulty="beginner")

    resp = client.get("/api/exercises?search=PuSh")
    assert resp.status_code == 200
    items = _json_list(resp)
    names = _names(items)

    assert names == {"Push Up"}


def test_get_exercises_search_squat_variations(client):
    create_exercise("Front Squat", category="lower_body", equipment="barbell", difficulty="intermediate")
    create_exercise("Goblet Squat", category="lower_body", equipment="dumbbell", difficulty="beginner")
    create_exercise("Push Up", category="upper_body", equipment="bodyweight", difficulty="beginner")

    resp = client.get("/api/exercises?search=squat")
    assert resp.status_code == 200
    items = _json_list(resp)

    assert _names(items) == {"Front Squat", "Goblet Squat"}


def test_get_exercises_search_non_matching_returns_empty(client):
    create_exercise("Deadlift", category="lower_body", equipment="barbell", difficulty="advanced")

    resp = client.get("/api/exercises?search=bench")
    assert resp.status_code == 200
    items = _json_list(resp)

    assert items == []


def test_get_exercises_filters_by_category_and_difficulty(client):
    create_exercise("Bench Press", category="upper_body", equipment="barbell", difficulty="intermediate")
    create_exercise("Burpee", category="cardio", equipment="bodyweight", difficulty="beginner")
    create_exercise("Sit Up", category="core", equipment="bodyweight", difficulty="beginner")

    resp = client.get("/api/exercises?category=core&difficulty=beginner")
    assert resp.status_code == 200
    items = _json_list(resp)
    names = _names(items)

    assert names == {"Sit Up"}


def test_get_exercises_filters_by_equipment(client):
    create_exercise("Bench Press", category="upper_body", equipment="barbell", difficulty="intermediate")
    create_exercise("Goblet Squat", category="lower_body", equipment="dumbbell", difficulty="beginner")
    create_exercise("Plank", category="core", equipment="bodyweight", difficulty="beginner")

    resp = client.get("/api/exercises?equipment=barbell")
    assert resp.status_code == 200
    items = _json_list(resp)

    assert _names(items) == {"Bench Press"}


@pytest.mark.parametrize(
    ("query", "error"),
    [
        ("category=invalid", "Invalid category filter"),
        ("equipment=invalid", "Invalid equipment filter"),
        ("difficulty=invalid", "Invalid difficulty filter"),
    ],
)
def test_get_exercises_invalid_filters_return_400(client, query, error):
    response = client.get(f"/api/exercises?{query}")

    assert response.status_code == 400
    assert response.get_json() == {"error": error}


def test_protected_route_requires_token(client):
    response = client.get("/test/protected")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Token is missing"}


def test_protected_route_rejects_malformed_authorization_header(client):
    response = client.get("/test/protected", headers={"Authorization": "Bearer"})

    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid token format"}


def test_protected_route_rejects_invalid_token(client):
    response = client.get("/test/protected", headers={"Authorization": "Bearer not-a-token"})

    assert response.status_code == 401
    assert response.get_json() == {"error": "Token is invalid or expired"}


def test_protected_route_allows_valid_token(client):
    token = _make_token(user_id=42, role="trainer")

    response = client.get("/test/protected", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.get_json() == {"ok": True, "user_id": 42, "role": "trainer"}


def test_role_required_rejects_wrong_role(client):
    token = _make_token(role="trainee")

    response = client.get("/test/admin", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.get_json() == {"error": "Insufficient permissions"}


def test_post_exercises_method_not_allowed(client):
    """
    If /api/exercises exists as GET-only resource, POST should be 405 (Method Not Allowed).
    We do NOT accept 404 here, because endpoint must exist for FC-3.
    """
    response = client.post("/api/exercises", json={"name": "New"})

    assert response.status_code == 405
