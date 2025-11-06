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
    user_id = int(get_jwt_identity())  # 转换为整数
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 创建项目目录
    project_dir = os.path.join(UPLOAD_DIR, f'project_{project_id}')
    os.makedirs(project_dir, exist_ok=True)
    
    try:
        # 如果是ZIP文件，解压
        if file.filename.endswith('.zip'):
            zip_path = os.path.join(project_dir, secure_filename(file.filename))
            file.save(zip_path)
            
            # 清空现有文件（可选，根据需求决定）
            # 如果希望每次上传都覆盖，取消下面的注释
            # for item in os.listdir(project_dir):
            #     item_path = os.path.join(project_dir, item)
            #     if item != secure_filename(file.filename):
            #         if os.path.isdir(item_path):
            #             shutil.rmtree(item_path)
            #         else:
            #             os.remove(item_path)
            
            # 解压ZIP文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(project_dir)
            
            # 删除ZIP文件
            os.remove(zip_path)
            
            return jsonify({
                'message': '项目文件上传成功',
                'project_id': project_id,
                'path': project_dir
            }), 200
        else:
            # 单个文件，直接保存
            filename = secure_filename(file.filename)
            file_path = os.path.join(project_dir, filename)
            file.save(file_path)
            
            return jsonify({
                'message': '项目文件上传成功',
                'project_id': project_id,
                'filename': filename,
                'path': file_path
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

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

