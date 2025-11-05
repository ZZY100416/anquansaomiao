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
    user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    
    query = db.session.query(Scan).join(Project).filter(Project.user_id == user_id)
    
    if project_id:
        query = query.filter(Scan.project_id == project_id)
    
    scans = query.all()
    
    return jsonify([s.to_dict() for s in scans]), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_scan():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('project_id') or not data.get('scan_type'):
        return jsonify({'error': '项目ID和扫描类型不能为空'}), 400
    
    project = Project.query.filter_by(id=data['project_id'], user_id=user_id).first()
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    scan = Scan(
        project_id=data['project_id'],
        scan_type=data['scan_type'],
        status='pending',
        config=json.dumps(data.get('config', {}))
    )
    
    db.session.add(scan)
    db.session.commit()
    
    # 异步执行扫描任务
    try:
        scanner_service = ScannerService()
        scanner_service.start_scan(scan.id)
    except Exception as e:
        scan.status = 'failed'
        db.session.commit()
        return jsonify({'error': f'启动扫描失败: {str(e)}'}), 500
    
    return jsonify(scan.to_dict()), 201

@bp.route('/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_scan(scan_id):
    user_id = get_jwt_identity()
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
    user_id = get_jwt_identity()
    scan = db.session.query(Scan).join(Project).filter(
        Scan.id == scan_id,
        Project.user_id == user_id
    ).first()
    
    if not scan:
        return jsonify({'error': '扫描任务不存在'}), 404
    
    results = ScanResult.query.filter_by(scan_id=scan_id).all()
    
    return jsonify([r.to_dict() for r in results]), 200

