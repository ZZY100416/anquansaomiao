"""
初始化数据库脚本
创建默认管理员账户
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models.user import User

def init_database():
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已存在管理员账户
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            # 创建默认管理员账户
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✓ 默认管理员账户创建成功')
            print('  用户名: admin')
            print('  密码: admin123')
        else:
            print('✓ 管理员账户已存在')
        
        print('✓ 数据库初始化完成')

if __name__ == '__main__':
    init_database()

