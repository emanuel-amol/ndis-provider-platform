from flask import Blueprint, request, jsonify
from auth import authenticate_user, create_user
from middleware.security import log_security_event

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    result = authenticate_user(email, password)
    
    if result:
        log_security_event('LOGIN_SUCCESS', result['user']['id'], f"Email: {email}")
        return jsonify(result)
    else:
        log_security_event('LOGIN_FAILED', 'unknown', f"Email: {email}")
        return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'staff')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = create_user(email, password, role)
    
    if user:
        log_security_event('USER_CREATED', user.id, f"Email: {email}, Role: {role}")
        return jsonify({'message': 'User created successfully'}), 201
    else:
        return jsonify({'error': 'User already exists'}), 409