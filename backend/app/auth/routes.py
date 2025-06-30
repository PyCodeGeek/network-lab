
# # backend/app/auth/routes.py
# from datetime import datetime, timedelta
# from flask import Blueprint, request, jsonify, current_app
# from flask_jwt_extended import (
#     create_access_token, create_refresh_token, jwt_required,
#     get_jwt_identity, get_jwt, verify_jwt_in_request
# )
# from sqlalchemy.exc import IntegrityError
# from marshmallow import Schema, fields, ValidationError, validate
# from app import db
# from app.auth.models import User, BlacklistedToken, UserSession
# from app.utils.decorators import admin_required
# from app.utils.validators import validate_password_strength

# auth_bp = Blueprint('auth', __name__)

# # Marshmallow schemas for validation
# class LoginSchema(Schema):
#     username = fields.Str(required=True, validate=validate.Length(min=3, max=64))
#     password = fields.Str(required=True, validate=validate.Length(min=6))

# class RegisterSchema(Schema):
#     username = fields.Str(required=True, validate=validate.Length(min=3, max=64))
#     email = fields.Email(required=True)
#     password = fields.Str(required=True, validate=validate_password_strength)
#     role = fields.Str(missing='user', validate=validate.OneOf(['user', 'operator', 'admin']))
#     first_name = fields.Str(validate=validate.Length(max=50))
#     last_name = fields.Str(validate=validate.Length(max=50))
#     phone = fields.Str(validate=validate.Length(max=20))
#     department = fields.Str(validate=validate.Length(max=50))

# class PasswordChangeSchema(Schema):
#     current_password = fields.Str(required=True)
#     new_password = fields.Str(required=True, validate=validate_password_strength)

# class ProfileUpdateSchema(Schema):
#     email = fields.Email()
#     first_name = fields.Str(validate=validate.Length(max=50))
#     last_name = fields.Str(validate=validate.Length(max=50))
#     phone = fields.Str(validate=validate.Length(max=20))
#     department = fields.Str(validate=validate.Length(max=50))

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     """User login endpoint."""
#     schema = LoginSchema()
    
#     try:
#         data = schema.load(request.get_json())
#     except ValidationError as err:
#         return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
#     username = data['username']
#     password = data['password']
    
#     # Find user
#     user = User.query.filter_by(username=username).first()
    
#     if not user:
#         return jsonify({'message': 'Invalid credentials'}), 401
    
#     # Check if account is locked
#     if user.is_locked():
#         return jsonify({'message': 'Account is temporarily locked due to multiple failed login attempts'}), 423
    
#     # Check if account is active
#     if not user.is_active:
#         return jsonify({'message': 'Account is deactivated'}), 401
    
#     # Verify password
#     if not user.check_password(password):
#         user.record_login_attempt(success=False)
#         return jsonify({'message': 'Invalid credentials'}), 401
    
#     # Successful login
#     user.record_login_attempt(success=True)
    
#     # Create tokens
#     access_token = create_access_token(identity=user.id)
#     refresh_token = create_refresh_token(identity=user.id)
    
#     # Create session record
#     session = UserSession(
#         user_id=user.id,
#         session_token=access_token,
#         ip_address=request.remote_addr,
#         user_agent=request.headers.get('User-Agent', '')
#     )
#     db.session.add(session)
#     db.session.commit()
    
#     return jsonify({
#         'access_token': access_token,
#         'refresh_token': refresh_token,
#         'user': user.to_dict()
#     }), 200

# @auth_bp.route('/register', methods=['POST'])
# @jwt_required()
# @admin_required
# def register():
#     """User registration endpoint (admin only)."""
#     schema = RegisterSchema()
    
#     try:
#         data = schema.load(request.get_json())
#     except ValidationError as err:
#         return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
#     # Check if username or email already exists
#     if User.query.filter_by(username=data['username']).first():
#         return jsonify({'message': 'Username already exists'}), 400
    
#     if User.query.filter_by(email=data['email']).first():
#         return jsonify({'message': 'Email already exists'}), 400
    
#     # Create new user
#     user = User(
#         username=data['username'],
#         email=data['email'],
#         role=data['role'],
#         first_name=data.get('first_name'),
#         last_name=data.get('last_name'),
#         phone=data.get('phone'),
#         department=data.get('department')
#     )
#     user.set_password(data['password'])
    
#     try:
#         db.session.add(user)
#         db.session.commit()
#         return jsonify({
#             'message': 'User registered successfully',
#             'user': user.to_dict()
#         }), 201
#     except IntegrityError:
#         db.session.rollback()
#         return jsonify({'message': 'Registration failed due to data conflict'}), 400

