# backend/app/models.py
# from app import db
# from datetime import datetime

# class Device(db.Model):
#     __tablename__ = 'devices'
#     __table_args__ = {'extend_existing': True}  # Fix the SQLAlchemy error
    
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     device_type = db.Column(db.String(50), nullable=False)
#     ip_address = db.Column(db.String(15), nullable=False)
#     username = db.Column(db.String(50))
#     password = db.Column(db.String(100))
#     ssh_port = db.Column(db.Integer, default=22)
#     status = db.Column(db.String(20), default='inactive')
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     ports = db.relationship('Port', backref='device', lazy=True, cascade="all, delete-orphan")
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'name': self.name,
#             'device_type': self.device_type,
#             'ip_address': self.ip_address,
#             'ssh_port': self.ssh_port,
#             'status': self.status,
#             'ports': [port.to_dict() for port in self.ports],
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat()
#         }

# class Port(db.Model):
#     __tablename__ = 'ports'
#     __table_args__ = {'extend_existing': True}  # Fix the SQLAlchemy error
    
#     id = db.Column(db.Integer, primary_key=True)
#     device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
#     name = db.Column(db.String(50), nullable=False)
#     port_type = db.Column(db.String(20), nullable=False)
#     status = db.Column(db.String(20), default='down')
#     connected_to_port_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=True)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'device_id': self.device_id,
#             'name': self.name,
#             'port_type': self.port_type,
#             'status': self.status,
#             'connected_to_port_id': self.connected_to_port_id
#         }


from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False, index=True)
    ip_address = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))
    ssh_port = db.Column(db.Integer, default=22)
    status = db.Column(db.String(20), default='inactive', index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ports = db.relationship('Port', backref='device', lazy='dynamic', cascade="all, delete-orphan")
    
    def to_dict(self, include_ports=True):
        """Convert device to dictionary"""
        result = {
            'id': self.id,
            'name': self.name,
            'device_type': self.device_type,
            'ip_address': self.ip_address,
            'username': self.username,
            'ssh_port': self.ssh_port,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_ports:
            result['ports'] = [port.to_dict() for port in self.ports]
        
        return result
    
    def __repr__(self):
        return f'<Device {self.name}>'

class Port(db.Model):
    __tablename__ = 'ports'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    port_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='down')
    speed = db.Column(db.String(20))
    duplex = db.Column(db.String(10))
    description = db.Column(db.String(255))
    connected_to_port_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert port to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'port_type': self.port_type,
            'status': self.status,
            'speed': self.speed,
            'duplex': self.duplex,
            'description': self.description,
            'connected_to_port_id': self.connected_to_port_id,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Port {self.name} on Device {self.device_id}>'