# 快速修复ContainerConfig错误

## 错误信息

```
KeyError: 'ContainerConfig'
```

## 原因

Docker容器配置损坏或不完整，通常发生在：
- 容器被强制停止
- Docker镜像损坏
- Docker Compose版本问题

## 立即修复（在Ubuntu上执行）

### 方法1: 清理并重新创建（推荐）

```bash
cd ~/projects/anquansaomiao

# 1. 停止所有容器
docker-compose down

# 2. 删除backend容器（如果存在）
docker rm -f uss-backend 2>/dev/null || true

# 3. 清理损坏的容器
docker container prune -f

# 4. 重新启动
docker-compose up -d
```

### 方法2: 完全清理后重建

如果方法1不行，执行：

```bash
cd ~/projects/anquansaomiao

# 1. 停止并删除所有容器
docker-compose down

# 2. 删除backend容器（强制）
docker rm -f uss-backend uss-frontend 2>/dev/null || true

# 3. 清理未使用的容器和网络
docker container prune -f
docker network prune -f

# 4. 重新构建并启动
docker-compose up -d --build
```

### 方法3: 如果还是不行，完全重置

```bash
cd ~/projects/anquansaomiao

# 1. 停止所有服务
docker-compose down -v

# 2. 删除所有相关容器
docker ps -a | grep uss- | awk '{print $1}' | xargs docker rm -f

# 3. 清理系统
docker system prune -f

# 4. 重新构建（不缓存）
docker-compose build --no-cache backend

# 5. 启动所有服务
docker-compose up -d
```

## 验证

```bash
# 检查容器状态
docker-compose ps

# 应该看到所有容器都是 Up 状态
```

## 如果问题持续

### 检查Docker版本

```bash
docker --version
docker-compose --version
```

如果Docker Compose版本太旧（<1.29），考虑升级：

```bash
# 检查是否有新版本
sudo apt update
sudo apt install docker-compose
```

### 检查Docker服务

```bash
# 重启Docker服务
sudo systemctl restart docker

# 检查Docker状态
sudo systemctl status docker
```

## 预防措施

1. **正常停止容器**：使用 `docker-compose down` 而不是强制停止
2. **定期清理**：`docker system prune -f`
3. **保持Docker更新**

