# # backend/app/config.py
# import os
# from datetime import timedelta

# class Config:
#     # Flask Configuration
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
#     # Database Configuration
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost:5432/network_lab'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SQLALCHEMY_ENGINE_OPTIONS = {
#         'pool_size': 10,
#         'pool_recycle': 120,
#         'pool_pre_ping': True
#     }
    
#     # JWT Configuration
#     JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
#     JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
#     JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
#     # Redis Configuration
#     REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
#     # Celery Configuration
#     CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
#     CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    
#     # Network Device Defaults
#     DEFAULT_SSH_PORT = 22
#     DEFAULT_SNMP_PORT = 161
#     CONNECTION_TIMEOUT = 30
    
#     # File Upload Configuration
#     MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
#     UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
#     # Logging Configuration
#     LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
#     LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'

# class DevelopmentConfig(Config):
#     DEBUG = True
#     SQLALCHEMY_ECHO = True

# class ProductionConfig(Config):
#     DEBUG = False
#     SQLALCHEMY_ECHO = False
    
# class TestingConfig(Config):
#     TESTING = True
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# # Configuration dictionary
# config = {
#     'development': DevelopmentConfig,
#     'production': ProductionConfig,
#     'testing': TestingConfig,
#     'default': DevelopmentConfig
# }






# backend/config.py - Updated configuration
# ==========================================

import os
from datetime import timedelta

class Config:
    """Base configuration."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/network_lab'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 20
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    
    # Flask-Limiter Configuration
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or 'redis://localhost:6379/1'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Application Configuration
    APP_NAME = os.environ.get('APP_NAME', 'Network Lab Automation')
    API_VERSION = os.environ.get('API_VERSION', 'v1')
    
    # Network Device Configuration
    DEFAULT_DEVICE_USERNAME = os.environ.get('DEFAULT_DEVICE_USERNAME', 'admin')
    DEFAULT_DEVICE_PASSWORD = os.environ.get('DEFAULT_DEVICE_PASSWORD', 'admin')
    
    # Telemetry Configuration
    TELEMETRY_RETENTION_DAYS = int(os.environ.get('TELEMETRY_RETENTION_DAYS', 30))
    TELEMETRY_COLLECTION_INTERVAL = int(os.environ.get('TELEMETRY_COLLECTION_INTERVAL', 60))
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3232').split(',')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
    # Development specific settings
    SQLALCHEMY_ECHO = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to console in development
        import logging
        from logging import StreamHandler
        
        handler = StreamHandler()
        handler.setLevel(logging.DEBUG)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.DEBUG)

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # Security settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to file in production
        import logging
        from logging.handlers import RotatingFileHandler
        import os
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        file_handler = RotatingFileHandler(
            'logs/network_lab.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Network Lab startup')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=1)

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}