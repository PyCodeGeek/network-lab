# STEP 1: Create missing app/auth/decorators.py
# =============================================

# backend/app/auth/decorators.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def role_required(required_role):
    """Decorator to require specific role for access"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            
            # For demo purposes, admin user has all roles
            # In production, you'd check user roles from database
            if current_user == 'admin':
                return f(*args, **kwargs)
            
            # For other users, you'd implement proper role checking
            user_roles = ['user']  # This would come from database
            
            if required_role not in user_roles:
                return jsonify(message="Insufficient permissions"), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def operator_required(f):
    """Decorator to require operator role"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        
        # For demo purposes, admin user is always operator
        # In production, you'd check user roles from database
        if current_user == 'admin':
            return f(*args, **kwargs)
        
        # Check if user has operator role
        user_roles = ['user']  # This would come from database
        
        if 'operator' not in user_roles and 'admin' not in user_roles:
            return jsonify(message="Operator role required"), 403
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        
        # For demo purposes, only 'admin' user is admin
        if current_user != 'admin':
            return jsonify(message="Admin role required"), 403
        
        return f(*args, **kwargs)
    return decorated_function




