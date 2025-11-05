# 修复前端API配置问题

## 问题确认

- ✅ Admin用户存在
- ✅ 后端API正常（curl测试成功）
- ❌ 前端API URL配置错误：`http://localhost:5000/api`
- ❌ 浏览器显示 `ERR_CONNECTION_REFUSED`（因为浏览器中的localhost指向Windows，不是Ubuntu）

## 解决方案

React应用在**构建时**读取环境变量，所以需要**重新构建**前端容器才能应用新的API URL。

### 方法1: 重新构建前端（推荐）

```bash
cd ~/projects/anquansaomiao

# 停止前端
docker-compose stop frontend

# 重新构建前端（应用新的环境变量）
docker-compose build --no-cache frontend

# 启动前端
docker-compose up -d frontend

# 查看日志确认启动
docker-compose logs -f frontend
```

### 方法2: 完全重建（如果方法1不行）

```bash
cd ~/projects/anquansaomiao

# 停止并删除前端容器
docker-compose stop frontend
docker rm -f uss-frontend

# 重新构建并启动
docker-compose up -d --build frontend

# 查看日志
docker-compose logs -f frontend
```

### 方法3: 一键修复命令

```bash
cd ~/projects/anquansaomiao

# 停止前端
docker-compose stop frontend

# 删除前端容器
docker rm -f uss-frontend

# 重新构建（强制重新构建，不使用缓存）
docker-compose build --no-cache frontend

# 启动
docker-compose up -d frontend

# 等待10秒后检查
sleep 10

# 验证环境变量
echo "=== 检查环境变量 ==="
docker-compose exec frontend env | grep REACT_APP_API_URL

# 应该显示：REACT_APP_API_URL=http://192.168.203.141:5000/api

# 查看日志
echo ""
echo "=== 查看启动日志 ==="
docker-compose logs --tail=20 frontend
```

## 验证

### 1. 检查环境变量

```bash
docker-compose exec frontend env | grep REACT_APP_API_URL
```

**应该显示**：`REACT_APP_API_URL=http://192.168.203.141:5000/api`

### 2. 检查前端日志

```bash
docker-compose logs --tail=30 frontend
```

应该看到：
- `Compiled successfully!`
- `Local: http://localhost:3000`

### 3. 在浏览器中测试

1. 刷新浏览器页面：`http://192.168.203.141:3000/login`
2. 打开开发者工具（F12）
3. 切换到 Network（网络）标签
4. 尝试登录
5. 查看 `/api/auth/login` 请求：
   - **请求URL**：应该是 `http://192.168.203.141:5000/api/auth/login`（不是localhost）
   - **状态码**：应该是 200（成功）

## 为什么需要重新构建？

React应用在构建时会将环境变量编译到JavaScript代码中。所以：
- 修改 `docker-compose.yml` 中的环境变量后
- 必须重新构建前端容器
- 仅重启容器（`docker-compose restart`）不会生效

## 如果还是不行

### 检查docker-compose.yml配置

```bash
cat docker-compose.yml | grep -A 10 frontend
```

确保看到：
```yaml
frontend:
  environment:
    - REACT_APP_API_URL=http://192.168.203.141:5000/api
```

### 检查前端源码

```bash
# 检查前端代码中的API配置
docker-compose exec frontend cat /app/src/services/api.js | grep REACT_APP_API_URL
```

### 完全清理重建

```bash
# 停止所有服务
docker-compose down

# 删除前端镜像
docker rmi anquansaomiao_frontend 2>/dev/null || true

# 重新构建所有服务
docker-compose build --no-cache

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f frontend
```

