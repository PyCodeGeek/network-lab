# # backend/app/auth/__init__.py
# from flask import Blueprint

# bp = Blueprint('auth', __name__)

# from app.auth import routes

# # backend/app/auth/routes.py
# from flask import request, jsonify, current_app
# from flask_jwt_extended import (
#     create_access_token, create_refresh_token, jwt_required, 
#     get_jwt_identity, get_jwt
# )
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# from app import db, limiter
# from app.auth import bp
# from app.models import User
# from datetime import datetime, timedelta
# import re

# # Token blacklist (in production, use Redis)
# blacklisted_tokens = set()

# @bp.route('/login', methods=['POST'])
# @limiter.limit("5 per minute")
# def login():
#     """User login endpoint"""
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         username = data.get('username', '').strip()
#         password = data.get('password', '')
        
#         if not username or not password:
#             return jsonify({'error': 'Username and password are required'}), 400
        
#         # Find user by username or email
#         user = User.query.filter(
#             (User.username == username) | (User.email == username)
#         ).first()
        
#         if not user or not user.check_password(password):
#             return jsonify({'error': 'Invalid credentials'}), 401
        
#         if not user.is_active:
#             return jsonify({'error': 'Account is disabled'}), 401
        
#         # Update last login
#         user.last_login = datetime.utcnow()
#         db.session.commit()
        
#         # Create tokens
#         access_token = create_access_token(
#             identity=user.id,
#             additional_claims={'role': user.role}
#         )
#         refresh_token = create_refresh_token(identity=user.id)
        
#         return jsonify({
#             'access_token': access_token,
#             'refresh_token': refresh_token,
#             'user': user.to_dict(),
#             'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
#         }), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Login error: {str(e)}")
#         return jsonify({'error': 'Login failed'}), 500

# @bp.route('/refresh', methods=['POST'])
# @jwt_required(refresh=True)
# def refresh():
#     """Refresh access token"""
#     try:
#         current_user_id = get_jwt_identity()
#         user = User.query.get(current_user_id)
        
#         if not user or not user.is_active:
#             return jsonify({'error': 'User not found or inactive'}), 401
        
#         new_access_token = create_access_token(
#             identity=current_user_id,
#             additional_claims={'role': user.role}
#         )
        
#         return jsonify({
#             'access_token': new_access_token,
#             'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
#         }), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Token refresh error: {str(e)}")
#         return jsonify({'error': 'Token refresh failed'}), 500

# @bp.route('/logout', methods=['POST'])
# @jwt_required()
# def logout():
#     """User logout endpoint"""
#     try:
#         jti = get_jwt()['jti']
#         blacklisted_tokens.add(jti)
#         return jsonify({'message': 'Logged out successfully'}), 200
#     except Exception as e:
#         current_app.logger.error(f"Logout error: {str(e)}")
#         return jsonify({'error': 'Logout failed'}), 500

# @bp.route('/register', methods=['POST'])
# @limiter.limit("3 per minute")
# def register():
#     """User registration endpoint"""
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         username = data.get('username', '').strip()
#         email = data.get('email', '').strip().lower()
#         password = data.get('password', '')
#         role = data.get('role', 'user')
        
#         # Validation
#         errors = []
        
#         if not username or len(username) < 3:
#             errors.append('Username must be at least 3 characters long')
        
#         if not email or not is_valid_email(email):
#             errors.append('Valid email address is required')
        
#         if not password or len(password) < 8:
#             errors.append('Password must be at least 8 characters long')
        
#         if role not in ['admin', 'operator', 'viewer', 'user']:
#             errors.append('Invalid role specified')
        
#         # Check for existing users
#         if User.query.filter_by(username=username).first():
#             errors.append('Username already exists')
        
#         if User.query.filter_by(email=email).first():
#             errors.append('Email already exists')
        
#         if errors:
#             return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
#         # Create user
#         user = User(
#             username=username,
#             email=email,
#             role=role
#         )
#         user.set_password(password)
        
#         db.session.add(user)
#         db.session.commit()
        
#         current_app.logger.info(f"New user registered: {username}")
        
#         return jsonify({
#             'message': 'User registered successfully',
#             'user': user.to_dict()
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Registration error: {str(e)}")
#         return jsonify({'error': 'Registration failed'}), 500

# @bp.route('/profile', methods=['GET'])
# @jwt_required()
# def get_profile():
#     """Get user profile"""
#     try:
#         current_user_id = get_jwt_identity()
#         user = User.query.get(current_user_id)
        
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         return jsonify(user.to_dict()), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Get profile error: {str(e)}")
#         return jsonify({'error': 'Failed to get profile'}), 500

# @bp.route('/profile', methods=['PUT'])
# @jwt_required()
# def update_profile():
#     """Update user profile"""
#     try:
#         current_user_id = get_jwt_identity()
#         user = User.query.get(current_user_id)
        
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         # Update allowed fields
#         if 'email' in data:
#             email = data['email'].strip().lower()
#             if not is_valid_email(email):
#                 return jsonify({'error': 'Invalid email address'}), 400
            
