#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Healthcare Risk Platform - Database Models
Author: Healthcare Systems Team
Version: 1.0.0
Description: SQLAlchemy ORM models for the Healthcare Risk Platform
"""
from datetime import datetime
from sqlalchemy import Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='viewer')  # admin, clinician, viewer
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User(id={self.id}, username={self.username})>'


class Patient(db.Model):
    """Patient model containing demographic and clinical information"""
    __tablename__ = 'patients'
    __table_args__ = (
        Index('idx_mrn', 'mrn'),
        Index('idx_date_of_birth', 'date_of_birth'),
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mrn = db.Column(db.String(50), unique=True, nullable=False)  # Medical Record Number
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # M, F, Other
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    insurance_id = db.Column(db.String(100))
    comorbidities = db.Column(ARRAY(db.String), default=[])
    allergies = db.Column(ARRAY(db.String), default=[])
    current_medications = db.Column(JSONB, default={})
    admission_date = db.Column(db.DateTime)
    discharge_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Patient(id={self.id}, mrn={self.mrn}, first_name={self.first_name})>'


class Vital(db.Model):
    """Vital signs model for storing patient measurements"""
    __tablename__ = 'vital_signs'
    __table_args__ = (
        Index('idx_patient_id_timestamp', 'patient_id', 'measurement_time'),
        CheckConstraint('heart_rate >= 0 AND heart_rate <= 300'),
        CheckConstraint('systolic_bp >= 50 AND systolic_bp <= 300'),
        CheckConstraint('diastolic_bp >= 30 AND diastolic_bp <= 200'),
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = db.Column(UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=False)
    measurement_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    heart_rate = db.Column(db.Integer)  # BPM
    systolic_bp = db.Column(db.Integer)  # mmHg
    diastolic_bp = db.Column(db.Integer)  # mmHg
    respiratory_rate = db.Column(db.Integer)  # breaths/min
    temperature = db.Column(db.Float)  # Celsius
    oxygen_saturation = db.Column(db.Float)  # %
    blood_glucose = db.Column(db.Float)  # mg/dL
    weight = db.Column(db.Float)  # kg
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', backref=db.backref('vitals', lazy=True))

    def __repr__(self):
        return f'<Vital(id={self.id}, patient_id={self.patient_id}, heart_rate={self.heart_rate})>'


class LabResult(db.Model):
    """Laboratory test results model"""
    __tablename__ = 'lab_results'
    __table_args__ = (
        Index('idx_patient_id_test_date', 'patient_id', 'test_date'),
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = db.Column(UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=False)
    test_name = db.Column(db.String(100), nullable=False)  # WBC, RBC, etc
    test_value = db.Column(db.Float)
    unit = db.Column(db.String(50))
    reference_low = db.Column(db.Float)
    reference_high = db.Column(db.Float)
    test_date = db.Column(db.DateTime, nullable=False)
    lab_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, completed, reviewed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', backref=db.backref('lab_results', lazy=True))

    def __repr__(self):
        return f'<LabResult(id={self.id}, patient_id={self.patient_id}, test_name={self.test_name})>'


class RiskAssessment(db.Model):
    """Risk assessment scores model"""
    __tablename__ = 'risk_assessments'
    __table_args__ = (
        Index('idx_patient_id_assessment_date', 'patient_id', 'assessment_date'),
        CheckConstraint('risk_score >= 0 AND risk_score <= 100'),
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = db.Column(UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=False)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)  # 0-100
    risk_category = db.Column(db.String(20))  # low, medium, high, critical
    clinical_factors = db.Column(JSONB, default={})
    alert_triggered = db.Column(db.Boolean, default=False)
    alert_message = db.Column(db.Text)
    assessment_type = db.Column(db.String(50))  # readmission, mortality, etc
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', backref=db.backref('risk_assessments', lazy=True))
    clinician = db.relationship('User', backref=db.backref('assessments', lazy=True))

    def __repr__(self):
        return f'<RiskAssessment(id={self.id}, patient_id={self.patient_id}, risk_score={self.risk_score}, risk_category={self.risk_category})>'


class Alert(db.Model):
    """Clinical alerts model"""
    __tablename__ = 'alerts'
    __table_args__ = (
        Index('idx_patient_id_created_at', 'patient_id', 'created_at'),
        Index('idx_status', 'status'),
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = db.Column(UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # critical, warning, info
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    severity = db.Column(db.String(20))  # low, medium, high, critical
    status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved
    acknowledged_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', backref=db.backref('alerts', lazy=True))
    clinician = db.relationship('User', backref=db.backref('acknowledged_alerts', lazy=True))

    def __repr__(self):
        return f'<Alert(id={self.id}, patient_id={self.patient_id}, severity={self.severity}, status={self.status})>'


class Intervention(db.Model):
    """Clinical interventions model"""
    __tablename__ = 'interventions'
    __table_args__ = (
        Index('idx_patient_id_intervention_date', 'patient_id', 'intervention_date'),
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = db.Column(UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=False)
    intervention_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    intervention_date = db.Column(db.DateTime, nullable=False)
    outcome = db.Column(db.String(50))  # successful, unsuccessful, ongoing
    clinician_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', backref=db.backref('interventions', lazy=True))
    clinician = db.relationship('User', backref=db.backref('interventions', lazy=True))

    def __repr__(self):
        return f'<Intervention(id={self.id}, patient_id={self.patient_id}, intervention_type={self.intervention_type}, outcome={self.outcome})>'
