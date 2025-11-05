FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    lsb-release \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 安装Trivy扫描器（使用二进制方式，兼容所有Debian版本）
# 如果下载失败，使用备选方案或跳过（不影响构建）
RUN TRIVY_VERSION="0.50.0" \
    && echo "Installing Trivy version: $TRIVY_VERSION" \
    && (wget -q --timeout=30 --tries=3 -O /tmp/trivy.tar.gz "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz" && \
        tar -xzf /tmp/trivy.tar.gz -C /tmp && \
        mv /tmp/trivy /usr/local/bin/trivy && \
        chmod +x /usr/local/bin/trivy && \
        rm -f /tmp/trivy.tar.gz && \
        trivy --version || echo "Trivy version check failed") || \
    (echo "Warning: Trivy installation failed, container scanning may not work" && \
     echo "#!/bin/sh" > /usr/local/bin/trivy && \
     echo "echo 'Trivy not installed'" >> /usr/local/bin/trivy && \
     chmod +x /usr/local/bin/trivy)

# 安装OWASP Dependency-Check（添加错误处理和重试）
RUN mkdir -p /opt/dependency-check \
    && cd /opt/dependency-check \
    && (wget --timeout=30 --tries=3 https://github.com/jeremylong/DependencyCheck/releases/latest/download/dependency-check-9.0.9-release.zip && \
        unzip dependency-check-9.0.9-release.zip && \
        rm dependency-check-9.0.9-release.zip && \
        chmod +x /opt/dependency-check/dependency-check/bin/dependency-check.sh) || \
    (echo "Warning: OWASP Dependency-Check download failed, SCA scanning may not work" && \
     mkdir -p /opt/dependency-check/dependency-check/bin && \
     echo "#!/bin/sh" > /opt/dependency-check/dependency-check/bin/dependency-check.sh && \
     echo "echo 'Dependency-Check not installed'" >> /opt/dependency-check/dependency-check/bin/dependency-check.sh && \
     chmod +x /opt/dependency-check/dependency-check/bin/dependency-check.sh)

# 安装Semgrep
RUN pip install semgrep

# 复制Python依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["python", "app.py"]

