# backend/app/provisioning/__init__.py
from flask import Blueprint

provisioning_bp = Blueprint('provisioning', __name__)

from app.provisioning import routes