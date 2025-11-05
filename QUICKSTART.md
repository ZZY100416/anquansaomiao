# 快速开始指南

## 5分钟快速部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd unified-security-scanner
```

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 初始化数据库

```bash
docker-compose exec backend python init_db.py
```

### 4. 访问应用

- Web界面: http://localhost:3000
- 默认账号: admin / admin123

## Ubuntu虚拟机开发环境

### 完整环境搭建

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. 安装Git
sudo apt install -y git

# 4. 配置Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 5. 生成SSH密钥
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub
# 复制公钥添加到GitHub

# 6. 克隆项目
git clone git@github.com:your-org/unified-security-scanner.git
cd unified-security-scanner

# 7. 启动服务
docker-compose up -d

# 8. 初始化数据库
docker-compose exec backend python init_db.py
```

## 下一步

1. 阅读 [README.md](README.md) 了解项目概览
2. 阅读 [安装部署手册](docs/安装部署手册.md) 了解详细配置
3. 阅读 [开发环境部署指南](docs/开发环境部署指南.md) 搭建开发环境
4. 阅读 [团队分工与Git工作流](docs/团队分工与Git工作流.md) 了解协作流程

## 常用命令

```bash
# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 重建服务
docker-compose up -d --build

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 初始化数据库
docker-compose exec backend python init_db.py
```

## 项目结构

```
unified-security-scanner/
├── backend/          # 后端服务
├── frontend/         # 前端应用
├── docs/            # 文档目录
├── docker-compose.yml
└── README.md
```

## 需要帮助？

- 查看 [常见问题](docs/安装部署手册.md#常见问题)
- 查看 [开发环境部署指南](docs/开发环境部署指南.md)
- 提交 Issue

