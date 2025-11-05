# Docker容器启动错误修复

## 问题描述

错误信息：
```
unable to start unit "docker-xxx.scope" was already loaded or has a fragment file
```

这是Docker的systemd cgroup配置冲突，通常是容器残留或Docker状态不一致导致的。

## 解决方案

### 方案1: 清理所有容器和资源（推荐）

```bash
# 1. 停止所有容器
docker-compose down

# 2. 停止Docker服务
sudo systemctl stop docker
sudo systemctl stop containerd

# 3. 清理所有容器和网络
docker system prune -a -f

# 4. 清理systemd残留（如果有）
sudo systemctl daemon-reload

# 5. 重启Docker服务
sudo systemctl start containerd
sudo systemctl start docker

# 6. 验证Docker
docker ps

# 7. 重新启动服务
cd ~/projects/anquansaomiao
docker-compose up -d
```

### 方案2: 强制清理（如果方案1不行）

```bash
# 1. 停止所有容器
docker-compose down

# 2. 查找并删除残留容器
docker ps -a | grep uss-backend
docker rm -f $(docker ps -a -q) 2>/dev/null || true

# 3. 清理网络
docker network prune -f

# 4. 重启Docker
sudo systemctl restart docker

# 5. 重新启动
docker-compose up -d
```

### 方案3: 检查systemd unit（高级）

```bash
# 查看残留的systemd unit
systemctl list-units | grep docker

# 如果有残留，删除
sudo systemctl reset-failed docker-*.scope

# 重新启动
docker-compose up -d
```

## 快速修复（执行这个）

在Ubuntu上执行：

```bash
cd ~/projects/anquansaomiao

# 1. 停止所有服务
docker-compose down

# 2. 清理残留
docker system prune -f

# 3. 重启Docker服务
sudo systemctl restart docker

# 4. 等待几秒
sleep 5

# 5. 重新启动
docker-compose up -d

# 6. 查看状态
docker-compose ps
```

## 如果还是不行

尝试完全重置：

```bash
# 停止所有
docker-compose down
sudo systemctl stop docker

# 删除所有容器、网络、卷
docker system prune -a --volumes -f

# 重启Docker
sudo systemctl start docker

# 重新构建和启动
docker-compose up -d --build
```

