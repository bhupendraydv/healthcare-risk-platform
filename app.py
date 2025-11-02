#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Healthcare Risk Platform - Main Flask Application
Author: Healthcare Systems Team
Version: 1.0.0
Description: Main entry point for the Healthcare Risk Platform API server
"""
import os
import logging
from datetime import timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/healthcare_risk'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = os.getenv('DEBUG', 'False') == 'True'
# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
    seconds=int(os.getenv('JWT_EXPIRATION', 3600))
)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(
    seconds=int(os.getenv('JWT_REFRESH_EXPIRATION', 2592000))
)
# CORS Configuration
app.config['CORS_ORIGINS'] = os.getenv('CORS_ORIGINS', '*').split(',')
# Session Configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Import blueprints and models
try:
    from routes import api_bp, auth_bp, patient_bp, risk_bp, report_bp
    from models import User, Patient, RiskAssessment, Vital, LabResult
    logger.info('Successfully imported all routes and models')
except ImportError as e:
    logger.warning(f'Some modules not yet available: {e}')
# Register blueprints
if 'api_bp' in locals():
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(patient_bp, url_prefix='/api/patients')
    app.register_blueprint(risk_bp, url_prefix='/api/risk')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
# Global Error Handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    response = {
        'success': False,
        'error': 'Bad Request',
        'message': str(error),
        'status_code': 400
    }
    return jsonify(response), 400
@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors"""
    response = {
        'success': False,
        'error': 'Unauthorized',
        'message': 'Authentication required. Please provide valid credentials.',
        'status_code': 401
    }
    return jsonify(response), 401
@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    response = {
        'success': False,
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource.',
        'status_code': 403
    }
    return jsonify(response), 403
@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    response = {
        'success': False,
        'error': 'Not Found',
        'message': 'The requested resource was not found.',
        'status_code': 404
    }
    return jsonify(response), 404
@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    logger.error(f'Internal Server Error: {error}')
    response = {
        'success': False,
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred. Please try again later.',
        'status_code': 500
    }
    return jsonify(response), 500
# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring and load balancers"""
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'service': 'Healthcare Risk Platform API',
            'version': '1.0.0',
            'database': 'connected'
        }), 200
    except Exception as e:
        logger.error(f'Health check failed: {e}')
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'database': 'disconnected'
        }), 500
# API Information endpoint
@app.route('/api', methods=['GET'])
def api_info():
    """Provide information about the API"""
    return jsonify({
        'service': 'Healthcare Risk Platform API',
        'version': '1.0.0',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth',
            'patients': '/api/patients',
            'risk': '/api/risk',
            'reports': '/api/reports'
        }
    }), 200
@app.before_request
def log_request():
    """Log incoming requests"""
    logger.debug(f'{request.method} {request.path} - {request.remote_addr}')
@app.after_request
def set_response_headers(response):
    """Set security headers on all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('DEBUG', 'False') == 'True'
    
    logger.info(f'Starting Healthcare Risk Platform API on {host}:{port}')
    logger.info(f'Environment: {os.getenv("FLASK_ENV", "production")}')
    logger.info(f'Debug Mode: {debug}')
    
    # Create database tables
    try:
        with app.app_context():
            db.create_all()
            logger.info('Database tables created successfully')
    except Exception as e:
        logger.warning(f'Could not create database tables: {e}')
    
    # Start the Flask development server
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug,
        threaded=True
    )
