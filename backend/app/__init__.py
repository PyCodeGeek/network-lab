# # # backend/app/__init__.py
# # from flask import Flask
# # from flask_sqlalchemy import SQLAlchemy
# # from flask_migrate import Migrate
# # from flask_cors import CORS
# # from flask_jwt_extended import JWTManager
# # from .config import Config

# # db = SQLAlchemy()
# # migrate = Migrate()
# # jwt = JWTManager()

# # def create_app(config_class=Config):
# #     app = Flask(__name__)
# #     app.config.from_object(config_class)
    
# #     # Initialize extensions
# #     db.init_app(app)
# #     migrate.init_app(app, db)
# #     jwt.init_app(app)
# #     CORS(app)
    
# #     # Import and register blueprints
# #     from app.auth.routes import auth_bp
# #     from app.devices.routes import devices_bp
# #     from app.inventory.routes import inventory_bp
# #     from app.provisioning.routes import provisioning_bp
# #     from app.reports.routes import reports_bp
# #     from app.telemetry.routes import telemetry_bp
    
# #     app.register_blueprint(auth_bp, url_prefix='/api/auth')
# #     app.register_blueprint(devices_bp, url_prefix='/api/devices')
# #     app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
# #     app.register_blueprint(provisioning_bp, url_prefix='/api/provisioning')
# #     app.register_blueprint(reports_bp, url_prefix='/api/reports')
# #     app.register_blueprint(telemetry_bp, url_prefix='/api/telemetry')
    
# #     # Create database tables
# #     @app.before_first_request
# #     def create_tables():
# #         db.create_all()
    
# #     return app

# # # backend/app/config.py
# # import os
# # from datetime import timedelta

# # class Config:
# #     SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
# #     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@db:5432/network_lab'
# #     SQLALCHEMY_TRACK_MODIFICATIONS = False
# #     JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
# #     JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
# # # backend/app/auth/models.py
# # from app import db
# # from werkzeug.security import generate_password_hash, check_password_hash

# # class User(db.Model):
# #     __tablename__ = 'users'
    
# #     id = db.Column(db.Integer, primary_key=True)
# #     username = db.Column(db.String(64), unique=True, nullable=False)
# #     email = db.Column(db.String(120), unique=True, nullable=False)
# #     password_hash = db.Column(db.String(256), nullable=False)
# #     role = db.Column(db.String(20), default='user')
    
# #     def set_password(self, password):
# #         self.password_hash = generate_password_hash(password)
        
# #     def check_password(self, password):
# #         return check_password_hash(self.password_hash, password)

# # # backend/app/auth/routes.py
# # from flask import Blueprint, request, jsonify
# # from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
# # from app import db
# # from app.auth.models import User

# # auth_bp = Blueprint('auth', __name__)

# # @auth_bp.route('/login', methods=['POST'])
# # def login():
# #     data = request.get_json()
# #     username = data.get('username')
# #     password = data.get('password')
    
# #     user = User.query.filter_by(username=username).first()
    
# #     if user and user.check_password(password):
# #         access_token = create_access_token(identity=user.id)
# #         return jsonify(access_token=access_token), 200
    
# #     return jsonify(message="Invalid credentials"), 401

# # @auth_bp.route('/register', methods=['POST'])
# # def register():
# #     data = request.get_json()
# #     username = data.get('username')
# #     email = data.get('email')
# #     password = data.get('password')
    
# #     if User.query.filter_by(username=username).first():
# #         return jsonify(message="Username already exists"), 400
    
# #     if User.query.filter_by(email=email).first():
# #         return jsonify(message="Email already exists"), 400
    
# #     user = User(username=username, email=email)
# #     user.set_password(password)
    
# #     db.session.add(user)
# #     db.session.commit()
    
# #     return jsonify(message="User registered successfully"), 201

# # @auth_bp.route('/profile', methods=['GET'])
# # @jwt_required()
# # def profile():
# #     current_user_id = get_jwt_identity()
# #     user = User.query.get(current_user_id)
    
