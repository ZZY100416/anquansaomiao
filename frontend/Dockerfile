FROM node:18-alpine

WORKDIR /app

# 设置npm配置以加速安装
RUN npm config set registry https://registry.npmmirror.com/ && \
    npm config set fetch-retries 3 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm config set maxsockets 10 && \
    npm config set progress false && \
    npm config set audit false

# 复制package文件（利用Docker层缓存）
COPY package*.json ./

# 安装依赖（优化选项）
RUN npm ci --prefer-offline --silent --no-audit || \
    (echo "npm ci failed, falling back to npm install" && \
     npm install --prefer-offline --silent --no-audit) && \
    npm cache clean --force

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 3000

# 启动开发服务器
CMD ["npm", "start"]

