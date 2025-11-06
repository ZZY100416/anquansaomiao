from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models.project import Project
from app.models.user import User
import os
import zipfile
import shutil

bp = Blueprint('projects', __name__)

# 项目文件上传目录
UPLOAD_DIR = '/app/uploaded_files'

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

@bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = int(get_jwt_identity())  # 转换为整数
    projects = Project.query.filter_by(user_id=user_id).all()
    
    return jsonify([p.to_dict() for p in projects]), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    user_id = int(get_jwt_identity())  # 转换为整数
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': '项目名称不能为空'}), 400
    
    project = Project(
        name=data['name'],
        description=data.get('description', ''),
        repository_url=data.get('repository_url', ''),
        project_type=data.get('project_type', ''),
        user_id=user_id
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify(project.to_dict()), 201

@bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    user_id = int(get_jwt_identity())  # 转换为整数
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    return jsonify(project.to_dict()), 200

@bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    user_id = int(get_jwt_identity())  # 转换为整数
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    data = request.get_json()
    if data.get('name'):
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'repository_url' in data:
        project.repository_url = data['repository_url']
    if 'project_type' in data:
        project.project_type = data['project_type']
    
    db.session.commit()
    
    return jsonify(project.to_dict()), 200

@bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    user_id = int(get_jwt_identity())  # 转换为整数
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    # 删除项目文件目录
    project_dir = os.path.join(UPLOAD_DIR, f'project_{project_id}')
    if os.path.exists(project_dir):
        try:
            shutil.rmtree(project_dir)
        except Exception as e:
            print(f"删除项目目录失败: {str(e)}")
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': '项目删除成功'}), 200

@bp.route('/<int:project_id>/upload', methods=['POST'])
@jwt_required()
def upload_project_files(project_id):
    """上传项目文件"""
    import sys
    user_id = int(get_jwt_identity())  # 转换为整数
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        print(f"[Upload] 错误: 项目不存在 project_id={project_id}, user_id={user_id}", file=sys.stderr)
        return jsonify({'error': '项目不存在'}), 404
    
    # 检查是否有文件上传
    print(f"[Upload] 请求文件: {list(request.files.keys())}", file=sys.stderr)
    if 'file' not in request.files:
        print(f"[Upload] 错误: 没有上传文件", file=sys.stderr)
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    print(f"[Upload] 收到文件: {file.filename}, 大小: {file.content_length if hasattr(file, 'content_length') else 'unknown'}", file=sys.stderr)
    
    if file.filename == '':
        print(f"[Upload] 错误: 文件名为空", file=sys.stderr)
        return jsonify({'error': '文件名为空'}), 400
    
    # 确保上传目录存在
    if not os.path.exists(UPLOAD_DIR):
        print(f"[Upload] 创建上传目录: {UPLOAD_DIR}", file=sys.stderr)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        # 设置权限（如果可能）
        try:
            os.chmod(UPLOAD_DIR, 0o777)
        except:
            pass
    
    # 创建项目目录
    project_dir = os.path.join(UPLOAD_DIR, f'project_{project_id}')
    print(f"[Upload] 创建项目目录: {project_dir}", file=sys.stderr)
    os.makedirs(project_dir, exist_ok=True)
    try:
        os.chmod(project_dir, 0o777)
    except:
        pass
    print(f"[Upload] 项目目录已创建: {project_dir}, 存在: {os.path.exists(project_dir)}", file=sys.stderr)
    
    try:
        # 如果是ZIP文件，解压
        if file.filename.endswith('.zip'):
            zip_path = os.path.join(project_dir, secure_filename(file.filename))
            print(f"[Upload] 保存ZIP文件到: {zip_path}", file=sys.stderr)
            file.save(zip_path)
            
            # 解压ZIP文件
            print(f"[Upload] 开始解压ZIP文件", file=sys.stderr)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(project_dir)
            
            # 删除ZIP文件
            os.remove(zip_path)
            print(f"[Upload] ZIP文件解压完成，已删除ZIP文件", file=sys.stderr)
            
            # 统计解压后的文件
            file_count = 0
            for root, dirs, files in os.walk(project_dir):
                file_count += len(files)
            print(f"[Upload] 解压后文件数量: {file_count}", file=sys.stderr)
            
            return jsonify({
                'message': '项目文件上传成功',
                'project_id': project_id,
                'path': project_dir,
                'file_count': file_count
            }), 200
        else:
            # 单个文件，直接保存
            filename = secure_filename(file.filename)
            file_path = os.path.join(project_dir, filename)
            print(f"[Upload] 保存单个文件到: {file_path}", file=sys.stderr)
            file.save(file_path)
            
            return jsonify({
                'message': '项目文件上传成功',
                'project_id': project_id,
                'filename': filename,
                'path': file_path,
                'file_count': 1
            }), 200
            
    except Exception as e:
        import traceback
        error_msg = f'上传失败: {str(e)}'
        print(f"[Upload] 错误: {error_msg}", file=sys.stderr)
        print(f"[Upload] 堆栈: {traceback.format_exc()}", file=sys.stderr)
        return jsonify({'error': error_msg}), 500

@bp.route('/<int:project_id>/files', methods=['GET'])
@jwt_required()
def get_project_files(project_id):
    """获取项目文件信息"""
    user_id = int(get_jwt_identity())  # 转换为整数
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    project_dir = os.path.join(UPLOAD_DIR, f'project_{project_id}')
    
    if not os.path.exists(project_dir):
        return jsonify({
            'has_files': False,
            'message': '项目文件目录不存在',
            'path': project_dir
        }), 200
    
    # 统计文件信息
    file_count = 0
    total_size = 0
    
    for root, dirs, files in os.walk(project_dir):
        file_count += len(files)
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
            except:
                pass
    
    return jsonify({
        'has_files': file_count > 0,
        'file_count': file_count,
        'total_size': total_size,
        'path': project_dir
    }), 200

