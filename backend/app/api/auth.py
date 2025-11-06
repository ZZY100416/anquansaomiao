from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if User.query.filter_by(email=data.get('email', '')).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    user = User(
        username=data['username'],
        email=data.get('email', ''),
        role=data.get('role', 'user')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '注册成功', 'user': user.to_dict()}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # Flask-JWT-Extended要求identity必须是字符串
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())  # 转换为整数
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify(user.to_dict()), 200

