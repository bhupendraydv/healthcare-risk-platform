"""Flask blueprints for the Healthcare Risk Platform."""
from flask import Blueprint

# Initialize blueprints
api_bp = Blueprint('api', __name__, url_prefix='/api')
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
patient_bp = Blueprint('patient', __name__, url_prefix='/patient')
risk_bp = Blueprint('risk', __name__, url_prefix='/risk')
report_bp = Blueprint('report', __name__, url_prefix='/report')
