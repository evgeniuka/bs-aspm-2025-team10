import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app

def generate_token(user_id, role):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.utcnow()
    } 
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    """Вспомогательная функция для расшифровки"""
    try:
        return jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=["HS256"],
        )
    except Exception:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header == "Bearer":
                return jsonify({'error': 'Invalid token format'}), 401
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]
                if not token:
                    return jsonify({'error': 'Invalid token format'}), 401
            else:
                token = auth_header

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
           
            data = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithms=["HS256"]
)
            request.user_id = data.get('user_id')
            request.user_role = data.get('role')  
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        except Exception:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        return f(*args, **kwargs)
    return decorated


def role_required(required_role):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user_role') or request.user_role != required_role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
