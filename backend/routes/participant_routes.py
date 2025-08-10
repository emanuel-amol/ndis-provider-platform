from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.security import require_auth, require_role
from models import Participant, SessionLocal
from automation.workflows import trigger_participant_enrollment

participant_bp = Blueprint('participant', __name__)

@participant_bp.route('/', methods=['GET'])
@require_auth
def get_all_participants():
    db = SessionLocal()
    try:
        participants_list = db.query(Participant).all()
        result = []
        for participant in participants_list:
            result.append({
                'id': participant.id,
                'first_name': participant.first_name,
                'last_name': participant.last_name,
                'email': participant.email,
                'phone': participant.phone,
                'address': participant.address,
                'emergency_contact': participant.emergency_contact,
                'ndis_number': participant.ndis_number,
                'status': participant.status,
                'created_at': participant.created_at.isoformat() if participant.created_at else None
            })
        return jsonify({'participants': result})
    finally:
        db.close()

@participant_bp.route('/', methods=['POST'])
@require_role('admin')
def create_participant():
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Create participant
        new_participant = Participant(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            emergency_contact=data.get('emergency_contact'),
            ndis_number=data.get('ndis_number')
        )
        
        db.add(new_participant)
        db.commit()
        db.refresh(new_participant)
        
        # Trigger automation workflow (Aryan's work)
        if new_participant.email:
            trigger_participant_enrollment(new_participant.id, new_participant.email)
        
        return jsonify({
            'message': 'Participant created successfully',
            'participant_id': new_participant.id
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@participant_bp.route('/<int:participant_id>', methods=['PUT'])
@require_auth
def update_participant(participant_id):
    db = SessionLocal()
    try:
        participant = db.query(Participant).filter(Participant.id == participant_id).first()
        if not participant:
            return jsonify({'error': 'Participant not found'}), 404
        
        data = request.get_json()
        participant.first_name = data.get('first_name', participant.first_name)
        participant.last_name = data.get('last_name', participant.last_name)
        participant.email = data.get('email', participant.email)
        participant.phone = data.get('phone', participant.phone)
        participant.address = data.get('address', participant.address)
        participant.emergency_contact = data.get('emergency_contact', participant.emergency_contact)
        participant.ndis_number = data.get('ndis_number', participant.ndis_number)
        participant.status = data.get('status', participant.status)
        
        db.commit()
        return jsonify({'message': 'Participant updated successfully'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()