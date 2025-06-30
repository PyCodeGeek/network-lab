# backend/app/telemetry/models.py
from app import db
from datetime import datetime
import json

class TelemetryConfig(db.Model):
    __tablename__ = 'telemetry_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    metrics = db.Column(db.Text) # JSON array of metrics to collect
    collection_interval = db.Column(db.Integer, default=60) # seconds
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    device = db.relationship('Device', backref='telemetry_config', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'metrics': json.loads(self.metrics) if self.metrics else [],
            'collection_interval': self.collection_interval,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class TelemetryData(db.Model):
    __tablename__ = 'telemetry_data'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    metric = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    device = db.relationship('Device', backref='telemetry_data', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'metric': self.metric,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat()
        }









