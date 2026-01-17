def validate_login_payload(data):
    if not data or not data.get("email") or not data.get("password"):
        return "Email and password are required"
    return None


def validate_register_payload(data):
    if not data:
        return "Missing required fields"
    required_fields = ["email", "password", "full_name", "role"]
    if not all(field in data for field in required_fields):
        return "Missing required fields"
    if data["role"] not in ["trainer", "trainee"]:
        return "Invalid role. Must be trainer or trainee"
    if len(data["password"]) < 8:
        return "Password must be at least 8 characters long"
    return None


def validate_client_create_payload(data):
    if not data.get("name") or len(data["name"]) < 2 or len(data["name"]) > 50:
        return "Name must be 2-50 characters"
    if not (16 <= data.get("age", 0) <= 100):
        return "Age must be between 16 and 100"
    if data.get("fitness_level") not in ["Beginner", "Intermediate", "Advanced"]:
        return "Invalid fitness level"
    if not data.get("goals") or len(data["goals"]) < 10:
        return "Goals must be at least 10 characters"
    return None


def validate_client_update_payload(data):
    if "name" in data:
        if len(data["name"]) < 2 or len(data["name"]) > 50:
            return "Name must be 2-50 characters"
    if "age" in data:
        if not (16 <= data["age"] <= 100):
            return "Age must be between 16 and 100"
    if "fitness_level" in data:
        if data["fitness_level"] not in ["Beginner", "Intermediate", "Advanced"]:
            return "Invalid fitness level"
    if "goals" in data:
        if len(data["goals"]) < 10:
            return "Goals must be at least 10 characters"
    return None


def parse_exercise_filters(args):
    search = args.get("search", "").strip()
    category = args.get("category")
    equipment = args.get("equipment")
    difficulty = args.get("difficulty")
    return search, category, equipment, difficulty