# #     return jsonify(
# #         id=user.id,
# #         username=user.username,
# #         email=user.email,
# #         role=user.role
# #     ), 200

# # # backend/app/devices/models.py
# # from app import db
# # from datetime import datetime

# # class Device(db.Model):
# #     __tablename__ = 'devices'
    
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(100), nullable=False)
# #     device_type = db.Column(db.String(50), nullable=False)
# #     ip_address = db.Column(db.String(15), nullable=False)
# #     username = db.Column(db.String(50))
# #     password = db.Column(db.String(100))
# #     ssh_port = db.Column(db.Integer, default=22)
# #     status = db.Column(db.String(20), default='inactive')
# #     created_at = db.Column(db.DateTime, default=datetime.utcnow)
# #     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
# #     # Relationships
# #     ports = db.relationship('Port', backref='device', lazy=True, cascade="all, delete-orphan")
    
# #     def to_dict(self):
# #         return {
# #             'id': self.id,
# #             'name': self.name,
# #             'device_type': self.device_type,
# #             'ip_address': self.ip_address,
# #             'ssh_port': self.ssh_port,
# #             'status': self.status,
# #             'ports': [port.to_dict() for port in self.ports],
# #             'created_at': self.created_at.isoformat(),
# #             'updated_at': self.updated_at.isoformat()
# #         }

# # class Port(db.Model):
# #     __tablename__ = 'ports'
    
# #     id = db.Column(db.Integer, primary_key=True)
# #     device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
# #     name = db.Column(db.String(50), nullable=False)
# #     port_type = db.Column(db.String(20), nullable=False)
# #     status = db.Column(db.String(20), default='down')
# #     connected_to_port_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=True)
    
# #     def to_dict(self):
# #         return {
# #             'id': self.id,
# #             'device_id': self.device_id,
# #             'name': self.name,
# #             'port_type': self.port_type,
# #             'status': self.status,
# #             'connected_to_port_id': self.connected_to_port_id
# #         }

# # # backend/app/devices/routes.py
# # from flask import Blueprint, request, jsonify
# # from flask_jwt_extended import jwt_required
# # from app import db
# # from app.devices.models import Device, Port

# # devices_bp = Blueprint('devices', __name__)

# # @devices_bp.route('/', methods=['GET'])
# # @jwt_required()
# # def get_devices():
# #     devices = Device.query.all()
# #     return jsonify([device.to_dict() for device in devices]), 200

# # @devices_bp.route('/<int:id>', methods=['GET'])
# # @jwt_required()
# # def get_device(id):
# #     device = Device.query.get_or_404(id)
# #     return jsonify(device.to_dict()), 200

# # @devices_bp.route('/', methods=['POST'])
# # @jwt_required()
# # def create_device():
# #     data = request.get_json()
    
# #     device = Device(
# #         name=data['name'],
# #         device_type=data['device_type'],
# #         ip_address=data['ip_address'],
# #         username=data.get('username'),
# #         password=data.get('password'),
# #         ssh_port=data.get('ssh_port', 22),
# #         status=data.get('status', 'inactive')
# #     )
    
# #     db.session.add(device)
# #     db.session.commit()
    
# #     # Create default ports based on device type
# #     if device.device_type == 'router':
# #         ports = [
# #             Port(device_id=device.id, name=f"GigabitEthernet0/{i}", port_type="ethernet", status="down")
# #             for i in range(4)
# #         ]
# #         db.session.bulk_save_objects(ports)
# #         db.session.commit()
    
# #     return jsonify(device.to_dict()), 201

# # @devices_bp.route('/<int:id>', methods=['PUT'])
# # @jwt_required()
# # def update_device(id):
# #     device = Device.query.get_or_404(id)
# #     data = request.get_json()
    
