# Backend容器启动失败排查

## 问题现象

- `uss-backend` 状态显示 `Exit 1`
- 执行 `init_db.py` 没有输出

## 排查步骤

### 步骤1: 查看Backend日志

```bash
# 查看backend容器日志（最重要的步骤）
docker-compose logs backend

# 查看最近100行日志
docker-compose logs --tail=100 backend
```

### 步骤2: 检查常见问题

#### 问题1: 数据库连接失败

**症状**: 日志中显示 "could not connect to server"

**解决**:
```bash
# 检查PostgreSQL是否运行
docker-compose ps postgres

# 检查数据库连接
docker-compose exec postgres psql -U scanner -d security_scanner

# 如果连接失败，重启PostgreSQL
docker-compose restart postgres
sleep 10
docker-compose restart backend
```

#### 问题2: Python模块导入错误

**症状**: 日志中显示 "ModuleNotFoundError" 或 "ImportError"

**解决**:
```bash
# 进入backend容器检查
docker-compose exec backend bash

# 在容器内检查Python环境
python --version
pip list

# 如果缺少模块，重新安装
pip install -r requirements.txt
```

#### 问题3: 端口被占用

**症状**: 日志中显示 "Address already in use"

**解决**:
```bash
# 查找占用5000端口的进程
sudo lsof -i :5000

# 停止占用端口的服务
# 或修改docker-compose.yml中的端口
```

#### 问题4: 数据库表创建失败

**症状**: 日志中显示数据库相关错误

**解决**:
```bash
# 手动进入容器执行
docker-compose exec backend python
# 然后在Python中执行：
from app import app, db
with app.app_context():
    db.create_all()
    print("Database tables created")
```

## 快速修复

```bash
# 1. 查看backend日志（最重要）
docker-compose logs backend

# 2. 根据日志错误信息修复

# 3. 重启backend
docker-compose restart backend

# 4. 查看日志确认启动成功
docker-compose logs -f backend

# 5. 如果启动成功，初始化数据库
docker-compose exec backend python init_db.py
```

## 手动初始化数据库（如果容器无法启动）

如果backend容器一直无法启动，可以手动初始化：

```bash
# 1. 进入postgres容器
docker-compose exec postgres psql -U scanner -d security_scanner

# 2. 在PostgreSQL中执行：
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 创建默认管理员（密码是admin123的哈希）
INSERT INTO users (username, email, password_hash, role) 
VALUES ('admin', 'admin@example.com', 'pbkdf2:sha256:260000$...', 'admin')
ON CONFLICT (username) DO NOTHING;

-- 查看用户
SELECT * FROM users;
```

## 常见错误和解决方案

### 错误1: "No module named 'app'"

**原因**: 工作目录不对

**解决**: 检查Dockerfile中的WORKDIR设置

### 错误2: "OperationalError: could not connect to server"

**原因**: 数据库还没启动

**解决**: 确保postgres服务已启动并健康

### 错误3: "Table 'users' already exists"

**原因**: 数据库已初始化

**解决**: 这是正常的，可以忽略或删除表重新创建

