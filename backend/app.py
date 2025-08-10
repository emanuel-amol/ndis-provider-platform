from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import bcrypt
import json

app = Flask(__name__)

# Enable CORS for frontend communication
CORS(app, origins=['http://localhost:3000'])

# Simple in-memory user store for demo
USERS = {
    'admin@ndis.com': {
        'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewDs.8.YhK6P.5jO',  # admin123
        'role': 'admin',
        'id': 1,
        'email': 'admin@ndis.com'
    }
}

# Simple in-memory staff store
STAFF = [
    {
        'id': 1,
        'first_name': 'John',
        'last_name': 'Admin', 
        'email': 'admin@ndis.com',
        'phone': '+61400123456',
        'position': 'Administrator',
        'status': 'active',
        'hire_date': '2024-01-01T00:00:00'
    }
]

def verify_password(password, hashed):
    """Verify password against hash"""
    print(f"🔧 Checking password: '{password}' against hash")
    
    # For demo purposes, just check if password is 'admin123'
    if password == 'admin123':
        print("✅ Password matches admin123")
        return True
    
    # Try bcrypt as backup
    try:
        result = bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        print(f"🔒 BCrypt result: {result}")
        return result
    except Exception as e:
        print(f"⚠️ BCrypt failed: {e}")
        return False
# Auth routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        print("🔐 Login attempt started")
        data = request.get_json()
        print(f"📝 Received data: {data}")
        
        if not data:
            print("❌ No data provided")
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {'*' * len(password) if password else 'None'}")
        
        if not email or not password:
            print("❌ Missing email or password")
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if user exists
        user = USERS.get(email)
        print(f"👤 User found: {user is not None}")
        
        if not user:
            print(f"❌ User not found for email: {email}")
            print(f"📋 Available users: {list(USERS.keys())}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        password_valid = verify_password(password, user['password_hash'])
        print(f"🔑 Password valid: {password_valid}")
        
        if password_valid:
            print("✅ Login successful!")
            # Return success with fake token
            return jsonify({
                'token': 'fake-jwt-token-for-demo',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'role': user['role']
                }
            })
        else:
            print("❌ Invalid password")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"💥 Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

# Staff routes
@app.route('/api/staff', methods=['GET'])
def get_staff():
    return jsonify({'staff': STAFF})

@app.route('/api/staff', methods=['POST'])
def create_staff():
    try:
        data = request.get_json()
        
        new_staff = {
            'id': len(STAFF) + 1,
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'phone': data.get('phone'),
            'position': data.get('position'),
            'status': 'active',
            'hire_date': '2024-01-01T00:00:00'
        }
        
        STAFF.append(new_staff)
        
        # Simulate automation workflow
        print(f"🤖 AUTOMATION TRIGGERED: Staff Onboarding for {data['first_name']} {data['last_name']}")
        print(f"📧 Welcome email sent to {data['email']}")
        
        return jsonify({
            'message': 'Staff created successfully',
            'staff_id': new_staff['id']
        }), 201
        
    except Exception as e:
        print(f"Create staff error: {e}")
        return jsonify({'error': str(e)}), 500

# Participants routes
@app.route('/api/participants', methods=['GET'])
def get_participants():
    participants = [
        {
            'id': 1,
            'first_name': 'Alice',
            'last_name': 'Brown',
            'email': 'alice@email.com',
            'phone': '+61400456789',
            'ndis_number': 'NDIS001',
            'status': 'active',
            'created_at': '2024-01-01T00:00:00'
        }
    ]
    return jsonify({'participants': participants})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Simple NDIS Platform API...")
    print("📱 Frontend: http://localhost:3000")
    print("🔐 Demo login: admin@ndis.com / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)