# #     device.name = data.get('name', device.name)
# #     device.device_type = data.get('device_type', device.device_type)
# #     device.ip_address = data.get('ip_address', device.ip_address)
# #     device.username = data.get('username', device.username)
# #     if 'password' in data:
# #         device.password = data['password']
# #     device.ssh_port = data.get('ssh_port', device.ssh_port)
# #     device.status = data.get('status', device.status)
    
# #     db.session.commit()
    
# #     return jsonify(device.to_dict()), 200

# # @devices_bp.route('/<int:id>', methods=['DELETE'])
# # @jwt_required()
# # def delete_device(id):
# #     device = Device.query.get_or_404(id)
# #     db.session.delete(device)
# #     db.session.commit()
    
# #     return jsonify(message="Device deleted"), 200

# # @devices_bp.route('/<int:device_id>/ports', methods=['GET'])
# # @jwt_required()
# # def get_device_ports(device_id):
# #     device = Device.query.get_or_404(device_id)
# #     return jsonify([port.to_dict() for port in device.ports]), 200

# # @devices_bp.route('/<int:device_id>/ports', methods=['POST'])
# # @jwt_required()
# # def create_port(device_id):
# #     device = Device.query.get_or_404(device_id)
# #     data = request.get_json()
    
# #     port = Port(
# #         device_id=device_id,
# #         name=data['name'],
# #         port_type=data['port_type'],
# #         status=data.get('status', 'down')
# #     )
    
# #     db.session.add(port)
# #     db.session.commit()
    
# #     return jsonify(port.to_dict()), 201

# # @devices_bp.route('/ports/<int:port_id>/connect', methods=['POST'])
# # @jwt_required()
# # def connect_ports(port_id):
# #     data = request.get_json()
# #     target_port_id = data.get('target_port_id')
    
# #     port = Port.query.get_or_404(port_id)
# #     target_port = Port.query.get_or_404(target_port_id)
    
# #     port.connected_to_port_id = target_port_id
# #     target_port.connected_to_port_id = port_id
    
# #     port.status = 'up'
# #     target_port.status = 'up'
    
# #     db.session.commit()
    
# #     return jsonify(message="Ports connected successfully"), 200

# # @devices_bp.route('/ports/<int:port_id>/disconnect', methods=['POST'])
# # @jwt_required()
# # def disconnect_ports(port_id):
# #     port = Port.query.get_or_404(port_id)
    
# #     if port.connected_to_port_id:
# #         target_port = Port.query.get(port.connected_to_port_id)
# #         if target_port:
# #             target_port.connected_to_port_id = None
# #             target_port.status = 'down'
    
# #     port.connected_to_port_id = None
# #     port.status = 'down'
    
# #     db.session.commit()
    
# #     return jsonify(message="Port disconnected successfully"), 200

# # # backend/run.py
# # from app import create_app

# # app = create_app()

# # if __name__ == '__main__':
# #     app.run(host='0.0.0.0', port=5000, debug=True)


# # backend/app/__init__.py
# from flask import Flask, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# import logging
# from logging.handlers import RotatingFileHandler
# import os
# from datetime import timedelta

# # Extensions
# db = SQLAlchemy()
# migrate = Migrate()
# jwt = JWTManager()
# limiter = Limiter(key_func=get_remote_address)

# def create_app(config_name='development'):
#     """Application factory pattern"""
#     app = Flask(__name__)
    
#     # Load configuration
#     from app.config import config
#     app.config.from_object(config[config_name])
    
#     # Initialize extensions
#     db.init_app(app)
#     migrate.init_app(app, db)
#     jwt.init_app(app)
#     limiter.init_app(app)
    
#     # CORS configuration
#     CORS(app, origins=app.config.get('CORS_ORIGINS', ['http://localhost:3232']))
    
#     # JWT configuration
#     app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
#     app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
#     # Register blueprints
#     from app.auth import bp as auth_bp
#     app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
#     from app.devices import bp as devices_bp
#     app.register_blueprint(devices_bp, url_prefix='/api/devices')
    