# @auth_bp.route('/refresh', methods=['POST'])
# @jwt_required(refresh=True)
# def refresh():
#     """Refresh access token."""
#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)
    
#     if not user or not user.is_active:
#         return jsonify({'message': 'User not found or inactive'}), 404
    
#     new_access_token = create_access_token(identity=current_user_id)
    
#     return jsonify({
#         'access_token': new_access_token
#     }), 200

# @auth_bp.route('/logout', methods=['POST'])
# @jwt_required()
# def logout():
#     """User logout endpoint."""
#     jti = get_jwt()['jti']
#     token_type = get_jwt()['type']
#     current_user_id = get_jwt_identity()
    
#     # Add token to blacklist
#     blacklisted_token = BlacklistedToken(
#         jti=jti,
#         token_type=token_type,
#         user_id=current_user_id,
#         expires_at=datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
#     )
#     db.session.add(blacklisted_token)
    
#     # Deactivate user session
#     session = UserSession.query.filter_by(
#         user_id=current_user_id,
#         is_active=True
#     ).first()
#     if session:
#         session.deactivate()
    
#     db.session.commit()
    
#     return jsonify({'message': 'Successfully logged out'}), 200

# @auth_bp.route('/profile', methods=['GET'])
# @jwt_required()
# def get_profile():
#     """Get current user profile."""
#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)
    
#     if not user:
#         return jsonify({'message': 'User not found'}), 404
    
#     # Update session activity
#     session = UserSession.query.filter_by(
#         user_id=current_user_id,
#         is_active=True
#     ).first()
#     if session:
#         session.update_activity()
    
#     return jsonify(user.to_dict()), 200

# @auth_bp.route('/profile', methods=['PUT'])
# @jwt_required()
# def update_profile():
#     """Update current user profile."""
#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)
    
#     if not user:
#         return jsonify({'message': 'User not found'}), 404
    
#     schema = ProfileUpdateSchema()
    
#     try:
#         data = schema.load(request.get_json())
#     except ValidationError as err:
#         return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
#     # Check if email is being changed and already exists
#     if 'email' in data and data['email'] != user.email:
#         if User.query.filter_by(email=data['email']).first():
#             return jsonify({'message': 'Email already exists'}), 400
    
#     # Update user fields
#     for field, value in data.items():
#         setattr(user, field, value)
    
#     user.updated_at = datetime.utcnow()
    
#     try:
#         db.session.commit()
#         return jsonify({
#             'message': 'Profile updated successfully',
#             'user': user.to_dict()
#         }), 200
#     except IntegrityError:
#         db.session.rollback()
#         return jsonify({'message': 'Update failed due to data conflict'}), 400

# @auth_bp.route('/change-password', methods=['POST'])
# @jwt_required()
# def change_password():
#     """Change user password."""
#     current_user_id = get_jwt_identity()
#     user = User.query.get(current_user_id)
    
#     if not user:
#         return jsonify({'message': 'User not found'}), 404
    
#     schema = PasswordChangeSchema()
    
#     try:
#         data = schema.load(request.get_json())
#     except ValidationError as err:
#         return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
#     # Verify current password
#     if not user.check_password(data['current_password']):
#         return jsonify({'message': 'Current password is incorrect'}), 400
    
#     # Set new password
#     user.set_password(data['new_password'])
#     user.updated_at = datetime.utcnow()
    
#     db.session.commit()
    
#     return jsonify({'message': 'Password changed successfully'}), 200

# @auth_bp.route('/users', methods=['GET'])
# @jwt_required()
# @admin_required
# def list_users():
#     """List all users (admin only)."""
#     page = request.args.get('page', 1, type=int)
#     per_page = min(request.args.get('per_page', 20, type=int), 100)
#     search = request.args.get('search', '', type=str)
#     role = request.args.get('role', '', type=str)
    
#     query = User.query
    
#     # Apply search filter
#     if search:
#         query = query.filter(
#             db.or_(
#                 User.username.contains(search),
#                 User.email.contains(search),
#                 User.first_name.contains(search),
#                 User.last_name.contains(search)
#             )
#         )
    
#     # Apply role filter
#     if role:
#         query = query.filter(User.role == role)
    
#     # Order by creation date
#     query = query.order_by(User.created_at.desc())
    
#     # Paginate
#     pagination = query.paginate(
#         page=page, per_page=per_page, error_out=False
#     )
    
