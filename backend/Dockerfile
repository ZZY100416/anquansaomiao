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

# 安装OWASP Dependency-Check（改进安装逻辑）
RUN mkdir -p /opt/dependency-check \
    && cd /opt/dependency-check \
    && echo "正在下载Dependency-Check..." \
    && (wget --timeout=60 --tries=5 --progress=bar:force \
        https://github.com/jeremylong/DependencyCheck/releases/download/v9.0.9/dependency-check-9.0.9-release.zip \
        -O dependency-check.zip && \
        echo "下载完成，开始解压..." && \
        unzip -q dependency-check.zip && \
        rm dependency-check.zip && \
        chmod +x /opt/dependency-check/dependency-check/bin/dependency-check.sh && \
        echo "验证安装..." && \
        /opt/dependency-check/dependency-check/bin/dependency-check.sh --version && \
        echo "Dependency-Check安装成功") || \
    (echo "警告: Dependency-Check v9.0.9下载失败，尝试使用最新版本..." && \
     wget --timeout=60 --tries=5 \
        https://github.com/jeremylong/DependencyCheck/releases/download/v12.1.0/dependency-check-12.1.0-release.zip \
        -O dependency-check.zip && \
     unzip -q dependency-check.zip && \
     rm dependency-check.zip && \
     chmod +x /opt/dependency-check/dependency-check/bin/dependency-check.sh && \
     /opt/dependency-check/dependency-check/bin/dependency-check.sh --version || \
     (echo "警告: OWASP Dependency-Check安装失败，SCA扫描可能无法工作" && \
      mkdir -p /opt/dependency-check/dependency-check/bin && \
      echo "#!/bin/sh" > /opt/dependency-check/dependency-check/bin/dependency-check.sh && \
      echo "echo 'Dependency-Check not installed'" >> /opt/dependency-check/dependency-check/bin/dependency-check.sh && \
      chmod +x /opt/dependency-check/dependency-check/bin/dependency-check.sh))

# 安装Semgrep
RUN pip install semgrep

# 安装Node.js和npm（用于npm audit扫描Node.js依赖）
RUN apt-get update && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm --version && \
    node --version && \
    rm -rf /var/lib/apt/lists/*

# 安装Maven（用于扫描Java/Maven项目依赖）
RUN apt-get update && \
    apt-get install -y maven && \
    mvn --version && \
    rm -rf /var/lib/apt/lists/*

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