#     from app.inventory import bp as inventory_bp
#     app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    
#     from app.provisioning import bp as provisioning_bp
#     app.register_blueprint(provisioning_bp, url_prefix='/api/provisioning')
    
#     from app.telemetry import bp as telemetry_bp
#     app.register_blueprint(telemetry_bp, url_prefix='/api/telemetry')
    
#     from app.reports import bp as reports_bp
#     app.register_blueprint(reports_bp, url_prefix='/api/reports')
    
#     from app.topology import bp as topology_bp
#     app.register_blueprint(topology_bp, url_prefix='/api/topology')
    
#     # Error handlers
#     register_error_handlers(app)
    
#     # Health check endpoint
#     @app.route('/api/health')
#     def health_check():
#         return jsonify({
#             'status': 'healthy',
#             'version': '1.0.0',
#             'timestamp': datetime.utcnow().isoformat()
#         })
    
#     # Initialize logging
#     if not app.debug and not app.testing:
#         setup_logging(app)
    
#     return app

# def register_error_handlers(app):
#     """Register error handlers"""
    
#     @app.errorhandler(400)
#     def bad_request(error):
#         return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
#     @app.errorhandler(401)
#     def unauthorized(error):
#         return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
#     @app.errorhandler(403)
#     def forbidden(error):
#         return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403
    
#     @app.errorhandler(404)
#     def not_found(error):
#         return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
#     @app.errorhandler(429)
#     def rate_limit_exceeded(error):
#         return jsonify({'error': 'Rate limit exceeded', 'message': str(error)}), 429
    
#     @app.errorhandler(500)
#     def internal_error(error):
#         db.session.rollback()
#         return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

# def setup_logging(app):
#     """Setup logging for production"""
#     if not os.path.exists('logs'):
#         os.mkdir('logs')
    
#     file_handler = RotatingFileHandler(
#         'logs/network_lab.log', 
#         maxBytes=10240000, 
#         backupCount=10
#     )
#     file_handler.setFormatter(logging.Formatter(
#         '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
#     ))
#     file_handler.setLevel(logging.INFO)
#     app.logger.addHandler(file_handler)
    
#     app.logger.setLevel(logging.INFO)
#     app.logger.info('Network Lab application startup')

# # backend/app/config.py
# import os
# from datetime import timedelta

# basedir = os.path.abspath(os.path.dirname(__file__))

# class Config:
#     """Base configuration"""
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
#     JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
#     JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
#     # Rate limiting
#     RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    
#     # CORS
#     CORS_ORIGINS = ['http://localhost:3232', 'http://127.0.0.1:3232']
    
#     # Celery
#     CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
#     CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    
#     # File uploads
#     MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
#     UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
#     # Network timeouts
#     SSH_TIMEOUT = 30
#     SNMP_TIMEOUT = 10
    
#     @staticmethod
#     def init_app(app):
#         pass

# class DevelopmentConfig(Config):
#     """Development configuration"""
#     DEBUG = True
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
#         'postgresql://postgres:postgres@localhost:5432/network_lab_dev'

# class TestingConfig(Config):
#     """Testing configuration"""
#     TESTING = True
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
#     WTF_CSRF_ENABLED = False

# class ProductionConfig(Config):
#     """Production configuration"""
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
#         'postgresql://postgres:postgres@localhost:5432/network_lab'
    
#     @classmethod
#     def init_app(cls, app):
#         Config.init_app(app)
        
#         # Log to syslog
#         import logging
#         from logging.handlers import SysLogHandler
#         syslog_handler = SysLogHandler()
#         syslog_handler.setLevel(logging.WARNING)
#         app.logger.addHandler(syslog_handler)

# config = {
#     'development': DevelopmentConfig,
#     'testing': TestingConfig,
#     'production': ProductionConfig,
#     'default': DevelopmentConfig
# }

# # backend/run.py
# import os
# from flask.cli import with_appcontext
# import click
# from app import create_app, db
# from app.models import User
# from werkzeug.security import generate_password_hash

