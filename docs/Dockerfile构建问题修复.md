# Dockerfile构建问题修复

## 问题1: apt-key命令不存在 ✅ 已修复

**原因**: 新版本Debian/Ubuntu移除了`apt-key`命令

**解决**: 使用新的GPG密钥管理方式

## 问题2: Trivy仓库不支持Trixie ✅ 已修复

**原因**: Trivy的APT仓库不支持Debian Trixie版本

**解决**: 改用二进制方式安装Trivy，直接从GitHub下载

### 修复内容

将APT安装方式改为二进制安装：

```dockerfile
# 旧方式（依赖APT仓库）
RUN apt-get install -y trivy

# 新方式（直接下载二进制）
RUN wget -qO - https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.51.4_Linux-64bit.tar.gz | tar -xz \
    && mv trivy /usr/local/bin/trivy \
    && chmod +x /usr/local/bin/trivy
```

## 重新构建

修复后，在Ubuntu上执行：

```bash
cd ~/projects/anquansaomiao

# 清理之前的构建
docker-compose down
docker system prune -f

# 重新构建
docker-compose up -d --build
```

## 如果还有问题

### 问题: 网络连接失败

如果下载Trivy失败，可以：

1. **使用国内镜像**（如果在中国）:
```dockerfile
# 使用清华镜像或其他镜像
RUN wget -qO - https://mirrors.tuna.tsinghua.edu.cn/github-release/aquasecurity/trivy/latest/download/trivy_0.51.4_Linux-64bit.tar.gz | tar -xz
```

2. **或者暂时注释掉Trivy安装**（如果不需要容器扫描功能）:
```dockerfile
# 暂时注释掉，先让服务启动
# RUN wget -qO - https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.51.4_Linux-64bit.tar.gz | tar -xz
```

### 问题: 版本号问题

如果特定版本下载失败，可以使用最新版本：

```dockerfile
# 获取最新版本
RUN TRIVY_VERSION=$(curl -s https://api.github.com/repos/aquasecurity/trivy/releases/latest | grep tag_name | cut -d '"' -f 4 | sed 's/v//') \
    && wget -qO - https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz | tar -xz \
    && mv trivy /usr/local/bin/trivy \
    && chmod +x /usr/local/bin/trivy
```

## 验证修复

构建成功后：

```bash
# 检查服务状态
docker-compose ps

# 进入容器验证Trivy
docker-compose exec backend trivy --version

# 应该显示版本信息
```

