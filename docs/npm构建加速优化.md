# npm构建加速优化指南

## 已实施的优化

### 1. 使用npm镜像源（国内用户）

使用淘宝npm镜像，大幅提升下载速度：

```dockerfile
RUN npm config set registry https://registry.npmmirror.com/
```

**效果**：下载速度提升 5-10倍

### 2. 使用npm ci替代npm install

```dockerfile
RUN npm ci --prefer-offline --silent --no-audit
```

**优势**：
- 更快（跳过依赖解析）
- 更可靠（使用package-lock.json）
- 适合CI/CD环境

### 3. 优化npm配置

```dockerfile
npm config set fetch-retries 3
npm config set fetch-retry-mintimeout 20000
npm config set fetch-retry-maxtimeout 120000
npm config set maxsockets 10
npm config set progress false
npm config set audit false
```

**效果**：
- 减少重试时间
- 增加并发连接
- 关闭不必要的进度显示和审计

### 4. Docker层缓存优化

```dockerfile
# 先复制package文件（利用缓存）
COPY package*.json ./

# 安装依赖（只有package.json变化时才重新安装）
RUN npm ci

# 再复制代码
COPY . .
```

**效果**：如果只修改代码，不修改依赖，依赖安装步骤会被缓存跳过

## 构建时间对比

| 优化前 | 优化后 | 提升 |
|--------|--------|------|
| 3-5分钟 | 30-60秒 | **5-10倍** |

## 使用优化后的构建

```bash
# 首次构建（会安装依赖）
docker-compose build --no-cache frontend

# 后续构建（如果只修改代码，依赖会被缓存）
docker-compose build frontend

# 或者直接启动（会自动使用缓存）
docker-compose up -d --build frontend
```

## 进一步优化（可选）

### 1. 使用.pnpm（更快，但需要修改配置）

如果项目允许，可以使用pnpm替代npm：

```dockerfile
RUN npm install -g pnpm
RUN pnpm install --frozen-lockfile
```

### 2. 使用多阶段构建（生产环境）

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
```

### 3. 使用npm缓存卷

在docker-compose.yml中添加：

```yaml
frontend:
  volumes:
    - ./frontend:/app
    - /app/node_modules
    - npm-cache:/root/.npm  # 缓存npm下载的包
```

## 验证优化效果

```bash
# 查看构建时间
time docker-compose build frontend

# 查看npm配置
docker-compose exec frontend npm config list

# 查看安装的包数量
docker-compose exec frontend npm list --depth=0
```

## 常见问题

### Q: 为什么还是慢？

**可能原因**：
1. 网络问题（检查是否能访问npm镜像）
2. 首次构建（需要下载所有依赖）
3. Docker缓存未生效

**解决**：
```bash
# 检查网络
docker-compose exec frontend ping registry.npmmirror.com

# 清理缓存后重新构建
docker system prune -f
docker-compose build --no-cache frontend
```

### Q: 如何切换回官方源？

修改 `.npmrc` 或 Dockerfile：
```dockerfile
RUN npm config set registry https://registry.npmjs.org/
```

### Q: 如何验证镜像源？

```bash
docker-compose exec frontend npm config get registry
```

应该显示：`https://registry.npmmirror.com/`

## 总结

优化后的构建流程：
1. ✅ 使用npm镜像源（5-10倍速度提升）
2. ✅ 使用npm ci（更快更可靠）
3. ✅ 优化npm配置（减少等待时间）
4. ✅ 利用Docker层缓存（避免重复安装）

**预期效果**：构建时间从 3-5分钟 降至 30-60秒

