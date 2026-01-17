from flask import Blueprint, request, jsonify
from models import db
from models.exercise import Exercise
from utils.validation import parse_exercise_filters

exercise_bp = Blueprint('exercise', __name__, url_prefix='/api/exercises')

@exercise_bp.route('', methods=['GET'])
def get_exercises():
    """
    GET /api/exercises
    Query params:
    - search: string (case-insensitive substring match on name)
    - category: string (exact match)
    - difficulty: string (exact match)
    """
    query = Exercise.query
    search, category, equipment, difficulty = parse_exercise_filters(request.args)

    valid_categories = {"upper_body", "lower_body", "core", "cardio", "full_body"}
    valid_equipment = {
        "bodyweight",
        "barbell",
        "dumbbell",
        "machine",
        "cable",
        "kettlebell",
        "other",
    }
    valid_difficulty = {"beginner", "intermediate", "advanced"}

    if search:
        query = query.filter(Exercise.name.ilike(f'%{search}%'))

    if category:
        if category not in valid_categories:
            return jsonify({"error": "Invalid category filter"}), 400
        query = query.filter_by(category=category)

    if equipment:
        if equipment not in valid_equipment:
            return jsonify({"error": "Invalid equipment filter"}), 400
        query = query.filter_by(equipment=equipment)

    if difficulty:
        if difficulty not in valid_difficulty:
            return jsonify({"error": "Invalid difficulty filter"}), 400
        query = query.filter_by(difficulty=difficulty)
    
    exercises = query.all()
    return jsonify([e.to_dict() for e in exercises]), 200
