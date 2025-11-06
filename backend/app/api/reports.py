from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.scan import Scan, ScanResult
from app.models.project import Project
from app.services.report_service import ReportService
from app import db

bp = Blueprint('reports', __name__)

@bp.route('/<int:scan_id>', methods=['GET'])
@jwt_required()
def generate_report(scan_id):
    user_id = get_jwt_identity()
    scan = db.session.query(Scan).join(Project).filter(
        Scan.id == scan_id,
        Project.user_id == user_id
    ).first()
    
    if not scan:
        return jsonify({'error': '扫描任务不存在'}), 404
    
    report_type = request.args.get('type', 'html')  # html, pdf
    
    report_service = ReportService()
    
    if report_type == 'pdf':
        report_data = report_service.generate_pdf_report(scan_id)
        return report_data, 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename=scan_report_{scan_id}.pdf'
        }
    else:
        report_data = report_service.generate_html_report(scan_id)
        return jsonify(report_data), 200

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    from flask import request
    import sys
    # 直接输出到stderr，确保能看到日志
    print(f'[Dashboard] 请求到达 - Authorization头: {request.headers.get("Authorization", "未找到")}', file=sys.stderr)
    
    user_id = get_jwt_identity()
    print(f'[Dashboard] User ID: {user_id}', file=sys.stderr)
    
    # 获取用户所有项目
    projects = Project.query.filter_by(user_id=user_id).all()
    
    # 统计信息
    total_projects = len(projects)
    total_scans = db.session.query(Scan).join(Project).filter(
        Project.user_id == user_id
    ).count()
    
    completed_scans = db.session.query(Scan).join(Project).filter(
        Project.user_id == user_id,
        Scan.status == 'completed'
    ).count()
    
    # 漏洞统计
    results = db.session.query(ScanResult).join(Scan).join(Project).filter(
        Project.user_id == user_id
    ).all()
    
    severity_stats = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'info': 0
    }
    
    for result in results:
        if result.severity in severity_stats:
            severity_stats[result.severity] += 1
    
    return jsonify({
        'total_projects': total_projects,
        'total_scans': total_scans,
        'completed_scans': completed_scans,
        'severity_stats': severity_stats
    }), 200

