from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.scan import Scan, ScanResult
from app.models.project import Project
from app.services.scanner_service import ScannerService
import json

bp = Blueprint('scans', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_scans():
    user_id = int(get_jwt_identity())  # 转换为整数
    project_id = request.args.get('project_id', type=int)
    
    query = db.session.query(Scan).join(Project).filter(Project.user_id == user_id)
    
    if project_id:
        query = query.filter(Scan.project_id == project_id)
    
    scans = query.all()
    
    return jsonify([s.to_dict() for s in scans]), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_scan():
    import sys
    user_id = int(get_jwt_identity())  # 转换为整数
    data = request.get_json()
    
    print(f'[Scan] 收到创建扫描任务请求: user_id={user_id}, data={data}', file=sys.stderr)
    
    if not data or not data.get('project_id') or not data.get('scan_type'):
        print(f'[Scan] 错误: 缺少必要参数', file=sys.stderr)
        return jsonify({'error': '项目ID和扫描类型不能为空'}), 400
    
    project = Project.query.filter_by(id=data['project_id'], user_id=user_id).first()
    if not project:
        print(f'[Scan] 错误: 项目不存在 project_id={data["project_id"]}, user_id={user_id}', file=sys.stderr)
        return jsonify({'error': '项目不存在'}), 404
    
    print(f'[Scan] 创建扫描任务: project_id={data["project_id"]}, scan_type={data["scan_type"]}', file=sys.stderr)
    
    scan = Scan(
        project_id=data['project_id'],
        scan_type=data['scan_type'],
        status='pending',
        config=json.dumps(data.get('config', {}))
    )
    
    db.session.add(scan)
    db.session.commit()
    
    print(f'[Scan] 扫描任务已创建: scan_id={scan.id}', file=sys.stderr)
    
    # 异步执行扫描任务（使用线程，避免阻塞HTTP响应）
    try:
        import threading
        from app import app
        
        # 保存scan_id，在后台线程中使用
        scan_id = scan.id
        
        def run_scan():
            # 在后台线程中，需要创建新的应用上下文
            with app.app_context():
                try:
                    print(f'[Scan] 开始执行扫描任务: scan_id={scan_id}', file=sys.stderr)
                    scanner_service = ScannerService()
                    scanner_service.start_scan(scan_id)
                    print(f'[Scan] 扫描任务执行完成: scan_id={scan_id}', file=sys.stderr)
                except Exception as e:
                    print(f'[Scan] 扫描执行失败: scan_id={scan_id}, error={str(e)}', file=sys.stderr)
                    import traceback
                    print(f'[Scan] 错误堆栈: {traceback.format_exc()}', file=sys.stderr)
                    # 更新扫描状态为失败
                    try:
                        failed_scan = Scan.query.get(scan_id)
                        if failed_scan:
                            failed_scan.status = 'failed'
                            from datetime import datetime
                            failed_scan.completed_at = datetime.utcnow()
                            db.session.commit()
                    except Exception as db_error:
                        print(f'[Scan] 更新扫描状态失败: {str(db_error)}', file=sys.stderr)
        
        # 在后台线程中执行扫描
        thread = threading.Thread(target=run_scan)
        thread.daemon = True
        thread.start()
        
        print(f'[Scan] 扫描任务已启动（后台执行）: scan_id={scan.id}', file=sys.stderr)
    except Exception as e:
        print(f'[Scan] 启动扫描失败: scan_id={scan.id}, error={str(e)}', file=sys.stderr)
        import traceback
        print(f'[Scan] 错误堆栈: {traceback.format_exc()}', file=sys.stderr)
        scan.status = 'failed'
        db.session.commit()
        return jsonify({'error': f'启动扫描失败: {str(e)}'}), 500
    
    return jsonify(scan.to_dict()), 201

@bp.route('/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_scan(scan_id):
    user_id = int(get_jwt_identity())  # 转换为整数
    scan = db.session.query(Scan).join(Project).filter(
        Scan.id == scan_id,
        Project.user_id == user_id
    ).first()
    
    if not scan:
        return jsonify({'error': '扫描任务不存在'}), 404
    
    return jsonify(scan.to_dict()), 200

@bp.route('/<int:scan_id>/results', methods=['GET'])
@jwt_required()
def get_scan_results(scan_id):
    user_id = int(get_jwt_identity())  # 转换为整数
    scan = db.session.query(Scan).join(Project).filter(
        Scan.id == scan_id,
        Project.user_id == user_id
    ).first()
    
    if not scan:
        return jsonify({'error': '扫描任务不存在'}), 404
    
    results = ScanResult.query.filter_by(scan_id=scan_id).all()
    
    return jsonify([r.to_dict() for r in results]), 200

