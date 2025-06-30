
# # backend/app/reports/models.py
# from app import db
# from datetime import datetime
# import json

# class Report(db.Model):
#     __tablename__ = 'reports'
    
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     report_type = db.Column(db.String(50), nullable=False)
#     parameters = db.Column(db.Text)  # JSON parameters for report generation
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     generated_at = db.Column(db.DateTime)
#     status = db.Column(db.String(20), default='pending')  # pending, generating, completed, failed
#     result = db.Column(db.Text)  # Generated report content or error message
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'name': self.name,
#             'report_type': self.report_type,
#             'parameters': json.loads(self.parameters) if self.parameters else {},
#             'created_at': self.created_at.isoformat(),
#             'generated_at': self.generated_at.isoformat() if self.generated_at else None,
#             'status': self.status,
#             'result': self.result
#         }
        
        
# backend/app/reports/models.py
from app import db
from datetime import datetime
import json

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    report_type = db.Column(db.String(50), nullable=False, index=True)
    parameters = db.Column(db.Text)  # JSON parameters for report generation
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))  # Path to generated report file
    file_size = db.Column(db.Integer)  # File size in bytes
    format = db.Column(db.String(20), default='html')  # html, pdf, csv, json
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    generated_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, generating, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    result = db.Column(db.Text)  # Generated report content or error message
    error_message = db.Column(db.Text)
    
    # Relationships
    created_by_user = db.relationship('User', backref='reports', lazy=True)
    
    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'name': self.name,
            'report_type': self.report_type,
            'description': self.description,
            'parameters': json.loads(self.parameters) if self.parameters else {},
            'format': self.format,
            'file_size': self.file_size,
            'created_by': self.created_by_user.username if self.created_by_user else None,
            'created_at': self.created_at.isoformat(),
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'status': self.status,
            'progress': self.progress,
            'error_message': self.error_message
        }
        
        if include_content and self.result:
            data['content'] = self.result
        
        return data