# app = create_app(os.getenv('FLASK_CONFIG') or 'development')

# @app.cli.command()
# @click.argument('username')
# @click.argument('email')
# @click.argument('password')
# @click.option('--role', default='admin', help='User role (admin, operator, viewer)')
# def create_user(username, email, password, role):
#     """Create a new user"""
#     user = User(
#         username=username,
#         email=email,
#         role=role
#     )
#     user.set_password(password)
    
#     try:
#         db.session.add(user)
#         db.session.commit()
#         click.echo(f'User {username} created successfully')
#     except Exception as e:
#         db.session.rollback()
#         click.echo(f'Error creating user: {str(e)}')

# @app.cli.command()
# def init_db():
#     """Initialize the database"""
#     db.create_all()
    
#     # Create default admin user if it doesn't exist
#     admin = User.query.filter_by(username='admin').first()
#     if not admin:
#         admin = User(
#             username='admin',
#             email='admin@networklab.com',
#             role='admin'
#         )
#         admin.set_password('admin')
#         db.session.add(admin)
#         db.session.commit()
#         click.echo('Default admin user created (username: admin, password: admin)')
    
#     click.echo('Database initialized successfully')

# @app.cli.command()
# def reset_db():
#     """Reset the database"""
#     if click.confirm('Are you sure you want to reset the database?'):
#         db.drop_all()
#         db.create_all()
#         click.echo('Database reset successfully')

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     host = os.environ.get('HOST', '0.0.0.0')
#     debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
#     app.run(host=host, port=port, debug=debug)

# # backend/requirements.txt
# Flask==2.3.3
# Flask-SQLAlchemy==3.0.5
# Flask-Migrate==4.0.5
# Flask-CORS==4.0.0
# Flask-JWT-Extended==4.5.3
# Flask-Limiter==3.5.0
# psycopg2-binary==2.9.7
# redis==4.6.0
# celery==5.3.1
# paramiko==3.3.1
# netmiko==4.2.0
# pysnmp==5.0.21
# jinja2==3.1.2
# requests==2.31.0
# python-dotenv==1.0.0
# gunicorn==21.2.0
# SQLAlchemy==2.0.21
# Werkzeug==2.3.7
# marshmallow==3.20.1
# python-dateutil==2.8.2
# schedule==1.2.0
# cryptography==41.0.4
# bcrypt==4.0.1

# # backend/app/models.py
# from datetime import datetime
# from app import db
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_jwt_extended import create_access_token
# import json

# class User(db.Model):
#     """User model for authentication"""
#     __tablename__ = 'users'
    
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, nullable=False, index=True)
#     email = db.Column(db.String(120), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(256), nullable=False)
#     role = db.Column(db.String(20), default='user')
#     is_active = db.Column(db.Boolean, default=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     last_login = db.Column(db.DateTime)
    
#     def set_password(self, password):
#         """Hash and set password"""
#         self.password_hash = generate_password_hash(password)
    
#     def check_password(self, password):
#         """Check password against hash"""
#         return check_password_hash(self.password_hash, password)
    
#     def get_token(self):
#         """Generate JWT token"""
#         return create_access_token(identity=self.id)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'username': self.username,
#             'email': self.email,
#             'role': self.role,
#             'is_active': self.is_active,
#             'created_at': self.created_at.isoformat(),
#             'last_login': self.last_login.isoformat() if self.last_login else None
#         }
    
#     def __repr__(self):
#         return f'<User {self.username}>'

# class Device(db.Model):
#     """Network device model"""
#     __tablename__ = 'devices'
    
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False, index=True)
#     device_type = db.Column(db.String(50), nullable=False, index=True)
#     ip_address = db.Column(db.String(15), nullable=False, unique=True, index=True)
#     username = db.Column(db.String(50))
#     password = db.Column(db.String(255))  # Encrypted
#     ssh_port = db.Column(db.Integer, default=22)
#     snmp_community = db.Column(db.String(100), default='public')
#     snmp_version = db.Column(db.String(10), default='2c')
#     status = db.Column(db.String(20), default='inactive', index=True)
#     location = db.Column(db.String(255))
#     description = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     last_seen = db.Column(db.DateTime)
    
