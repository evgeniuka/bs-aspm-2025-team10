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
    
    search, category, difficulty = parse_exercise_filters(request.args)
    if search:
        query = query.filter(Exercise.name.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    exercises = query.all()
    return jsonify([e.to_dict() for e in exercises]), 200
