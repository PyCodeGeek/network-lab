
# backend/app/topology/__init__.py
from flask import Blueprint

topology_bp = Blueprint('topology', __name__)

from app.topology import routes