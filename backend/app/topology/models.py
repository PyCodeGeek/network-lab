# backend/app/topology/models.py
from app import db
from datetime import datetime
import json

class TopologyLayout(db.Model):
    __tablename__ = 'topology_layouts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    layout_data = db.Column(db.Text)  # JSON data for device positions and connections
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = db.relationship('User', backref='topology_layouts', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'layout_data': json.loads(self.layout_data) if self.layout_data else {},
            'is_default': self.is_default,
            'created_by': self.created_by_user.username if self.created_by_user else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
