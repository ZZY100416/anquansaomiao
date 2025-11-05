# 快速修复Backend启动失败

## 问题

- `uss-backend` 状态显示 `Exit 1`（启动失败）
- 执行 `init_db.py` 没有输出（因为容器没有运行）

## 立即排查（在Ubuntu上执行）

### 步骤1: 查看Backend日志（最重要）

```bash
# 查看backend容器日志
docker-compose logs backend

# 查看最近50行日志
docker-compose logs --tail=50 backend
```

### 步骤2: 根据日志错误修复

常见错误和解决方案：

#### 错误1: 模块导入错误

如果看到 `ModuleNotFoundError` 或 `ImportError`：

```bash
# 进入容器检查
docker-compose run --rm backend bash

# 在容器内检查
python --version
pip list | grep Flask
```

#### 错误2: 数据库连接失败

如果看到 `could not connect to server`：

```bash
# 重启postgres
docker-compose restart postgres
sleep 10

# 重启backend
docker-compose restart backend
```

#### 错误3: 端口问题

如果看到 `Address already in use`：

```bash
# 检查端口占用
sudo lsof -i :5000
```

## 快速修复命令

```bash
# 1. 查看日志（最重要）
docker-compose logs backend

# 2. 重启backend（如果只是临时问题）
docker-compose restart backend

# 3. 查看实时日志
docker-compose logs -f backend

# 4. 如果backend启动成功，初始化数据库
docker-compose exec backend python init_db.py
```

## 如果重启不行，重建容器

```bash
# 停止backend
docker-compose stop backend

# 删除backend容器
docker-compose rm -f backend

# 重新构建并启动
docker-compose up -d --build backend

# 查看日志
docker-compose logs -f backend
```