#     users = pagination.items
    
#     return jsonify({
#         'users': [user.to_dict() for user in users],
#         'pagination': {
#             'page': page,
#             'pages': pagination.pages,
#             'per_page': per_page,
#             'total': pagination.total,
#             'has_next': pagination.has_next,
#             'has_prev': pagination.has_prev
#         }
#     }), 200

# @auth_bp.route('/users/<int:user_id>', methods=['PUT'])
# @jwt_required()
# @admin_required
# def update_user(user_id):
#     """Update user (admin only)."""
#     user = User.query.get(user_id)
    
#     if not user:
#         return jsonify({'message': 'User not found'}), 404
    
#     schema = RegisterSchema(partial=True)
    
#     try:
#         data = schema.load(request.get_json())
#     except ValidationError as err:
#         return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
#     # Check for username/email conflicts
#     if 'username' in data and data['username'] != user.username:
#         if User.query.filter_by(username=data['username']).first():
#             return jsonify({'message': 'Username already exists'}), 400
    
#     if 'email' in data and data['email'] != user.email:
#         if User.query.filter_by(email=data['email']).first():
#             return jsonify({'message': 'Email already exists'}), 400
    
#     # Update user fields
#     for field, value in data.items():
#         if field == 'password':
#             user.set_password(value)
#         else:
#             setattr(user, field, value)
    
#     user.updated_at = datetime.utcnow()
    
#     try:
#         db.session.commit()
#         return jsonify({
#             'message': 'User updated successfully',
#             'user': user.to_dict()
#         }), 200
#     except IntegrityError:
#         db.session.rollback()
#         return jsonify({'message': 'Update failed due to data conflict'}), 400

# @auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
# @jwt_required()
# @admin_required
# def delete_user(user_id):
#     """Delete user (admin only)."""
#     current_user_id = get_jwt_identity()
    
#     if user_id == current_user_id:
#         return jsonify({'message': 'Cannot delete your own account'}), 400
    
#     user = User.query.get(user_id)
    
#     if not user:
#         return jsonify({'message': 'User not found'}), 404
    
#     # Deactivate instead of deleting to maintain referential integrity
#     user.is_active = False
#     user.updated_at = datetime.utcnow()
    
#     db.session.commit()
    
#     return jsonify({'message': 'User deactivated successfully'}), 200

# @auth_bp.route('/users/<int:user_id>/unlock', methods=['POST'])
# @jwt_required()
# @admin_required
# def unlock_user(user_id):
#     """Unlock user account (admin only)."""
#     user = User.query.get(user_id)
    
#     if not user:
#         return jsonify({'message': 'User not found'}), 404
    
#     user.unlock_account()
    
#     return jsonify({'message': 'User account unlocked successfully'}), 200

# # JWT token verification callback
# @auth_bp.before_app_request
# def check_token_blacklist():
#     """Check if token is blacklisted before processing request."""
#     try:
#         verify_jwt_in_request(optional=True)
#         if get_jwt():
#             jti = get_jwt()['jti']
#             token = BlacklistedToken.query.filter_by(jti=jti).first()
#             if token:
#                 return jsonify({'message': 'Token has been revoked'}), 401
#     except Exception:
#         pass



# backend/app/auth/routes.py
# from flask import Blueprint, request, jsonify, current_app
# from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
# from app import db
# from app.auth.models import User
# from datetime import datetime
# import re

# auth_bp = Blueprint('auth', __name__)
# devices_bp = Blueprint('devices', __name__)

# def validate_email(email):
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None

# def validate_password(password):
#     # At least 8 characters, one uppercase, one lowercase, one digit
#     if len(password) < 8:
#         return False, "Password must be at least 8 characters long"
#     if not re.search(r'[A-Z]', password):
#         return False, "Password must contain at least one uppercase letter"
#     if not re.search(r'[a-z]', password):
#         return False, "Password must contain at least one lowercase letter"
#     if not re.search(r'\d', password):
#         return False, "Password must contain at least one digit"
#     return True, "Valid password"

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     try:
#         data = request.get_json()
        
#         if not data:
#             return jsonify({'message': 'No data provided'}), 400
        
#         username = data.get('username', '').strip()
#         password = data.get('password', '')
        
#         if not username or not password:
#             return jsonify({'message': 'Username and password are required'}), 400
        
#         # Find user by username or email
#         user = User.query.filter(
#             (User.username == username) | (User.email == username)
#         ).first()
        
#         if not user or not user.check_password(password):
#             return jsonify({'message': 'Invalid credentials'}), 401
        
