from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.project import Project
from app.models.user import User

bp = Blueprint('projects', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = get_jwt_identity()
    projects = Project.query.filter_by(user_id=user_id).all()
    
    return jsonify([p.to_dict() for p in projects]), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    user_id = get_jwt_identity()
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
    user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    return jsonify(project.to_dict()), 200

@bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    user_id = get_jwt_identity()
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
    user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': '项目删除成功'}), 200

