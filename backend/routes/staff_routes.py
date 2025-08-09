from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.security import require_auth, require_role
from models import Staff, User, SessionLocal
from automation.workflows import trigger_staff_onboarding

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/', methods=['GET'])
@require_auth
def get_all_staff():
    db = SessionLocal()
    try:
        staff_list = db.query(Staff).join(User).all()
        result = []
        for staff in staff_list:
            result.append({
                'id': staff.id,
                'first_name': staff.first_name,
                'last_name': staff.last_name,
                'email': staff.user.email,
                'phone': staff.phone,
                'position': staff.position,
                'status': staff.status,
                'hire_date': staff.hire_date.isoformat() if staff.hire_date else None
            })
        return jsonify({'staff': result})
    finally:
        db.close()

@staff_bp.route('/', methods=['POST'])
@require_role('admin')
def create_staff():
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Create user account first
        from auth import create_user
        user = create_user(data['email'], data['password'], 'staff')
        
        if not user:
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create staff profile
        new_staff = Staff(
            user_id=user.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            position=data.get('position')
        )
        
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)
        
        # Trigger automation workflow (Aryan's work)
        trigger_staff_onboarding(new_staff.id, data['email'])
        
        return jsonify({
            'message': 'Staff created successfully',
            'staff_id': new_staff.id
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@staff_bp.route('/<int:staff_id>', methods=['PUT'])
@require_auth
def update_staff(staff_id):
    db = SessionLocal()
    try:
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
        
        data = request.get_json()
        staff.first_name = data.get('first_name', staff.first_name)
        staff.last_name = data.get('last_name', staff.last_name)
        staff.phone = data.get('phone', staff.phone)
        staff.position = data.get('position', staff.position)
        staff.status = data.get('status', staff.status)
        
        db.commit()
        return jsonify({'message': 'Staff updated successfully'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()