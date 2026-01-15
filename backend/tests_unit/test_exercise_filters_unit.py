from utils.validation import parse_exercise_filters


def test_parse_exercise_filters_trims_search():
    class DummyArgs(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    args = DummyArgs({"search": "  Push Up  "})
    search, category, equipment, difficulty = parse_exercise_filters(args)

    assert search == "Push Up"
    assert category is None
    assert equipment is None
    assert difficulty is None


def test_parse_exercise_filters_defaults():
    class DummyArgs(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    search, category, equipment, difficulty = parse_exercise_filters(DummyArgs())

    assert search == ""
    assert category is None
    assert equipment is None
    assert difficulty is None


def test_parse_exercise_filters_returns_category_equipment_and_difficulty():
    class DummyArgs(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    args = DummyArgs({"category": "core", "equipment": "barbell", "difficulty": "beginner"})
    search, category, equipment, difficulty = parse_exercise_filters(args)

    assert search == ""
    assert category == "core"
    assert equipment == "barbell"
    assert difficulty == "beginner"
