import pytest

from models import db
from models.exercise import Exercise


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


def test_get_exercises_empty_returns_list(client):
    response = client.get("/api/exercises")

    assert response.status_code == 200
    data = _json_list(response)
    assert data == []


def test_get_exercises_returns_all(app, client):
    with app.app_context():
        create_exercise("Push Up", category="upper_body", equipment="bodyweight", difficulty="beginner")
        create_exercise("Plank", category="core", equipment="bodyweight", difficulty="intermediate")

    response = client.get("/api/exercises")

    assert response.status_code == 200
    data = _json_list(response)
    assert _names(data) == {"Push Up", "Plank"}
    for item in data:
        _assert_exercise_payload(item)
    with app.app_context():
        assert Exercise.query.count() == 2


def test_get_exercises_search_empty_query_returns_all(app, client):
    with app.app_context():
        create_exercise("Squat", category="lower_body", equipment="barbell", difficulty="beginner")
        create_exercise("Lunge", category="lower_body", equipment="bodyweight", difficulty="beginner")

    response = client.get("/api/exercises?search=")

    assert response.status_code == 200
    data = _json_list(response)
    assert _names(data) == {"Squat", "Lunge"}


def test_get_exercises_search_filters_case_insensitive(app, client):
    with app.app_context():
        create_exercise("Push Up", category="upper_body", equipment="bodyweight", difficulty="beginner")
        create_exercise("Pull Up", category="upper_body", equipment="bodyweight", difficulty="advanced")
        create_exercise("Squat", category="lower_body", equipment="barbell", difficulty="beginner")

    resp = client.get("/api/exercises?search=PuSh")
    assert resp.status_code == 200
    items = _json_list(resp)
    names = _names(items)

    assert names == {"Push Up"}


def test_get_exercises_search_squat_variations(app, client):
    with app.app_context():
        create_exercise("Front Squat", category="lower_body", equipment="barbell", difficulty="intermediate")
        create_exercise("Goblet Squat", category="lower_body", equipment="dumbbell", difficulty="beginner")
        create_exercise("Push Up", category="upper_body", equipment="bodyweight", difficulty="beginner")

    resp = client.get("/api/exercises?search=squat")
    assert resp.status_code == 200
    items = _json_list(resp)

    assert _names(items) == {"Front Squat", "Goblet Squat"}


def test_get_exercises_search_non_matching_returns_empty(app, client):
    with app.app_context():
        create_exercise("Deadlift", category="lower_body", equipment="barbell", difficulty="advanced")

    resp = client.get("/api/exercises?search=bench")
    assert resp.status_code == 200
    items = _json_list(resp)

    assert items == []


def test_get_exercises_filters_by_category_and_difficulty(app, client):
    with app.app_context():
        create_exercise("Bench Press", category="upper_body", equipment="barbell", difficulty="intermediate")
        create_exercise("Burpee", category="cardio", equipment="bodyweight", difficulty="beginner")
        create_exercise("Sit Up", category="core", equipment="bodyweight", difficulty="beginner")

    resp = client.get("/api/exercises?category=core&difficulty=beginner")
    assert resp.status_code == 200
    items = _json_list(resp)
    names = _names(items)

    assert names == {"Sit Up"}


def test_get_exercises_filters_by_equipment(app, client):
    with app.app_context():
        create_exercise("Bench Press", category="upper_body", equipment="barbell", difficulty="intermediate")
        create_exercise("Goblet Squat", category="lower_body", equipment="dumbbell", difficulty="beginner")
        create_exercise("Plank", category="core", equipment="bodyweight", difficulty="beginner")

    resp = client.get("/api/exercises?equipment=barbell")
    assert resp.status_code == 200
    items = _json_list(resp)

    assert _names(items) == {"Bench Press"}


def test_get_all_exercises_returns_seeded_set(app, client):
    with app.app_context():
        for idx in range(121):
            create_exercise(
                f"Exercise {idx}",
                category="lower_body",
                equipment="bodyweight",
                difficulty="beginner",
            )

    response = client.get("/api/exercises")

    assert response.status_code == 200
    data = _json_list(response)
    assert len(data) >= 120


def test_filter_by_category_alias_legs(app, client):
    with app.app_context():
        create_exercise("Squat", category="lower_body", equipment="barbell", difficulty="beginner")
        create_exercise("Bench Press", category="upper_body", equipment="barbell", difficulty="intermediate")

    resp = client.get("/api/exercises?category=Legs")
    assert resp.status_code == 200
    items = _json_list(resp)

    assert _names(items) == {"Squat"}


def test_search_exercises_returns_matching_names(app, client):
    with app.app_context():
        create_exercise("Bench Press", category="upper_body", equipment="barbell", difficulty="intermediate")
        create_exercise("Incline Bench Press", category="upper_body", equipment="barbell", difficulty="intermediate")
        create_exercise("Deadlift", category="lower_body", equipment="barbell", difficulty="advanced")

    resp = client.get("/api/exercises?search=bench press")
    assert resp.status_code == 200
    items = _json_list(resp)

    assert _names(items) == {"Bench Press", "Incline Bench Press"}


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