#     # Relationships
#     ports = db.relationship('Port', backref='device', lazy=True, cascade="all, delete-orphan")
#     inventory_items = db.relationship('Inventory', backref='device', lazy=True, cascade="all, delete-orphan")
#     telemetry_configs = db.relationship('TelemetryConfig', backref='device', lazy=True, cascade="all, delete-orphan")
#     telemetry_data = db.relationship('TelemetryData', backref='device', lazy=True, cascade="all, delete-orphan")
#     provisioning_tasks = db.relationship('ProvisioningTask', backref='device', lazy=True, cascade="all, delete-orphan")
    
#     def to_dict(self, include_credentials=False):
#         data = {
#             'id': self.id,
#             'name': self.name,
#             'device_type': self.device_type,
#             'ip_address': self.ip_address,
#             'ssh_port': self.ssh_port,
#             'snmp_community': self.snmp_community if include_credentials else '***',
#             'snmp_version': self.snmp_version,
#             'status': self.status,
#             'location': self.location,
#             'description': self.description,
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat(),
#             'last_seen': self.last_seen.isoformat() if self.last_seen else None,
#             'ports': [port.to_dict() for port in self.ports]
#         }
        
#         if include_credentials:
#             data['username'] = self.username
#             # Never include plain password in serialization
        
#         return data
    
#     def __repr__(self):
#         return f'<Device {self.name} ({self.ip_address})>'

# class Port(db.Model):
#     """Device port model"""
#     __tablename__ = 'ports'
    
#     id = db.Column(db.Integer, primary_key=True)
#     device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
#     name = db.Column(db.String(50), nullable=False)
#     port_type = db.Column(db.String(20), nullable=False)
#     status = db.Column(db.String(20), default='down')
#     admin_status = db.Column(db.String(20), default='up')
#     speed = db.Column(db.String(20))
#     duplex = db.Column(db.String(10))
#     mtu = db.Column(db.Integer, default=1500)
#     vlan_id = db.Column(db.Integer)
#     mac_address = db.Column(db.String(17))
#     description = db.Column(db.String(255))
#     connected_to_port_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Self-referential relationship for connections
#     connected_port = db.relationship('Port', remote_side=[id], backref='connected_from')
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'device_id': self.device_id,
#             'name': self.name,
#             'port_type': self.port_type,
#             'status': self.status,
#             'admin_status': self.admin_status,
#             'speed': self.speed,
#             'duplex': self.duplex,
#             'mtu': self.mtu,
#             'vlan_id': self.vlan_id,
#             'mac_address': self.mac_address,
#             'description': self.description,
#             'connected_to_port_id': self.connected_to_port_id,
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat()
#         }
    
#     def __repr__(self):
#         return f'<Port {self.name} on Device {self.device_id}>'













# # backend/app/__init__.py
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# import logging
# from logging.handlers import RotatingFileHandler
# import os


# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# from celery import Celery


# # Initialize extensions
# db = SQLAlchemy()
# migrate = Migrate()
# jwt = JWTManager()
# limiter = Limiter(key_func=get_remote_address)

# def make_celery(app):
#     """Create Celery instance with Flask app context."""
#     celery = Celery(
#         app.import_name,
#         backend=app.config.get('CELERY_RESULT_BACKEND'),
#         broker=app.config.get('CELERY_BROKER_URL')
#     )
    
#     celery.conf.update(
#         task_serializer='json',
#         accept_content=['json'],
#         result_serializer='json',
#         timezone='UTC',
#         enable_utc=True,
#         result_expires=3600,
#         task_routes={
#             'app.tasks.*': {'queue': 'default'},
#         }
#     )
    