#             # Check if email is already taken by another user
#             existing_user = User.query.filter(
#                 User.email == email,
#                 User.id != current_user_id
#             ).first()
#             if existing_user:
#                 return jsonify({'error': 'Email already exists'}), 400
            
#             user.email = email
        
#         user.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         return jsonify({
#             'message': 'Profile updated successfully',
#             'user': user.to_dict()
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Update profile error: {str(e)}")
#         return jsonify({'error': 'Failed to update profile'}), 500

# @bp.route('/change-password', methods=['POST'])
# @jwt_required()
# @limiter.limit("3 per minute")
# def change_password():
#     """Change user password"""
#     try:
#         current_user_id = get_jwt_identity()
#         user = User.query.get(current_user_id)
        
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         current_password = data.get('current_password', '')
#         new_password = data.get('new_password', '')
        
#         if not current_password or not new_password:
#             return jsonify({'error': 'Current and new passwords are required'}), 400
        
#         if not user.check_password(current_password):
#             return jsonify({'error': 'Current password is incorrect'}), 401
        
#         if len(new_password) < 8:
#             return jsonify({'error': 'New password must be at least 8 characters long'}), 400
        
#         user.set_password(new_password)
#         user.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         current_app.logger.info(f"Password changed for user: {user.username}")
        
#         return jsonify({'message': 'Password changed successfully'}), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Change password error: {str(e)}")
#         return jsonify({'error': 'Failed to change password'}), 500

# @bp.route('/users', methods=['GET'])
# @jwt_required()
# def list_users():
#     """List all users (admin only)"""
#     try:
#         current_user_id = get_jwt_identity()
#         claims = get_jwt()
        
#         if claims.get('role') != 'admin':
#             return jsonify({'error': 'Admin access required'}), 403
        
#         page = request.args.get('page', 1, type=int)
#         per_page = min(request.args.get('per_page', 20, type=int), 100)
        
#         users = User.query.paginate(
#             page=page, 
#             per_page=per_page, 
#             error_out=False
#         )
        
#         return jsonify({
#             'users': [user.to_dict() for user in users.items],
#             'total': users.total,
#             'pages': users.pages,
#             'current_page': page,
#             'per_page': per_page
#         }), 200
        
#     except Exception as e:
#         current_app.logger.error(f"List users error: {str(e)}")
#         return jsonify({'error': 'Failed to list users'}), 500

# @bp.route('/users/<int:user_id>', methods=['PUT'])
# @jwt_required()
# def update_user(user_id):
#     """Update user (admin only)"""
#     try:
#         current_user_id = get_jwt_identity()
#         claims = get_jwt()
        
#         if claims.get('role') != 'admin':
#             return jsonify({'error': 'Admin access required'}), 403
        
#         user = User.query.get(user_id)
#         if not user:
#             return jsonify({'error': 'User not found'}), 404
        
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         # Update allowed fields
#         if 'role' in data:
#             if data['role'] not in ['admin', 'operator', 'viewer', 'user']:
#                 return jsonify({'error': 'Invalid role specified'}), 400
#             user.role = data['role']
        
#         if 'is_active' in data:
#             user.is_active = bool(data['is_active'])
        
#         user.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         current_app.logger.info(f"User {user.username} updated by admin")
        
#         return jsonify({
#             'message': 'User updated successfully',
#             'user': user.to_dict()
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Update user error: {str(e)}")
#         return jsonify({'error': 'Failed to update user'}), 500

# # JWT token blacklist check
# from flask_jwt_extended import jwt_manager

# @jwt_manager.token_in_blocklist_loader
# def check_if_token_revoked(jwt_header, jwt_payload):
#     jti = jwt_payload['jti']
#     return jti in blacklisted_tokens

# # Helper functions
# def is_valid_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None

# # backend/app/auth/decorators.py
# from functools import wraps
# from flask import jsonify
# from flask_jwt_extended import get_jwt, jwt_required

# def role_required(roles):
#     """Decorator to require specific roles"""
#     def decorator(f):
#         @wraps(f)
#         @jwt_required()
#         def decorated_function(*args, **kwargs):
#             claims = get_jwt()
#             user_role = claims.get('role', 'user')
            
#             if isinstance(roles, str):
#                 roles_list = [roles]
#             else:
#                 roles_list = roles
            
#             if user_role not in roles_list:
#                 return jsonify({'error': 'Insufficient permissions'}), 403
            
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator

# def admin_required(f):
#     """Decorator to require admin role"""
#     return role_required('admin')(f)

# def operator_required(f):
#     """Decorator to require operator or admin role"""
#     return role_required(['admin', 'operator'])(f)









# backend/app/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from app.auth import routes