#         if not user.is_active:
#             return jsonify({'message': 'Account is disabled'}), 401
        
#         # Update last login
#         user.last_login = datetime.utcnow()
#         db.session.commit()
        
#         # Create tokens
#         access_token = create_access_token(identity=user.id)
#         refresh_token = create_refresh_token(identity=user.id)
        
#         return jsonify({
#             'access_token': access_token,
#             'refresh_token': refresh_token,
#             'user': user.to_dict()
#         }), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Login error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @auth_bp.route('/register', methods=['POST'])
# def register():
#     try:
#         data = request.get_json()
        
#         if not data:
#             return jsonify({'message': 'No data provided'}), 400
        
#         username = data.get('username', '').strip()
#         email = data.get('email', '').strip().lower()
#         password = data.get('password', '')
#         role = data.get('role', 'user')
        
#         # Validation
#         if not username or not email or not password:
#             return jsonify({'message': 'Username, email, and password are required'}), 400
        
#         if len(username) < 3:
#             return jsonify({'message': 'Username must be at least 3 characters long'}), 400
        
#         if not validate_email(email):
#             return jsonify({'message': 'Invalid email format'}), 400
        
#         is_valid_password, password_message = validate_password(password)
#         if not is_valid_password:
#             return jsonify({'message': password_message}), 400
        
#         if role not in ['user', 'admin']:
#             role = 'user'
        
#         # Check if user already exists
#         if User.query.filter_by(username=username).first():
#             return jsonify({'message': 'Username already exists'}), 409
        
#         if User.query.filter_by(email=email).first():
#             return jsonify({'message': 'Email already exists'}), 409
        
#         # Create new user
#         user = User(
#             username=username,
#             email=email,
#             role=role
#         )
#         user.set_password(password)
        
#         db.session.add(user)
#         db.session.commit()
        
#         return jsonify({
#             'message': 'User registered successfully',
#             'user': user.to_dict()
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Registration error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @auth_bp.route('/profile', methods=['GET'])
# @jwt_required()
# def get_profile():
#     try:
#         current_user_id = get_jwt_identity()
#         user = User.query.get(current_user_id)
        
#         if not user:
#             return jsonify({'message': 'User not found'}), 404
        
#         return jsonify(user.to_dict()), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Get profile error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @auth_bp.route('/profile', methods=['PUT'])
# @jwt_required()
# def update_profile():
#     try:
#         current_user_id = get_jwt_identity()
#         user = User.query.get(current_user_id)
        
#         if not user:
#             return jsonify({'message': 'User not found'}), 404
        
#         data = request.get_json()
#         if not data:
#             return jsonify({'message': 'No data provided'}), 400
        
#         # Update allowed fields
#         if 'email' in data:
#             email = data['email'].strip().lower()
#             if not validate_email(email):
#                 return jsonify({'message': 'Invalid email format'}), 400
#             if User.query.filter(User.email == email, User.id != user.id).first():
#                 return jsonify({'message': 'Email already exists'}), 409
#             user.email = email
        
#         if 'password' in data:
#             password = data['password']
#             is_valid_password, password_message = validate_password(password)
#             if not is_valid_password:
#                 return jsonify({'message': password_message}), 400
#             user.set_password(password)
        
#         user.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         return jsonify({
#             'message': 'Profile updated successfully',
#             'user': user.to_dict()
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Update profile error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @auth_bp.route('/refresh', methods=['POST'])
# @jwt_required(refresh=True)
# def refresh():
#     try:
#         current_user_id = get_jwt_identity()
#         user = User.query.get(current_user_id)
        
#         if not user or not user.is_active:
#             return jsonify({'message': 'User not found or inactive'}), 404
        
#         access_token = create_access_token(identity=user.id)
        
#         return jsonify({
#             'access_token': access_token
#         }), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Token refresh error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @auth_bp.route('/users', methods=['GET'])
# @jwt_required()
# def list_users():
#     try:
#         current_user_id = get_jwt_identity()
#         current_user = User.query.get(current_user_id)
        
#         if not current_user or current_user.role != 'admin':
#             return jsonify({'message': 'Admin access required'}), 403
        
#         page = request.args.get('page', 1, type=int)
#         per_page = min(request.args.get('per_page', 10, type=int), 100)
        
#         users = User.query.paginate(
#             page=page, per_page=per_page, error_out=False
#         )
        
#         return jsonify({
#             'users': [user.to_dict() for user in users.items],
#             'total': users.total,
#             'pages': users.pages,
#             'current_page': page
#         }), 200
        
