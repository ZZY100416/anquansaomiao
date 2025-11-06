# 快速修复Docker重启错误

## 错误信息

```
unable to start unit "docker-...scope" was already loaded or has a fragment file
```

这是Docker cgroup/systemd冲突，需要清理容器资源。

## 立即修复（在Ubuntu上执行）

### 方法1: 清理并重启（推荐）

```bash
cd ~/projects/anquansaomiao

# 1. 停止所有容器
docker-compose down

# 2. 清理Docker系统
docker system prune -f

# 3. 重启Docker服务
sudo systemctl restart docker

# 4. 等待几秒
sleep 5

# 5. 重新启动所有服务
docker-compose up -d

# 6. 查看状态
docker-compose ps
```

### 方法2: 如果方法1不行，强制删除容器

```bash
cd ~/projects/anquansaomiao

# 1. 停止所有容器
docker-compose down

# 2. 强制删除backend容器
docker rm -f uss-backend 2>/dev/null || true

# 3. 清理系统
docker system prune -f
sudo systemctl restart docker

# 4. 等待几秒
sleep 5

# 5. 重新启动
docker-compose up -d --build backend

# 6. 查看日志确认启动
docker-compose logs -f backend
```

### 方法3: 完全重置（如果还是不行）

```bash
cd ~/projects/anquansaomiao

# 1. 停止所有服务
docker-compose down -v

# 2. 删除所有相关容器
docker ps -a | grep uss- | awk '{print $1}' | xargs -r docker rm -f

# 3. 清理系统
docker system prune -af
sudo systemctl restart docker

# 4. 等待
sleep 10

# 5. 重新构建并启动
docker-compose build --no-cache backend
docker-compose up -d

# 6. 查看状态
docker-compose ps
```

## 验证

```bash
# 检查容器状态（应该都是Up）
docker-compose ps

# 查看后端日志
docker-compose logs --tail=20 backend

# 测试API
curl http://localhost:5000/api/health
```

## 如果问题持续

### 检查Docker服务状态

```bash
sudo systemctl status docker
```

### 检查Docker版本

```bash
docker --version
docker-compose --version
```

### 完全重启Docker

```bash
sudo systemctl stop docker
sudo systemctl start docker
sudo systemctl status docker
```

