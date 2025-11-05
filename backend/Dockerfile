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

# 安装Trivy扫描器（使用新的方法，不依赖apt-key）
RUN wget -qO /usr/share/keyrings/trivy.gpg https://aquasecurity.github.io/trivy-repo/deb/public.key \
    && echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/trivy.list \
    && apt-get update \
    && apt-get install -y trivy \
    && rm -rf /var/lib/apt/lists/*

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

