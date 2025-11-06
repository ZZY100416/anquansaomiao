from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.rasp_event import RASPEvent
from app.scanners.rasp_scanner import RASPScanner
from datetime import datetime
import json

bp = Blueprint('rasp', __name__)

@bp.route('/status', methods=['GET'])
@jwt_required()
def get_rasp_status():
    """获取OpenRASP服务状态"""
    scanner = RASPScanner()
    status = scanner.get_rasp_status()
    return jsonify(status), 200

@bp.route('/events', methods=['GET'])
@jwt_required()
def get_rasp_events():
    """获取RASP事件列表"""
    app_id = request.args.get('app_id')
    severity = request.args.get('severity')
    handled = request.args.get('handled')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = RASPEvent.query
    
    if app_id:
        query = query.filter(RASPEvent.app_id == app_id)
    if severity:
        query = query.filter(RASPEvent.severity == severity)
    if handled is not None:
        query = query.filter(RASPEvent.handled == (handled.lower() == 'true'))
    if start_time:
        query = query.filter(RASPEvent.event_time >= datetime.fromisoformat(start_time))
    if end_time:
        query = query.filter(RASPEvent.event_time <= datetime.fromisoformat(end_time))
    
    # 按时间倒序排列
    query = query.order_by(RASPEvent.event_time.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'events': [e.to_dict() for e in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@bp.route('/events/<int:event_id>', methods=['GET'])
@jwt_required()
def get_rasp_event(event_id):
    """获取RASP事件详情"""
    event = RASPEvent.query.get(event_id)
    if not event:
        return jsonify({'error': '事件不存在'}), 404
    
    return jsonify(event.to_dict()), 200

@bp.route('/events/<int:event_id>/handle', methods=['POST'])
@jwt_required()
def handle_rasp_event(event_id):
    """标记RASP事件为已处理"""
    user_id = int(get_jwt_identity())  # 转换为整数
    event = RASPEvent.query.get(event_id)
    
    if not event:
        return jsonify({'error': '事件不存在'}), 404
    
    event.handled = True
    event.handled_at = datetime.utcnow()
    event.handled_by = user_id
    
    db.session.commit()
    
    return jsonify({'message': '事件已标记为已处理', 'event': event.to_dict()}), 200

@bp.route('/events/sync', methods=['POST'])
@jwt_required()
def sync_rasp_events():
    """从OpenRASP同步事件"""
    data = request.get_json() or {}
    app_id = data.get('app_id', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    
    scanner = RASPScanner()
    
    # 创建临时扫描对象
    from app.models.scan import Scan
    temp_scan = Scan()
    temp_scan.config = json.dumps({
        'app_id': app_id,
        'start_time': start_time,
        'end_time': end_time
    })
    
    events = scanner.scan(temp_scan)
    
    # 保存事件到数据库
    synced_count = 0
    for event_data in events:
        event_id = event_data.get('raw_data', {}).get('event_id')
        if event_id:
            # 检查事件是否已存在
            existing = RASPEvent.query.filter_by(event_id=event_id).first()
            if not existing:
                event = RASPEvent(
                    app_id=event_data.get('raw_data', {}).get('app_id', app_id),
                    event_id=event_id,
                    attack_type=event_data.get('type', ''),
                    severity=event_data.get('severity', 'medium'),
                    message=event_data.get('title', ''),
                    url=event_data.get('raw_data', {}).get('url', ''),
                    client_ip=event_data.get('raw_data', {}).get('client_ip', ''),
                    user_agent=event_data.get('raw_data', {}).get('user_agent', ''),
                    request_id=event_data.get('raw_data', {}).get('request_id', ''),
                    file_path=event_data.get('file_path', ''),
                    line_number=event_data.get('line_number'),
                    attack_params=json.dumps(event_data.get('raw_data', {}).get('attack_params', {})),
                    stack_trace=event_data.get('raw_data', {}).get('stack_trace', ''),
                    raw_data=json.dumps(event_data.get('raw_data', {})),
                    event_time=datetime.utcnow()
                )
                db.session.add(event)
                synced_count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'成功同步 {synced_count} 个事件',
        'synced_count': synced_count
    }), 200

