# backend/app/provisioning/models.py
from app import db
from datetime import datetime
import json

class ConfigTemplate(db.Model):
    __tablename__ = 'config_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    variables = db.Column(db.Text)  # JSON string of variable definitions
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default='1.0')
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('ProvisioningTask', backref='template', lazy=True)
    created_by_user = db.relationship('User', backref='templates', lazy=True)
    
    def to_dict(self, include_content=True):
        data = {
            'id': self.id,
            'name': self.name,
            'device_type': self.device_type,
            'description': self.description,
            'version': self.version,
            'is_active': self.is_active,
            'variables': json.loads(self.variables) if self.variables else [],
            'created_by': self.created_by_user.username if self.created_by_user else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'usage_count': len(self.tasks)
        }
        
        if include_content:
            data['content'] = self.content
        
        return data

class ProvisioningTask(db.Model):
    __tablename__ = 'provisioning_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('config_templates.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, running, completed, failed, cancelled
    config_data = db.Column(db.Text)  # JSON data for template variables
    rendered_config = db.Column(db.Text)  # Final rendered configuration
    result = db.Column(db.Text)  # Execution result and logs
    progress = db.Column(db.Integer, default=0)  # 0-100
    error_message = db.Column(db.Text)
    rollback_config = db.Column(db.Text)  # Configuration for rollback
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    created_by_user = db.relationship('User', backref='provisioning_tasks', lazy=True)
    
    def to_dict(self, include_configs=False):
        data = {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'template_id': self.template_id,
            'template_name': self.template.name if self.template else 'Custom Configuration',
            'name': self.name,
            'status': self.status,
            'progress': self.progress,
            'error_message': self.error_message,
            'created_by': self.created_by_user.username if self.created_by_user else None,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.get_duration()
        }
        
        if include_configs:
            data['config_data'] = json.loads(self.config_data) if self.config_data else {}
            data['rendered_config'] = self.rendered_config
            data['result'] = self.result
            data['rollback_config'] = self.rollback_config
        
        return data
    
    def get_duration(self):
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            return str(duration).split('.')[0]  # Remove microseconds
        elif self.started_at:
            duration = datetime.utcnow() - self.started_at
            return str(duration).split('.')[0]
        return None

class ProvisioningLog(db.Model):
    __tablename__ = 'provisioning_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('provisioning_tasks.id'), nullable=False)
    level = db.Column(db.String(10), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    task = db.relationship('ProvisioningTask', backref='logs', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }



