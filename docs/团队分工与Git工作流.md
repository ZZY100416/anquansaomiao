# 团队分工与Git工作流

## 目录

1. [团队角色分工](#团队角色分工)
2. [Git工作流](#git工作流)
3. [开发环境部署](#开发环境部署)
4. [代码提交规范](#代码提交规范)
5. [分支管理策略](#分支管理策略)
6. [Pull Request流程](#pull-request流程)
7. [常见问题](#常见问题)

## 团队角色分工

### 项目结构分工

根据统一安全扫描平台的功能模块，建议按以下方式分工：

#### 1. 前端开发组（Frontend Team）

**负责人**: 前端开发工程师

**职责**:
- Web界面开发
- 用户交互优化
- 前端性能优化
- UI/UX设计实现

**负责模块**:
- `frontend/` 目录
- React组件开发
- API集成
- 状态管理

**技术栈**:
- React 18
- Ant Design
- Axios
- ECharts

#### 2. 后端开发组（Backend Team）

**负责人**: 后端开发工程师

**职责**:
- API服务开发
- 数据库设计
- 业务逻辑实现
- 性能优化

**负责模块**:
- `backend/` 目录
- API路由和控制器
- 数据模型
- 业务服务

**技术栈**:
- Python Flask
- SQLAlchemy
- PostgreSQL
- JWT认证

#### 3. 扫描器集成组（Scanner Integration Team）

**负责人**: 安全工程师

**职责**:
- 扫描器集成
- 扫描规则配置
- 结果解析和处理
- 扫描性能优化

**负责模块**:
- `backend/app/scanners/` 目录
- SAST扫描器（Semgrep）
- SCA扫描器（Dependency-Check）
- 容器扫描器（Trivy）

**技术栈**:
- Python
- Semgrep
- OWASP Dependency-Check
- Trivy

#### 4. 基础设施组（Infrastructure Team）

**负责人**: DevOps工程师

**职责**:
- Docker容器化
- CI/CD流程
- 部署脚本
- 监控和日志

**负责模块**:
- `docker-compose.yml`
- Dockerfile文件
- CI/CD配置
- 部署文档

**技术栈**:
- Docker
- Docker Compose
- CI/CD平台（GitHub Actions/GitLab CI）

#### 5. 测试组（Testing Team）

**负责人**: 测试工程师

**职责**:
- 功能测试
- 集成测试
- 安全测试
- 性能测试

**负责模块**:
- 测试用例编写
- 测试自动化
- 测试报告

#### 6. 文档组（Documentation Team）

**负责人**: 技术文档工程师

**职责**:
- 用户文档编写
- API文档维护
- 开发文档更新
- 培训材料准备

**负责模块**:
- `docs/` 目录
- README文件
- 代码注释

### 团队协作流程

```
需求分析 → 任务分配 → 并行开发 → 代码审查 → 集成测试 → 部署发布
```

## Git工作流

### 工作流模型

采用 **Git Flow** 工作流模型，适合团队协作和持续集成。

### 分支结构

```
main (生产环境)
  ├── develop (开发环境)
  │   ├── feature/xxx (功能分支)
  │   ├── bugfix/xxx (Bug修复分支)
  │   └── hotfix/xxx (紧急修复分支)
  └── release/xxx (发布分支)
```

### 分支说明

#### main 分支

- **用途**: 生产环境代码
- **保护**: 禁止直接推送，必须通过Pull Request
- **合并**: 只能从release或hotfix分支合并
- **标签**: 每次合并打版本标签（v1.0.0）

#### develop 分支

- **用途**: 开发环境代码
- **保护**: 允许团队成员推送
- **合并**: 从feature和bugfix分支合并
- **部署**: 自动部署到开发环境

#### feature 分支

- **命名**: `feature/功能名称`，如 `feature/user-authentication`
- **创建**: 从develop分支创建
- **用途**: 新功能开发
- **合并**: 完成后合并到develop
- **删除**: 合并后删除

#### bugfix 分支

- **命名**: `bugfix/问题描述`，如 `bugfix/login-error`
- **创建**: 从develop分支创建
- **用途**: Bug修复
- **合并**: 完成后合并到develop

#### hotfix 分支

- **命名**: `hotfix/问题描述`，如 `hotfix/security-patch`
- **创建**: 从main分支创建
- **用途**: 生产环境紧急修复
- **合并**: 同时合并到main和develop
- **优先级**: 最高

#### release 分支

- **命名**: `release/版本号`，如 `release/v1.0.0`
- **创建**: 从develop分支创建
- **用途**: 发布准备
- **合并**: 完成后合并到main和develop
- **活动**: Bug修复、版本号更新、文档更新

### 分支创建示例

```bash
# 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/user-dashboard

# 创建Bug修复分支
git checkout develop
git pull origin develop
git checkout -b bugfix/login-error

# 创建紧急修复分支
git checkout main
git pull origin main
git checkout -b hotfix/security-patch
```

## 开发环境部署

### Ubuntu虚拟机环境搭建

#### 1. 系统要求

- Ubuntu 20.04 LTS 或更高版本
- 至少4GB内存
- 至少20GB磁盘空间
- 网络连接

#### 2. 安装基础工具

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    build-essential \
    python3-pip \
    nodejs \
    npm
```

#### 3. 安装Docker

```bash
# 卸载旧版本
sudo apt remove docker docker-engine docker.io containerd runc

# 安装依赖
sudo apt install -y \
    ca-certificates \
    gnupg \
    lsb-release

# 添加Docker官方GPG密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组（避免每次使用sudo）
sudo usermod -aG docker $USER

# 验证安装
docker --version
docker compose version
```

**注意**: 添加用户到docker组后，需要重新登录才能生效。

#### 4. 安装Git

```bash
# 安装Git
sudo apt install -y git

# 配置Git用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 生成SSH密钥（用于GitHub认证）
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub
# 复制公钥内容，添加到GitHub账户设置中
```

#### 5. 克隆项目

```bash
# 创建项目目录
mkdir -p ~/projects
cd ~/projects

# 克隆项目（如果已创建GitHub仓库）
git clone git@github.com:your-org/unified-security-scanner.git
cd unified-security-scanner

# 或者初始化新仓库
git init
git remote add origin git@github.com:your-org/unified-security-scanner.git
```

#### 6. 配置开发环境

```bash
# 创建Python虚拟环境（如果本地开发）
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 安装前端依赖（如果本地开发）
cd ../frontend
npm install
```

#### 7. 启动开发环境

```bash
# 使用Docker Compose启动（推荐）
cd ~/projects/unified-security-scanner
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### Windows开发环境（可选）

如果需要在Windows上开发：

1. 安装WSL2（Windows Subsystem for Linux）
2. 在WSL2中按照Ubuntu环境搭建步骤操作
3. 使用VS Code的Remote WSL扩展

### IDE推荐配置

#### VS Code

推荐扩展：
- Python
- ESLint
- Prettier
- Docker
- GitLens
- Remote - WSL

配置 `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

## 代码提交规范

### 提交信息格式

采用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构（既不是新功能也不是Bug修复）
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `security`: 安全相关

### 提交示例

```bash
# 新功能
git commit -m "feat(backend): 添加用户认证功能"

# Bug修复
git commit -m "fix(frontend): 修复登录页面样式问题"

# 文档更新
git commit -m "docs: 更新API接口文档"

# 重构
git commit -m "refactor(scanner): 重构扫描器服务代码"

# 安全修复
git commit -m "security(api): 修复SQL注入漏洞"
```

### 提交信息最佳实践

1. **使用中文或英文**: 团队统一语言
2. **简洁明了**: 第一行不超过50字符
3. **详细描述**: 复杂变更在body中说明
4. **关联Issue**: 使用 `#123` 关联Issue

### Git Hooks配置

创建 `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# 运行代码检查
echo "Running code checks..."

# Python代码检查
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
    flake8 app/ || exit 1
    black --check app/ || exit 1
fi

# JavaScript代码检查
cd ../frontend
npm run lint || exit 1

echo "All checks passed!"
```

## 分支管理策略

### 功能开发流程

```bash
# 1. 从develop创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/user-dashboard

# 2. 开发功能，多次提交
git add .
git commit -m "feat(frontend): 添加用户仪表盘组件"
git commit -m "feat(backend): 添加仪表盘API接口"

# 3. 推送到远程
git push origin feature/user-dashboard

# 4. 创建Pull Request到develop分支
# 在GitHub/GitLab上创建PR

# 5. 代码审查通过后合并
# 在GitHub/GitLab上点击合并按钮

# 6. 删除本地分支
git checkout develop
git pull origin develop
git branch -d feature/user-dashboard
```

### Bug修复流程

```bash
# 1. 从develop创建bugfix分支
git checkout develop
git pull origin develop
git checkout -b bugfix/login-error

# 2. 修复Bug并提交
git add .
git commit -m "fix(auth): 修复登录验证逻辑错误"

# 3. 推送到远程并创建PR
git push origin bugfix/login-error
# 创建PR到develop分支
```

### 紧急修复流程

```bash
# 1. 从main创建hotfix分支
git checkout main
git pull origin main
git checkout -b hotfix/security-patch

# 2. 修复问题并提交
git add .
git commit -m "hotfix(security): 紧急修复安全漏洞"

# 3. 推送到远程
git push origin hotfix/security-patch

# 4. 创建PR到main分支（快速审查和合并）

# 5. 合并到develop
git checkout develop
git pull origin develop
git merge hotfix/security-patch
git push origin develop
```

## Pull Request流程

### PR创建步骤

1. **确保代码最新**: 
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/your-feature
   git rebase develop  # 或 git merge develop
   ```

2. **推送分支**:
   ```bash
   git push origin feature/your-feature
   ```

3. **创建PR**: 在GitHub/GitLab上创建Pull Request

### PR模板

创建 `.github/pull_request_template.md`:

```markdown
## 变更类型
- [ ] 新功能
- [ ] Bug修复
- [ ] 文档更新
- [ ] 重构
- [ ] 性能优化

## 变更描述
<!-- 描述本次PR的变更内容 -->

## 相关Issue
<!-- 关联的Issue编号，如 #123 -->

## 测试说明
<!-- 说明如何测试本次变更 -->

## 检查清单
- [ ] 代码已通过lint检查
- [ ] 已添加/更新单元测试
- [ ] 文档已更新
- [ ] 已通过本地测试
```

### PR审查流程

1. **自动检查**: CI/CD自动运行测试和代码检查
2. **代码审查**: 至少1名团队成员审查
3. **修改**: 根据审查意见修改代码
4. **批准**: 审查者批准后合并
5. **合并**: 使用Squash Merge或Rebase Merge

### PR合并规则

- ✅ 至少1个批准
- ✅ 所有CI检查通过
- ✅ 无冲突
- ✅ 代码审查通过

## 常见问题

### Q1: 如何解决分支冲突？

**A**: 

```bash
# 1. 获取最新代码
git checkout develop
git pull origin develop

# 2. 切换到你的分支
git checkout feature/your-feature

# 3. 合并或变基
git rebase develop  # 推荐使用rebase保持提交历史清晰
# 或
git merge develop

# 4. 解决冲突
# 编辑冲突文件，解决冲突标记

# 5. 继续rebase或完成merge
git add .
git rebase --continue  # 如果是rebase
# 或
git commit  # 如果是merge
```

### Q2: 如何撤销已推送的提交？

**A**: 

```bash
# 谨慎操作！如果其他人已拉取，使用revert
git revert <commit-hash>
git push origin branch-name

# 如果确定要修改历史（危险操作）
git reset --hard <commit-hash>
git push --force origin branch-name  # 不推荐，除非在个人分支
```

### Q3: 如何同步远程分支？

**A**: 

```bash
# 获取所有远程分支信息
git fetch origin

# 查看远程分支
git branch -r

# 切换到远程分支（创建本地跟踪分支）
git checkout -b local-branch origin/remote-branch

# 更新跟踪分支
git pull origin branch-name
```

### Q4: 如何查看提交历史？

**A**: 

```bash
# 查看提交历史
git log

# 查看图形化历史
git log --graph --oneline --all

# 查看某个文件的修改历史
git log --follow -- filename

# 查看某个提交的详细内容
git show <commit-hash>
```

### Q5: 如何创建和管理标签？

**A**: 

```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0

# 查看所有标签
git tag

# 删除标签
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

## GitHub仓库设置

### 分支保护规则

在GitHub仓库设置中配置：

1. **main分支保护**:
   - 要求Pull Request审查
   - 要求状态检查通过
   - 禁止强制推送
   - 禁止删除分支

2. **develop分支保护**:
   - 要求状态检查通过
   - 允许团队成员直接推送

### CI/CD配置

创建 `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop, main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest
```

## 学习资源

### Git学习

- [Git官方文档](https://git-scm.com/doc)
- [Pro Git Book](https://git-scm.com/book)
- [GitHub Guides](https://guides.github.com/)

### 团队协作

- [Git Flow工作流](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

### 最佳实践

- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub最佳实践](https://guides.github.com/)

