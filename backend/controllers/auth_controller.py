from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from utils.jwt_utils import generate_token, token_required
from utils.validation import validate_login_payload, validate_register_payload
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    Body: { "email": "trainer@example.com", "password": "password123" }
    """
    data = request.get_json()

    error = validate_login_payload(data)
    if error:
        return jsonify({'error': error}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    token = generate_token(user.id, user.role)
    print(f"Login attempt for: {data['email']}")
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200

    

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/auth/register
    Body: { "email": "...", "password": "...", "full_name": "...", "role": "trainer|trainee" }
    """
    data = request.get_json()

    error = validate_register_payload(data)
    if error:
        return jsonify({'error': error}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    user = User(
        email=data['email'],
        full_name=data['full_name'],
        role=data['role']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    token = generate_token(user.id, user.role)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 201

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    GET /api/auth/me
    Headers: { "Authorization": "Bearer <token>" }
    """
    user = User.query.get(request.user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    POST /api/auth/logout
    Note: JWT is stateless, so logout is handled client-side by removing token
    """
    return jsonify({'message': 'Logged out successfully'}), 200
