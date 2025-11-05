from app import db
from datetime import datetime
import json

class Scan(db.Model):
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    scan_type = db.Column(db.String(50), nullable=False)  # sast, sca, container, rasp
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    config = db.Column(db.Text)  # JSON配置
    
    # 关联关系
    results = db.relationship('ScanResult', backref='scan', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'scan_type': self.scan_type,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'config': json.loads(self.config) if self.config else {},
            'result_count': len(self.results)
        }

class ScanResult(db.Model):
    __tablename__ = 'scan_results'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    severity = db.Column(db.String(20))  # critical, high, medium, low, info
    vulnerability_type = db.Column(db.String(100))
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    file_path = db.Column(db.String(1000))
    line_number = db.Column(db.Integer)
    cve_id = db.Column(db.String(50))
    package_name = db.Column(db.String(200))
    package_version = db.Column(db.String(50))
    fixed_version = db.Column(db.String(50))
    raw_data = db.Column(db.Text)  # JSON原始数据
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'severity': self.severity,
            'vulnerability_type': self.vulnerability_type,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'cve_id': self.cve_id,
            'package_name': self.package_name,
            'package_version': self.package_version,
            'fixed_version': self.fixed_version,
            'raw_data': json.loads(self.raw_data) if self.raw_data else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

