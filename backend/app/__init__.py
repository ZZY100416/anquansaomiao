"""
Flask应用初始化
"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

load_dotenv()

# 创建Flask应用实例
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://scanner:scanner123@postgres:5432/security_scanner')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

# 初始化扩展
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# 导入路由（必须在db初始化之后）
from app.api import auth, projects, scans, reports, rasp

# 注册蓝图
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(projects.bp, url_prefix='/api/projects')
app.register_blueprint(scans.bp, url_prefix='/api/scans')
app.register_blueprint(reports.bp, url_prefix='/api/reports')
app.register_blueprint(rasp.bp, url_prefix='/api/rasp')

@app.route('/api/health')
def health():
    return {'status': 'healthy', 'service': 'Unified Security Scanner API'}

