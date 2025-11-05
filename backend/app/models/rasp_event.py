from app import db
from datetime import datetime
import json

class RASPEvent(db.Model):
    """
    OpenRASP运行时安全事件模型
    用于存储从OpenRASP获取的运行时安全事件
    """
    __tablename__ = 'rasp_events'
    
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.String(100))  # 应用ID
    event_id = db.Column(db.String(100), unique=True)  # OpenRASP事件ID
    attack_type = db.Column(db.String(100))  # 攻击类型
    severity = db.Column(db.String(20))  # 严重级别
    message = db.Column(db.Text)  # 事件消息
    url = db.Column(db.String(1000))  # 请求URL
    client_ip = db.Column(db.String(50))  # 客户端IP
    user_agent = db.Column(db.String(500))  # User Agent
    request_id = db.Column(db.String(100))  # 请求ID
    file_path = db.Column(db.String(1000))  # 文件路径
    line_number = db.Column(db.Integer)  # 行号
    attack_params = db.Column(db.Text)  # 攻击参数（JSON）
    stack_trace = db.Column(db.Text)  # 堆栈跟踪
    raw_data = db.Column(db.Text)  # 原始数据（JSON）
    event_time = db.Column(db.DateTime)  # 事件发生时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 记录创建时间
    handled = db.Column(db.Boolean, default=False)  # 是否已处理
    handled_at = db.Column(db.DateTime)  # 处理时间
    handled_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 处理人
    
    def to_dict(self):
        return {
            'id': self.id,
            'app_id': self.app_id,
            'event_id': self.event_id,
            'attack_type': self.attack_type,
            'severity': self.severity,
            'message': self.message,
            'url': self.url,
            'client_ip': self.client_ip,
            'user_agent': self.user_agent,
            'request_id': self.request_id,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'attack_params': json.loads(self.attack_params) if self.attack_params else {},
            'stack_trace': self.stack_trace,
            'raw_data': json.loads(self.raw_data) if self.raw_data else {},
            'event_time': self.event_time.isoformat() if self.event_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'handled': self.handled,
            'handled_at': self.handled_at.isoformat() if self.handled_at else None,
            'handled_by': self.handled_by
        }

