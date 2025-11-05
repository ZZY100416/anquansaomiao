FROM node:18-alpine

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖（使用缓存和优化选项）
RUN npm install --prefer-offline --no-audit --progress=false

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 3000

# 启动开发服务器
CMD ["npm", "start"]

