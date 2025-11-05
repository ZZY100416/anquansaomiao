# Ubuntu下一步操作指南（代码已Clone）

## ✅ 当前状态

- ✅ 代码已通过Git clone到Ubuntu
- ✅ 项目文件在：`~/projects/unified-security-scanner`（或您的路径）

## 🚀 接下来的步骤

### 步骤1: 验证项目文件（30秒）

```bash
# 进入项目目录
cd ~/projects/unified-security-scanner
# 或您的实际路径

# 检查关键文件是否存在
ls -la docker-compose.yml
ls -la backend/app.py
ls -la frontend/package.json
ls -la .github/workflows/

# 查看项目结构
tree -L 2  # 如果没有tree，使用: ls -R
```

### 步骤2: 检查Docker环境（1分钟）

```bash
# 检查Docker是否已安装
docker --version
docker compose version

# 检查Docker服务是否运行
sudo systemctl status docker

# 如果Docker未安装，安装它：
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker  # 使组权限立即生效

# 验证Docker
docker ps
```

### 步骤3: 启动Docker服务（2-5分钟）

```bash
# 确保在项目根目录
cd ~/projects/unified-security-scanner

# 查看docker-compose配置
cat docker-compose.yml

# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 应该看到类似输出：
# NAME              STATUS          PORTS
# uss-backend       Up              0.0.0.0:5000->5000/tcp
# uss-frontend      Up              0.0.0.0:3000->3000/tcp
# uss-postgres      Up              0.0.0.0:5432->5432/tcp
# uss-redis         Up              0.0.0.0:6379->6379/tcp
```

### 步骤4: 查看启动日志（1分钟）

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# 实时查看日志（按Ctrl+C退出）
docker-compose logs -f

# 如果看到错误，记录下来
```

### 步骤5: 等待服务完全启动（1-2分钟）

```bash
# 等待PostgreSQL就绪
echo "等待数据库启动..."
sleep 30

# 检查服务健康状态
curl http://localhost:5000/api/health

# 应该返回: {"status":"healthy","service":"Unified Security Scanner API"}
```

### 步骤6: 初始化数据库（1分钟）

```bash
# 初始化数据库并创建默认管理员账户
docker-compose exec backend python init_db.py

# 如果上面的命令失败，尝试：
docker-compose exec -T backend python init_db.py

# 应该看到输出：
# ✓ 默认管理员账户创建成功
#   用户名: admin
#   密码: admin123
# ✓ 数据库初始化完成
```

### 步骤7: 验证部署（2分钟）

#### 7.1 检查服务状态

```bash
# 再次检查所有服务
docker-compose ps

# 所有服务应该显示为 "Up"
```

#### 7.2 测试API

```bash
# 测试后端API
curl http://localhost:5000/api/health

# 测试前端（应该返回HTML）
curl http://localhost:3000 | head -20
```

#### 7.3 访问Web界面

在Ubuntu虚拟机的浏览器中访问：

- **Web界面**: http://localhost:3000
- **默认账号**: 
  - 用户名: `admin`
  - 密码: `admin123`

或者如果没有图形界面，可以在Windows上通过浏览器访问：

- 需要先获取Ubuntu的IP地址：
  ```bash
  hostname -I
  # 或
  ip addr show
  ```
- 然后在Windows浏览器访问：`http://Ubuntu的IP:3000`

### 步骤8: 测试基本功能（5分钟）

1. **登录测试**
   - 访问 http://localhost:3000
   - 使用 admin / admin123 登录
   - 确认能成功进入Dashboard

2. **项目管理测试**
   - 点击 "项目管理"
   - 点击 "新建项目"
   - 创建一个测试项目
   - 确认项目创建成功

3. **扫描任务测试**
   - 点击 "扫描任务"
   - 点击 "新建扫描"
   - 选择项目，选择扫描类型（如SAST）
   - 创建扫描任务
   - 查看扫描状态

### 步骤9: 配置Git和GitHub（如果需要推送代码）

```bash
# 检查Git配置
git config --list

# 如果还没配置，设置用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 检查远程仓库
git remote -v

# 如果需要添加远程仓库
git remote add origin https://github.com/your-username/unified-security-scanner.git
# 或SSH方式
git remote add origin git@github.com:your-username/unified-security-scanner.git

# 检查分支
git branch -a

# 如果需要推送代码
git push -u origin main
```

## 🔍 常见问题排查

### 问题1: Docker命令需要sudo

**解决**:
```bash
# 将用户添加到docker组
sudo usermod -aG docker $USER
newgrp docker  # 立即生效

# 验证
docker ps
```

### 问题2: 端口被占用

**解决**:
```bash
# 查找占用端口的进程
sudo lsof -i :3000
sudo lsof -i :5000
sudo lsof -i :5432

# 停止占用端口的服务，或修改docker-compose.yml中的端口
```

### 问题3: 服务启动失败

**解决**:
```bash
# 查看详细错误
docker-compose logs --tail=100

# 检查磁盘空间
df -h

# 检查内存
free -h

# 重建服务
docker-compose down
docker-compose up -d --build
```

### 问题4: 数据库初始化失败

**解决**:
```bash
# 检查PostgreSQL容器是否运行
docker-compose ps postgres

# 查看PostgreSQL日志
docker-compose logs postgres

# 手动进入容器检查
docker-compose exec postgres psql -U scanner -d security_scanner

# 如果容器未运行，重启
docker-compose restart postgres
sleep 10
docker-compose exec backend python init_db.py
```

### 问题5: 无法访问Web界面

**解决**:
```bash
# 检查服务是否运行
docker-compose ps

# 检查防火墙
sudo ufw status
sudo ufw allow 3000
sudo ufw allow 5000

# 检查服务日志
docker-compose logs frontend
docker-compose logs backend

# 尝试从容器内访问
docker-compose exec frontend curl http://localhost:3000
```

## ✅ 完成检查清单

完成以下检查，确认所有步骤已完成：

- [ ] Docker已安装并运行
- [ ] 所有服务已启动（docker-compose ps显示Up）
- [ ] 数据库已初始化（能执行init_db.py）
- [ ] API健康检查通过（curl返回healthy）
- [ ] Web界面可访问（http://localhost:3000）
- [ ] 能够成功登录（admin/admin123）
- [ ] 能够创建项目
- [ ] 能够创建扫描任务

## 📚 下一步学习

1. **阅读文档**:
   ```bash
   # 查看使用手册
   cat docs/用户使用手册.md
   
   # 查看API文档
   cat docs/API接口文档.md
   ```

2. **测试GitHub安全扫描**:
   - 确保代码已推送到GitHub
   - 查看GitHub Actions运行状态
   - 查看Security标签中的扫描结果

3. **开始开发**:
   - 阅读 [团队分工与Git工作流](docs/团队分工与Git工作流.md)
   - 创建功能分支
   - 开始开发

## 🎯 快速命令参考

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 重建服务
docker-compose up -d --build

# 初始化数据库
docker-compose exec backend python init_db.py
```

---

**现在开始执行步骤1！** 如果遇到任何问题，请查看上面的常见问题部分或告诉我具体情况。

