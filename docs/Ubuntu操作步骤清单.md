# Ubuntu虚拟机操作步骤清单

## 📋 当前状态检查

首先检查您的环境是否已经准备好：

```bash
# 检查Docker是否已安装
docker --version

# 检查Docker Compose是否已安装
docker compose version

# 检查Git是否已安装
git --version

# 检查当前用户是否在docker组中
groups | grep docker
```

## 🚀 步骤1: 环境准备（如果还没完成）

### 1.1 安装Docker（如果未安装）

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker（使用官方脚本，最简单）
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 将当前用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录或执行以下命令使组权限生效
newgrp docker

# 验证安装
docker --version
docker compose version
```

### 1.2 安装Git（如果未安装）

```bash
sudo apt install -y git
git --version
```

### 1.3 配置Git（如果还没配置）

```bash
# 配置Git用户信息（替换为您的信息）
git config --global user.name "您的姓名"
git config --global user.email "your.email@example.com"

# 查看配置
git config --list
```

## 📥 步骤2: 获取项目代码

> **详细传输指南**: 请查看 [Windows到Ubuntu代码传输指南](Windows到Ubuntu代码传输指南.md)

### 方式A: 如果代码在Windows上，需要传输到Ubuntu

**选项1: 使用SCP（如果已配置SSH）**

```bash
# 在Windows PowerShell中执行
scp -r E:\network\anquannchanpin\* ubuntu-user@your-vm-ip:/home/ubuntu/projects/unified-security-scanner/
```

**选项2: 使用共享文件夹（VirtualBox/VMware）**

```bash
# 如果已配置共享文件夹，直接复制
cp -r /path/to/shared/folder/anquannchanpin/* ~/projects/unified-security-scanner/
```

**选项3: 使用Git（推荐 - 如果已创建GitHub仓库）**

```bash
# 在Windows上先提交代码到GitHub，然后在Ubuntu上克隆
cd ~
mkdir -p projects
cd projects
git clone git@github.com:your-org/unified-security-scanner.git
cd unified-security-scanner
```

**选项4: 使用U盘或移动设备**

```bash
# 挂载U盘后复制
sudo mkdir /mnt/usb
sudo mount /dev/sdb1 /mnt/usb
cp -r /mnt/usb/anquannchanpin/* ~/projects/unified-security-scanner/
```

### 方式B: 如果代码已经在Ubuntu上

```bash
# 进入项目目录
cd ~/projects/unified-security-scanner
# 或
cd /path/to/your/project

# 确认项目文件存在
ls -la
```

## 🔧 步骤3: 配置项目环境

### 3.1 进入项目目录

```bash
cd ~/projects/unified-security-scanner
# 或您的项目路径
```

### 3.2 检查项目文件

```bash
# 确认关键文件存在
ls -la docker-compose.yml
ls -la backend/
ls -la frontend/
ls -la docs/
```

### 3.3 配置环境变量（可选）

```bash
# 创建后端环境变量文件（如果需要）
cd backend
cp .env.example .env  # 如果文件存在
# 编辑 .env 文件（可选）
nano .env
```

## 🐳 步骤4: 启动Docker服务

### 4.1 启动所有服务

```bash
# 确保在项目根目录
cd ~/projects/unified-security-scanner

# 启动服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 4.2 查看日志（检查是否有错误）

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# 实时查看日志
docker-compose logs -f
```

### 4.3 如果启动失败，检查问题

```bash
# 检查Docker是否运行
sudo systemctl status docker

# 检查端口是否被占用
sudo netstat -tulpn | grep -E ':(3000|5000|5432)'

# 检查磁盘空间
df -h

# 检查内存
free -h
```

## 💾 步骤5: 初始化数据库

```bash
# 等待服务启动完成（约30秒）
sleep 30

# 初始化数据库并创建默认管理员账户
docker-compose exec backend python init_db.py

# 如果上面的命令失败，尝试：
docker-compose exec -T backend python init_db.py
```

## ✅ 步骤6: 验证部署

### 6.1 检查服务状态

```bash
# 检查所有容器是否运行
docker-compose ps

# 应该看到类似以下输出：
# NAME              STATUS          PORTS
# uss-backend       Up             0.0.0.0:5000->5000/tcp
# uss-frontend      Up             0.0.0.0:3000->3000/tcp
# uss-postgres      Up             0.0.0.0:5432->5432/tcp
```

### 6.2 测试API健康检查

```bash
# 测试后端API
curl http://localhost:5000/api/health

# 应该返回: {"status":"healthy","service":"Unified Security Scanner API"}
```

### 6.3 访问Web界面

在Ubuntu虚拟机的浏览器中访问：

- **Web界面**: http://localhost:3000
- **默认账号**: admin
- **默认密码**: admin123

或者使用命令行测试：

```bash
# 测试前端是否可访问
curl http://localhost:3000
```

## 🔐 步骤7: 配置Git和SSH（用于GitHub）

### 7.1 生成SSH密钥

```bash
# 生成SSH密钥（如果还没有）
ssh-keygen -t ed25519 -C "your.email@example.com"

# 按回车使用默认路径
# 设置密码（可选，建议设置）

# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

### 7.2 添加SSH密钥到GitHub

1. 复制公钥内容（上面命令的输出）
2. 访问 https://github.com/settings/keys
3. 点击 "New SSH key"
4. 粘贴公钥并保存

### 7.3 测试SSH连接

```bash
# 测试GitHub连接
ssh -T git@github.com

# 应该看到: Hi username! You've successfully authenticated...
```

### 7.4 初始化Git仓库（如果还没初始化）

```bash
# 进入项目目录
cd ~/projects/unified-security-scanner

# 如果目录还不是Git仓库，初始化
git init

# 添加远程仓库（替换为您的仓库地址）
git remote add origin git@github.com:your-org/unified-security-scanner.git

# 或者如果已有远程仓库
git remote -v  # 查看现有远程仓库
```

## 📝 步骤8: 创建第一个Git提交（如果还没提交）

```bash
# 进入项目目录
cd ~/projects/unified-security-scanner

# 检查当前状态
git status

# 添加所有文件
git add .

# 创建初始提交
git commit -m "feat: 初始项目提交 - 统一安全扫描平台"

# 推送到GitHub（如果已配置远程仓库）
git branch -M main  # 如果使用main分支
git push -u origin main
```

## 🧪 步骤9: 测试功能

### 9.1 测试登录

1. 访问 http://localhost:3000
2. 使用 admin / admin123 登录
3. 确认能成功登录

### 9.2 测试项目管理

1. 点击 "项目管理"
2. 创建测试项目
3. 确认项目创建成功

### 9.3 测试扫描功能

1. 点击 "扫描任务"
2. 创建测试扫描（选择任意类型）
3. 查看扫描结果

### 9.4 测试RASP功能（如果OpenRASP已配置）

1. 点击 "RASP事件"
2. 查看OpenRASP连接状态
3. 尝试同步事件

## 📚 步骤10: 学习Git工作流

```bash
# 阅读Git工作流文档
cat docs/团队分工与Git工作流.md

# 或者使用浏览器打开
xdg-open docs/团队分工与Git工作流.md
```

### 10.1 创建功能分支

```bash
# 创建develop分支（如果还不存在）
git checkout -b develop

# 创建功能分支
git checkout -b feature/test-feature

# 进行开发...

# 提交更改
git add .
git commit -m "feat: 添加测试功能"
```

## 🎯 下一步行动

根据您的角色，选择相应的任务：

### 如果您是前端开发人员

```bash
# 进入前端目录
cd frontend

# 安装依赖（如果需要本地开发）
npm install

# 启动开发服务器（如果使用本地开发）
npm start
```

### 如果您是后端开发人员

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（如果需要本地开发）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python app.py
```

### 如果您是DevOps工程师

```bash
# 优化Docker配置
# 配置CI/CD
# 设置监控和日志
```

## 🔍 常见问题排查

### 问题1: Docker命令需要sudo

**解决**: 重新登录或执行 `newgrp docker`

### 问题2: 端口被占用

**解决**: 
```bash
# 查找占用端口的进程
sudo lsof -i :3000
sudo lsof -i :5000

# 杀死进程或修改docker-compose.yml中的端口
```

### 问题3: 服务启动失败

**解决**:
```bash
# 查看详细错误日志
docker-compose logs --tail=100

# 重建服务
docker-compose down
docker-compose up -d --build
```

### 问题4: 无法访问Web界面

**解决**:
```bash
# 检查防火墙
sudo ufw status

# 如果防火墙开启，允许端口
sudo ufw allow 3000
sudo ufw allow 5000
```

## 📖 参考文档

- [开发环境部署指南](开发环境部署指南.md)
- [安装部署手册](../docs/安装部署手册.md)
- [团队分工与Git工作流](团队分工与Git工作流.md)
- [QUICKSTART.md](../../QUICKSTART.md)

## ✅ 检查清单

完成以下检查清单，确认所有步骤已完成：

- [ ] Docker已安装并运行
- [ ] Docker Compose已安装
- [ ] Git已安装并配置
- [ ] 项目代码已获取到Ubuntu
- [ ] 服务已成功启动（docker-compose ps显示所有服务Up）
- [ ] 数据库已初始化（能执行init_db.py）
- [ ] Web界面可访问（http://localhost:3000）
- [ ] 能够成功登录（admin/admin123）
- [ ] SSH密钥已生成并添加到GitHub
- [ ] Git仓库已初始化或连接到远程仓库

---

**现在您应该**: 根据上述步骤，从步骤1开始检查，确定您当前在哪个步骤，然后继续执行后续步骤。

如果遇到问题，请查看相应的文档或检查常见问题部分。

