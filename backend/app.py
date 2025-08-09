from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

# Import routes
from routes.auth_routes import auth_bp
from routes.staff_routes import staff_bp
from routes.participant_routes import participant_bp

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

# Enable CORS for frontend communication
CORS(app, origins=['http://localhost:3000'])

# Initialize JWT
jwt = JWTManager(app)

# Register blueprints (API routes)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(staff_bp, url_prefix='/api/staff')
app.register_blueprint(participant_bp, url_prefix='/api/participants')

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'NDIS Platform API is running',
        'version': '1.0.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)