#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
    
#     celery.Task = ContextTask
#     return celery

# def create_app(config_name='default'):
#     """Application factory pattern"""
#     app = Flask(__name__)
#     app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
#         'postgresql://postgres:postgres@localhost:5432/network_lab')
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret')
    
#     # Load configuration
#     from app.config import config
#     app.config.from_object(config[config_name])
    
#     # Initialize extensions
#     db.init_app(app)
#     migrate.init_app(app, db)
#     jwt.init_app(app)
#     CORS(app, origins=['http://localhost:3232', 'http://127.0.0.1:3232'])
    
    
#      # Import models (after db is initialized)
#     from app.models import Device, Port
    
#     # Register blueprints
#     from app.auth.routes import auth_bp
#     from app.devices.routes import devices_bp
#     from app.inventory.routes import inventory_bp
#     from app.provisioning.routes import provisioning_bp
#     from app.telemetry.routes import telemetry_bp
#     from app.reports.routes import reports_bp
#     from app.topology.routes import topology_bp
    
#     app.register_blueprint(auth_bp, url_prefix='/api/auth')
#     app.register_blueprint(devices_bp, url_prefix='/api/devices')
#     app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
#     app.register_blueprint(provisioning_bp, url_prefix='/api/provisioning')
#     app.register_blueprint(telemetry_bp, url_prefix='/api/telemetry')
#     app.register_blueprint(reports_bp, url_prefix='/api/reports')
#     app.register_blueprint(topology_bp, url_prefix='/api/topology')
    
#     # Error handlers
#     @app.errorhandler(404)
#     def not_found(error):
#         return {'message': 'Resource not found'}, 404
    
#     @app.errorhandler(500)
#     def internal_error(error):
#         db.session.rollback()
#         return {'message': 'Internal server error'}, 500
    
#     # Health check endpoint
#     # @app.route('/api/health')
#     # def health_check():
#     #     # return {'status': 'healthy', 'timestamp': db.func.now()}
#     #     return {'status': 'healthy', 'service': 'backend'}, 200
#     # Health check route
#     @app.route('/api/health')
#     def health_check():
#         try:
#             # Test database connection
#             db.session.execute('SELECT 1')
#             db_status = 'healthy'
#         except Exception as e:
#             db_status = f'error: {str(e)}'
        
#         try:
#             # Test Redis connection if available
#             if app.celery:
#                 redis_status = 'healthy'
#             else:
#                 redis_status = 'not_configured'
#         except Exception as e:
#             redis_status = f'error: {str(e)}'
        
#         return {
#             'status': 'healthy',
#             'service': 'backend',
#             'database': db_status,
#             'redis': redis_status,
#             'environment': os.getenv('FLASK_ENV', 'development')
#         }, 200
    
#     # API info endpoint
#     @app.route('/api/info')
#     def api_info():
#         return {
#             'name': 'Network Lab Automation API',
#             'version': '1.0.0',
#             'description': 'RESTful API for network lab automation and management'
#         }

#      # Create tables
#     with app.app_context():
#         # Clear any existing metadata to avoid conflicts
#         db.metadata.clear()
        
#         # Import models
#         from app.models import Device, Port
        
#         # Create tables
#         try:
#             db.create_all()
#         except Exception as e:
#             print(f"Database error (continuing anyway): {e}")
    
    
#     # Configure logging
#     if not app.debug and not app.testing:
#         if not os.path.exists('logs'):
#             os.mkdir('logs')
        
#         file_handler = RotatingFileHandler(
#             'logs/network_lab.log', 
#             maxBytes=10240000, 
#             backupCount=10
#         )
#         file_handler.setFormatter(logging.Formatter(
#             '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
#         ))
#         file_handler.setLevel(logging.INFO)
#         app.logger.addHandler(file_handler)
        
#         app.logger.setLevel(logging.INFO)
#         app.logger.info('Network Lab Automation startup')
    
#     return app