#     except Exception as e:
#         current_app.logger.error(f"List users error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500


# # added after devices_bp

# # Mock data for testing (no database dependencies)
# MOCK_DEVICES = [
#     {
#         'id': 1, 
#         'name': 'Router-01', 
#         'device_type': 'router', 
#         'ip_address': '192.168.1.1', 
#         'status': 'active',
#         'ports': [
#             {'id': 1, 'name': 'GigabitEthernet0/0', 'status': 'up'},
#             {'id': 2, 'name': 'GigabitEthernet0/1', 'status': 'down'}
#         ]
#     },
#     {
#         'id': 2, 
#         'name': 'Switch-01', 
#         'device_type': 'switch', 
#         'ip_address': '192.168.1.2', 
#         'status': 'active',
#         'ports': [
#             {'id': 3, 'name': 'FastEthernet0/1', 'status': 'up'},
#             {'id': 4, 'name': 'FastEthernet0/2', 'status': 'down'}
#         ]
#     },
#     {
#         'id': 3, 
#         'name': 'Server-01', 
#         'device_type': 'server', 
#         'ip_address': '192.168.1.10', 
#         'status': 'inactive',
#         'ports': [
#             {'id': 5, 'name': 'eth0', 'status': 'down'}
#         ]
#     }
# ]

# @devices_bp.route('/', methods=['GET'])
# @jwt_required()
# def get_devices():
#     return jsonify(MOCK_DEVICES)

# @devices_bp.route('/<int:device_id>', methods=['GET'])
# @jwt_required()
# def get_device(device_id):
#     device = next((d for d in MOCK_DEVICES if d['id'] == device_id), None)
#     if device:
#         return jsonify(device)
#     return jsonify(message="Device not found"), 404

# @devices_bp.route('/', methods=['POST'])
# @jwt_required()
# def create_device():
#     data = request.get_json() or {}
    
#     new_device = {
#         'id': len(MOCK_DEVICES) + 1,
#         'name': data.get('name', 'New Device'),
#         'device_type': data.get('device_type', 'router'),
#         'ip_address': data.get('ip_address', '192.168.1.100'),
#         'status': 'inactive',
#         'ports': []
#     }
    
#     MOCK_DEVICES.append(new_device)
#     return jsonify(new_device), 201

# @devices_bp.route('/<int:device_id>', methods=['PUT'])
# @jwt_required()
# def update_device(device_id):
#     device = next((d for d in MOCK_DEVICES if d['id'] == device_id), None)
#     if not device:
#         return jsonify(message="Device not found"), 404
    
#     data = request.get_json() or {}
#     device.update({
#         'name': data.get('name', device['name']),
#         'device_type': data.get('device_type', device['device_type']),
#         'ip_address': data.get('ip_address', device['ip_address']),
#         'status': data.get('status', device['status'])
#     })
    
#     return jsonify(device)

# @devices_bp.route('/<int:device_id>', methods=['DELETE'])
# @jwt_required()
# def delete_device(device_id):
#     global MOCK_DEVICES
#     MOCK_DEVICES = [d for d in MOCK_DEVICES if d['id'] != device_id]
#     return jsonify(message="Device deleted"), 200




from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    """User login endpoint"""
    if request.method == 'GET':
        return jsonify({
            "message": "Login endpoint",
            "method": "POST",
            "endpoint": "/api/auth/login",
            "required_fields": ["username", "password"],
            "example": {
                "username": "admin",
                "password": "admin"
            },
            "test_with_curl": 'curl -X POST http://your-server:5000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"admin"}\''
        })
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify(message="Username and password required"), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return jsonify(
                access_token=access_token, 
                user=user.to_dict()
            )
        
        return jsonify(message="Invalid credentials"), 401
        
    except Exception as e:
        return jsonify(message=f"Login error: {str(e)}"), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify(message="User not found"), 404
        
        return jsonify(user.to_dict())
        
    except Exception as e:
        return jsonify(message=f"Profile error: {str(e)}"), 500
    
    
# Add API documentation endpoint
@auth_bp.route('/docs', methods=['GET'])
def api_docs():
    """API documentation"""
    return jsonify({
        "endpoints": {
            "POST /api/auth/login": {
                "description": "User authentication",
                "required": ["username", "password"],
                "example": {"username": "admin", "password": "admin"}
            },
            "GET /api/auth/profile": {
                "description": "Get user profile",
                "required": ["Authorization: Bearer <token>"]
            }
        }
    })