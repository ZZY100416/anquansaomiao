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
RUN wget -qO - https://github.com/aquasecurity/trivy/releases/latest/download/trivy_0.51.4_Linux-64bit.tar.gz | tar -xz \
    && mv trivy /usr/local/bin/trivy \
    && chmod +x /usr/local/bin/trivy \
    && trivy --version

# 安装OWASP Dependency-Check
RUN mkdir -p /opt/dependency-check \
    && cd /opt/dependency-check \
    && wget https://github.com/jeremylong/DependencyCheck/releases/latest/download/dependency-check-9.0.9-release.zip \
    && unzip dependency-check-9.0.9-release.zip \
    && rm dependency-check-9.0.9-release.zip \
    && chmod +x /opt/dependency-check/dependency-check/bin/dependency-check.sh

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

