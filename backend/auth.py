import bcrypt
from flask_jwt_extended import create_access_token
from models import User, SessionLocal

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def authenticate_user(email, password):
    """Authenticate user and return token"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user and verify_password(password, user.password_hash):
            # Create JWT token
            token = create_access_token(
                identity=user.id,
                additional_claims={
                    'email': user.email,
                    'role': user.role
                }
            )
            return {
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role
                }
            }
        return None
    finally:
        db.close()

def create_user(email, password, role='staff'):
    """Create new user"""
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return None
        
        # Create new user
        hashed_password = hash_password(password)
        new_user = User(
            email=email,
            password_hash=hashed_password,
            role=role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    finally:
        db.close()