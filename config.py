#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Healthcare Risk Platform - Application Configuration
Author: Healthcare Systems Team
Version: 1.0.0
Description: Configuration management for different environments
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with common settings"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/healthcare_risk'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_EXPIRATION', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_REFRESH_EXPIRATION', 2592000)))
    JWT_TOKEN_LOCATION = ('headers', 'json', 'query_string')
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
    
    # Email Configuration
    MAIL_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('SMTP_PORT', 587))
    MAIL_USE_TLS = os.getenv('SMTP_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('SMTP_USERNAME')
    MAIL_PASSWORD = os.getenv('SMTP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('SMTP_FROM_EMAIL', 'noreply@healthcare.com')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/healthcare_risk_platform/app.log')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    UPLOAD_FOLDER = os.getenv('LOCAL_STORAGE_PATH', '/app/storage')
    ALLOWED_EXTENSIONS = {'pdf', 'csv', 'xlsx', 'json', 'xml', 'txt'}
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }
    
    # Feature Flags
    FEATURE_ADVANCED_ANALYTICS = os.getenv('FEATURE_ADVANCED_ANALYTICS', 'True') == 'True'
    FEATURE_MACHINE_LEARNING = os.getenv('FEATURE_MACHINE_LEARNING', 'True') == 'True'
    FEATURE_TELEHEALTH = os.getenv('FEATURE_TELEHEALTH', 'False') == 'True'
    FEATURE_MOBILE_APP = os.getenv('FEATURE_MOBILE_APP', 'False') == 'True'
    FEATURE_BATCH_PROCESSING = os.getenv('FEATURE_BATCH_PROCESSING', 'True') == 'True'
    FEATURE_DATA_EXPORT = os.getenv('FEATURE_DATA_EXPORT', 'True') == 'True'
    
    # Compliance Configuration
    HIPAA_COMPLIANT = os.getenv('HIPAA_COMPLIANT', 'True') == 'True'
    GDPR_COMPLIANT = os.getenv('GDPR_COMPLIANT', 'True') == 'True'
    COMPLIANCE_MODE = os.getenv('COMPLIANCE_MODE', 'strict')
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', 2555))  # ~7 years
    
    # Celery Configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    
    # API Configuration
    API_TITLE = 'Healthcare Risk Platform API'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.2'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False
    JWT_VERIFY_EXP = True


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://test_user:test_password@localhost:5432/healthcare_risk_test'
    )
    WTF_CSRF_ENABLED = False
    JWT_VERIFY_EXP = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_ECHO = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class StagingConfig(ProductionConfig):
    """Staging environment configuration"""
    DEBUG = False
    TESTING = False


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment
    
    Args:
        env: Environment name (development, testing, production, staging)
        
    Returns:
        Configuration class for the specified environment
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env.lower(), config['default'])
