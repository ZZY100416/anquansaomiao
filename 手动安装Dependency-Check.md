# 手动安装Dependency-Check（容器内）

## 步骤说明

不需要修改Dockerfile，直接在运行中的容器内安装。

## 完整步骤

### 1. 进入后端容器

```bash
# 在Ubuntu上执行
cd ~/projects/anquansaomiao

# 进入后端容器（进入bash交互式终端）
docker-compose exec backend bash
```

### 2. 在容器内安装Dependency-Check

进入容器后，你会看到类似 `root@容器ID:/app#` 的提示符，然后执行：

```bash
# 创建安装目录
mkdir -p /opt/dependency-check
cd /opt/dependency-check

# 清理旧文件（如果有）
rm -rf *

# 下载Dependency-Check（使用固定版本v9.0.9）
# 注意：正确的下载地址格式是 /releases/download/v{版本号}/dependency-check-{版本号}-release.zip
wget --timeout=60 --tries=5 \
  https://github.com/jeremylong/DependencyCheck/releases/download/v9.0.9/dependency-check-9.0.9-release.zip

# 如果v9.0.9下载失败，可以尝试最新版本v12.1.0：
# wget --timeout=60 --tries=5 \
#   https://github.com/jeremylong/DependencyCheck/releases/download/v12.1.0/dependency-check-12.1.0-release.zip

# 解压
unzip dependency-check-9.0.9-release.zip

# 删除zip文件
rm dependency-check-9.0.9-release.zip

# 设置执行权限
chmod +x /opt/dependency-check/dependency-check/bin/dependency-check.sh

# 验证安装是否成功
/opt/dependency-check/dependency-check/bin/dependency-check.sh --version
```

### 3. 验证安装

如果看到类似以下输出，说明安装成功：
```
Dependency-Check version 9.0.9
```

如果是 `Dependency-Check not installed`，说明安装失败，需要检查网络或下载链接。

### 4. 退出容器

```bash
exit
```

### 5. 重启后端容器（使安装生效）

```bash
# 退出容器后，在Ubuntu终端执行
docker-compose restart backend
```

## 一键安装脚本（可选）

如果你想一键执行所有步骤，可以创建一个脚本：

```bash
# 在Ubuntu上创建脚本
cat > install-dependency-check.sh << 'EOF'
#!/bin/bash
docker-compose exec -T backend bash << 'INNER'
cd /opt/dependency-check
rm -rf *
# 使用正确的下载地址格式
wget --timeout=60 --tries=5 \
  https://github.com/jeremylong/DependencyCheck/releases/download/v9.0.9/dependency-check-9.0.9-release.zip
unzip dependency-check-9.0.9-release.zip
rm dependency-check-9.0.9-release.zip
chmod +x /opt/dependency-check/dependency-check/bin/dependency-check.sh
/opt/dependency-check/dependency-check/bin/dependency-check.sh --version
INNER
docker-compose restart backend
EOF

# 给脚本执行权限
chmod +x install-dependency-check.sh

# 执行脚本
./install-dependency-check.sh
```

## 如果下载失败

### 方法1：使用国内镜像（如果GitHub访问慢）

```bash
# 在容器内执行
cd /opt/dependency-check
rm -rf *

# 使用gitee镜像或其他国内镜像（如果有）
# 或者先下载到宿主机，然后复制到容器
```

### 方法2：从宿主机复制文件

如果Ubuntu可以访问GitHub，可以：

```bash
# 在Ubuntu主机上下载（使用正确的下载地址）
cd ~/projects/anquansaomiao
wget https://github.com/jeremylong/DependencyCheck/releases/download/v9.0.9/dependency-check-9.0.9-release.zip

# 如果v9.0.9下载失败，可以尝试最新版本v12.1.0：
# wget https://github.com/jeremylong/DependencyCheck/releases/download/v12.1.0/dependency-check-12.1.0-release.zip

# 复制到容器内
docker cp dependency-check-9.0.9-release.zip anquansaomiao-backend-1:/tmp/

# 进入容器
docker-compose exec backend bash

# 在容器内解压
cd /opt/dependency-check
rm -rf *
unzip /tmp/dependency-check-9.0.9-release.zip
rm /tmp/dependency-check-9.0.9-release.zip
chmod +x /opt/dependency-check/dependency-check/bin/dependency-check.sh
```

## 验证安装是否生效

安装完成后，重新创建SCA扫描任务，查看日志：

```bash
docker-compose logs --tail=50 backend | grep -E "\[SCA\]|Dependency-Check"
```

应该看到：
- `[SCA] Dependency-Check已安装` 或版本信息
- 不再显示 `Dependency-Check未安装或不可用`

## 注意事项

1. **容器重启后安装会丢失**：如果容器被删除重建，手动安装会丢失。如果需要持久化，需要：
   - 使用Docker volume挂载
   - 或者修改Dockerfile（但你说不想用Dockerfile）

2. **如果容器被删除重建**，需要重新手动安装。

3. **建议**：如果经常需要安装，还是建议修改Dockerfile，这样每次构建都会自动安装。

