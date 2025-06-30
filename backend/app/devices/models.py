# backend/app/devices/models.py
from app import db
from datetime import datetime
import json

class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False, index=True)
    ip_address = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))  # Should be encrypted in production
    ssh_port = db.Column(db.Integer, default=22)
    snmp_community = db.Column(db.String(50), default='public')
    snmp_port = db.Column(db.Integer, default=161)
    status = db.Column(db.String(20), default='inactive', index=True)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ports = db.relationship('Port', backref='device', lazy=True, cascade="all, delete-orphan")
    inventory_items = db.relationship('Inventory', backref='device', lazy=True, cascade="all, delete-orphan")
    provisioning_tasks = db.relationship('ProvisioningTask', backref='device', lazy=True)
    telemetry_data = db.relationship('TelemetryData', backref='device', lazy=True)
    telemetry_config = db.relationship('TelemetryConfig', backref='device', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'name': self.name,
            'device_type': self.device_type,
            'ip_address': self.ip_address,
            'ssh_port': self.ssh_port,
            'snmp_port': self.snmp_port,
            'status': self.status,
            'location': self.location,
            'description': self.description,
            'ports': [port.to_dict() for port in self.ports],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data['username'] = self.username
            data['snmp_community'] = self.snmp_community
        
        return data
    
    def __repr__(self):
        return f'<Device {self.name}>'

class Port(db.Model):
    __tablename__ = 'ports'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    port_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='down')
    admin_status = db.Column(db.String(20), default='up')
    connected_to_port_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=True)
    speed = db.Column(db.String(20))
    duplex = db.Column(db.String(10))
    mtu = db.Column(db.Integer, default=1500)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for connections
    connected_to = db.relationship('Port', remote_side=[id], backref='connected_from')
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'port_type': self.port_type,
            'status': self.status,
            'admin_status': self.admin_status,
            'connected_to_port_id': self.connected_to_port_id,
            'speed': self.speed,
            'duplex': self.duplex,
            'mtu': self.mtu,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
        
    def __repr__(self):
        return f'<Port {self.name} on Device {self.device_id}>'