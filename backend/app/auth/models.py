# # backend/app/auth/models.py
# from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from werkzeug.security import generate_password_hash, check_password_hash
# from app import db

# bcrypt = Bcrypt()

# class User(db.Model):
#     """User model for authentication and authorization."""
#     __tablename__ = 'users'
    
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, nullable=False, index=True)
#     email = db.Column(db.String(120), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(256), nullable=False)
#     role = db.Column(db.String(20), default='user', nullable=False)
#     is_active = db.Column(db.Boolean, default=True, nullable=False)
#     last_login = db.Column(db.DateTime)
#     login_count = db.Column(db.Integer, default=0)
#     failed_login_attempts = db.Column(db.Integer, default=0)
#     locked_until = db.Column(db.DateTime)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Profile information
#     first_name = db.Column(db.String(50))
#     last_name = db.Column(db.String(50))
#     phone = db.Column(db.String(20))
#     department = db.Column(db.String(50))
    
#     def set_password(self, password):
#         """Set password hash."""
#         self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
#     def check_password(self, password):
#         """Check password against hash."""
#         return bcrypt.check_password_hash(self.password_hash, password)
    
#     def is_admin(self):
#         """Check if user is an administrator."""
#         return self.role == 'admin'
    
#     def is_operator(self):
#         """Check if user is an operator."""
#         return self.role in ['admin', 'operator']
    
#     def is_locked(self):
#         """Check if account is locked."""
#         if self.locked_until:
#             return datetime.utcnow() < self.locked_until
#         return False
    
#     def lock_account(self, duration_minutes=15):
#         """Lock account for specified duration."""
#         self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
#         db.session.commit()
    
#     def unlock_account(self):
#         """Unlock account and reset failed attempts."""
#         self.locked_until = None
#         self.failed_login_attempts = 0
#         db.session.commit()
    
#     def record_login_attempt(self, success=False):
#         """Record login attempt."""
#         if success:
#             self.last_login = datetime.utcnow()
#             self.login_count += 1
#             self.failed_login_attempts = 0
#             self.locked_until = None
#         else:
#             self.failed_login_attempts += 1
#             # Lock account after 5 failed attempts
#             if self.failed_login_attempts >= 5:
#                 self.lock_account()
#         db.session.commit()
    
#     def get_full_name(self):
#         """Get user's full name."""
#         if self.first_name and self.last_name:
#             return f"{self.first_name} {self.last_name}"
#         return self.username
    
#     def to_dict(self):
#         """Convert user to dictionary."""
#         return {
#             'id': self.id,
#             'username': self.username,
#             'email': self.email,
#             'role': self.role,
#             'is_active': self.is_active,
#             'last_login': self.last_login.isoformat() if self.last_login else None,
#             'login_count': self.login_count,
#             'created_at': self.created_at.isoformat(),
#             'full_name': self.get_full_name(),
#             'first_name': self.first_name,
#             'last_name': self.last_name,
#             'phone': self.phone,
#             'department': self.department
#         }
    
#     def __repr__(self):
#         return f'<User {self.username}>'

# class BlacklistedToken(db.Model):
#     """Blacklisted JWT tokens."""
#     __tablename__ = 'blacklisted_tokens'
    
#     id = db.Column(db.Integer, primary_key=True)
#     jti = db.Column(db.String(36), nullable=False, unique=True)
#     token_type = db.Column(db.String(10), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     revoked_at = db.Column(db.DateTime, default=datetime.utcnow)
#     expires_at = db.Column(db.DateTime, nullable=False)
    
#     user = db.relationship('User', backref='blacklisted_tokens')
    
#     def __repr__(self):
#         return f'<BlacklistedToken {self.jti}>'

# class UserSession(db.Model):
#     """User session tracking."""
#     __tablename__ = 'user_sessions'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     session_token = db.Column(db.String(255), nullable=False, unique=True)
#     ip_address = db.Column(db.String(45))
#     user_agent = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     last_activity = db.Column(db.DateTime, default=datetime.utcnow)
#     is_active = db.Column(db.Boolean, default=True)
    
#     user = db.relationship('User', backref='sessions')
    
#     def update_activity(self):
#         """Update last activity timestamp."""
#         self.last_activity = datetime.utcnow()
#         db.session.commit()
    
#     def deactivate(self):
#         """Deactivate session."""
#         self.is_active = False
#         db.session.commit()
    
#     def __repr__(self):
#         return f'<UserSession {self.user.username}>'





# backend/app/auth/models.py
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import jwt
from flask import current_app

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self):
        payload = {
            'user_id': self.id,
            'username': self.username,
            'role': self.role
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return User.query.get(payload['user_id'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    def __repr__(self):
        return f'<User {self.username}>'
