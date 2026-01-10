import os
import sys
import pytest

# Skip if no test DB configured
if not os.getenv("DATABASE_URL_TEST"):
    pytest.skip("DATABASE_URL_TEST is not set", allow_module_level=True)

# App reads DATABASE_URL, so map it from DATABASE_URL_TEST
os.environ["DATABASE_URL"] = os.environ["DATABASE_URL_TEST"]

# Provide defaults so create_app won't crash if these are required
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")

# Ensure backend/ is importable in CI and locally
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app
from models import db
from models.exercise import Exercise


@pytest.fixture()
def app_client():
    app, _socketio = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

    with app.test_client() as client:
        yield app, client

    with app.app_context():
        db.session.remove()
        db.drop_all()


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


def test_get_exercises_empty_returns_list(app_client):
    _app, client = app_client

    response = client.get("/api/exercises")

    assert response.status_code == 200
    data = _json_list(response)
    assert data == []


def test_get_exercises_returns_all(app_client):
    app, client = app_client

    with app.app_context():
        create_exercise("Push Up", category="upper_body", equipment="bodyweight", difficulty="beginner")
        create_exercise("Plank", category="core", equipment="bodyweight", difficulty="intermediate")

    response = client.get("/api/exercises")

    assert response.status_code == 200
    data = _json_list(response)
    assert _names(data) == {"Push Up", "Plank"}


def test_get_exercises_search_empty_query_returns_all(app_client):
    app, client = app_client

    with app.app_context():
        create_exercise("Squat", category="lower_body", equipment="barbell", difficulty="beginner")
        create_exercise("Lunge", category="lower_body", equipment="bodyweight", difficulty="beginner")

    response = client.get("/api/exercises?search=")

    assert response.status_code == 200
    data = _json_list(response)
    assert _names(data) == {"Squat", "Lunge"}


def test_get_exercises_search_filters_case_insensitive_or_is_ignored(app_client):
    """
    If backend implements `search`, it must filter case-insensitively.
    If backend ignores unknown query params, it should still return 200 and include matching items.
    """
    app, client = app_client

    with app.app_context():
        create_exercise("Push Up", category="upper_body", equipment="bodyweight", difficulty="beginner")
        create_exercise("Pull Up", category="upper_body", equipment="bodyweight", difficulty="advanced")
        create_exercise("Squat", category="lower_body", equipment="barbell", difficulty="beginner")

    all_resp = client.get("/api/exercises")
    assert all_resp.status_code == 200
    all_items = _json_list(all_resp)
    all_names = _names(all_items)

    resp = client.get("/api/exercises?search=PuSh")
    assert resp.status_code == 200
    items = _json_list(resp)
    names = _names(items)

    # Must at least include the matching exercise
    assert "Push Up" in names

    # If filtering actually happens (result got smaller), enforce exact match
    if len(names) < len(all_names):
        assert names == {"Push Up"}


def test_get_exercises_search_non_matching_returns_empty_or_is_ignored(app_client):
    """
    If backend implements `search`, non-matching query should return empty list.
    If backend ignores `search`, it should still return 200 (then list will be non-empty).
    """
    app, client = app_client

    with app.app_context():
        create_exercise("Deadlift", category="lower_body", equipment="barbell", difficulty="advanced")

    all_resp = client.get("/api/exercises")
    assert all_resp.status_code == 200
    all_items = _json_list(all_resp)
    all_names = _names(all_items)

    resp = client.get("/api/exercises?search=bench")
    assert resp.status_code == 200
    items = _json_list(resp)
    names = _names(items) if items else set()

    # If search is implemented, expect empty result
    if len(names) < len(all_names):
        assert items == []
    else:
        # Search is likely ignored; at least ensure response is valid and includes existing data
        assert "Deadlift" in names


def test_get_exercises_filters_by_category_and_difficulty_or_is_ignored(app_client):
    """
    If backend implements category/difficulty filters, it must return only matching items.
    If backend ignores these params, it should still return 200 and include matching items.
    """
    app, client = app_client

    with app.app_context():
        create_exercise("Bench Press", category="upper_body", equipment="barbell", difficulty="intermediate")
        create_exercise("Burpee", category="cardio", equipment="bodyweight", difficulty="beginner")
        create_exercise("Sit Up", category="core", equipment="bodyweight", difficulty="beginner")

    all_resp = client.get("/api/exercises")
    assert all_resp.status_code == 200
    all_items = _json_list(all_resp)
    all_names = _names(all_items)

    resp = client.get("/api/exercises?category=core&difficulty=beginner")
    assert resp.status_code == 200
    items = _json_list(resp)
    names = _names(items)

    # Must at least include the matching item
    assert "Sit Up" in names

    # If filtering actually happens (result got smaller), enforce exact match
    if len(names) < len(all_names):
        assert names == {"Sit Up"}


def test_post_exercises_not_allowed(app_client):
    _app, client = app_client

    response = client.post("/api/exercises", json={"name": "New"})

    assert response.status_code in (404, 405)


def test_get_exercise_by_id_not_found(app_client):
    _app, client = app_client

    response = client.get("/api/exercises/1")

    assert response.status_code in (404, 405)


def test_put_exercise_by_id_not_found(app_client):
    _app, client = app_client

    response = client.put("/api/exercises/1", json={"name": "Update"})

    assert response.status_code in (404, 405)


def test_patch_exercise_by_id_not_found(app_client):
    _app, client = app_client

    response = client.patch("/api/exercises/1", json={"name": "Update"})

    assert response.status_code in (404, 405)


def test_delete_exercise_by_id_not_found(app_client):
    _app, client = app_client

    response = client.delete("/api/exercises/1")

    assert response.status_code in (404, 405)  # ok: endpoint does not exist - так лучше?
