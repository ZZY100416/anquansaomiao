# Git工作流程指南 - Windows本地修改同步到Ubuntu

## 📋 工作流程概览

```
Windows本地修改 → 提交到Git → 推送到GitHub → Ubuntu pull更新
```

## 🪟 Windows上操作（提交和推送）

### 步骤1: 查看修改的文件

```powershell
# 在PowerShell中，进入项目目录
cd E:\network\anquannchanpin

# 查看哪些文件被修改了
git status

# 查看具体的修改内容
git diff
```

### 步骤2: 添加修改的文件

```powershell
# 添加所有修改的文件
git add .

# 或者只添加特定文件
git add backend/Dockerfile
git add docs/构建错误修复指南.md

# 查看已暂存的文件
git status
```

### 步骤3: 提交修改

```powershell
# 提交修改（使用清晰的提交信息）
git commit -m "fix: 修复Dockerfile中apt-key废弃问题"

# 提交信息格式建议：
# fix: 修复bug
# feat: 新功能
# docs: 文档更新
# style: 代码格式
# refactor: 重构
```

### 步骤4: 推送到GitHub

```powershell
# 推送到远程仓库
git push origin main

# 如果是第一次推送，可能需要设置上游分支
git push -u origin main

# 如果推送失败，可能需要先拉取远程更新
git pull origin main
# 解决冲突后，再推送
git push origin main
```

### 完整示例

```powershell
# 1. 进入项目目录
cd E:\network\anquannchanpin

# 2. 查看状态
git status

# 3. 添加所有修改
git add .

# 4. 提交
git commit -m "fix: 修复Dockerfile构建错误，更新apt-key为新的GPG管理方式"

# 5. 推送
git push origin main
```

## 🐧 Ubuntu上操作（拉取更新）

### 步骤1: 进入项目目录

```bash
# 进入项目目录
cd ~/projects/anquansaomiao
# 或您的实际路径
```

### 步骤2: 查看当前状态

```bash
# 查看当前分支和状态
git status

# 查看远程仓库信息
git remote -v

# 查看本地和远程的差异
git fetch origin
git log HEAD..origin/main
```

### 步骤3: 拉取更新

```bash
# 方法1: 使用pull（推荐）
git pull origin main

# 方法2: 先fetch再merge（更安全）
git fetch origin
git merge origin/main

# 如果本地有未提交的修改，先暂存
git stash
git pull origin main
git stash pop  # 恢复暂存的修改
```

### 步骤4: 处理冲突（如果有）

```bash
# 如果出现冲突，Git会提示
# 查看冲突文件
git status

# 编辑冲突文件，解决冲突
nano 冲突的文件名

# 解决冲突后，标记为已解决
git add 冲突的文件名

# 完成合并
git commit -m "merge: 合并远程更新"
```

### 步骤5: 重启服务（如果代码有重要更新）

```bash
# 如果修改了Dockerfile或docker-compose.yml，需要重建
docker-compose down
docker-compose up -d --build

# 如果只是修改了应用代码，重启服务即可
docker-compose restart backend
docker-compose restart frontend
```

## 🔄 完整工作流程示例

### 场景：修复Dockerfile后同步

**Windows上**:
```powershell
cd E:\network\anquannchanpin

# 1. 查看修改
git status

# 2. 添加修改
git add backend/Dockerfile

# 3. 提交
git commit -m "fix: 修复Dockerfile中apt-key废弃问题，添加lsb-release依赖"

# 4. 推送
git push origin main
```

**Ubuntu上**:
```bash
cd ~/projects/anquansaomiao

# 1. 拉取更新
git pull origin main

# 2. 因为修改了Dockerfile，需要重建
docker-compose down
docker-compose up -d --build

# 3. 查看服务状态
docker-compose ps
```

## 📝 Git提交信息规范

建议使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```powershell
# 格式: <type>(<scope>): <subject>

# 类型说明:
git commit -m "feat: 添加新功能"
git commit -m "fix: 修复bug"
git commit -m "docs: 更新文档"
git commit -m "style: 代码格式调整"
git commit -m "refactor: 重构代码"
git commit -m "test: 添加测试"
git commit -m "chore: 构建/工具变更"

# 示例:
git commit -m "fix(backend): 修复Dockerfile构建错误"
git commit -m "feat(frontend): 添加RASP事件页面"
git commit -m "docs: 添加Git工作流程指南"
```

## 🔍 常用Git命令

### Windows上常用命令

```powershell
# 查看状态
git status

# 查看修改内容
git diff

# 查看提交历史
git log --oneline -10

# 撤销未提交的修改
git checkout -- 文件名
git restore 文件名

# 撤销已暂存的文件
git reset HEAD 文件名
git restore --staged 文件名

# 修改最后一次提交信息
git commit --amend -m "新的提交信息"
```

### Ubuntu上常用命令

```bash
# 查看状态
git status

# 查看远程更新（不合并）
git fetch origin

# 查看本地和远程的差异
git diff HEAD origin/main

# 查看提交历史
git log --oneline --graph -10

# 切换到其他分支
git checkout 分支名

# 创建新分支
git checkout -b feature/新功能
```

## ⚠️ 常见问题

### Q1: 推送时提示"需要先pull"

**解决**:
```powershell
# Windows上
git pull origin main
# 解决冲突后
git push origin main
```

### Q2: Ubuntu上pull时提示"本地有未提交的修改"

**解决**:
```bash
# 方法1: 暂存修改
git stash
git pull origin main
git stash pop

# 方法2: 提交本地修改
git add .
git commit -m "本地修改"
git pull origin main
```

### Q3: 推送时提示"权限被拒绝"

**解决**:
```powershell
# 检查SSH密钥配置
ssh -T git@github.com

# 或使用HTTPS方式
git remote set-url origin https://github.com/your-username/unified-security-scanner.git
```

### Q4: 冲突解决

**解决**:
```bash
# 1. 查看冲突文件
git status

# 2. 编辑冲突文件，找到冲突标记
# <<<<<<< HEAD
# 本地修改
# =======
# 远程修改
# >>>>>>> origin/main

# 3. 手动解决冲突，删除冲突标记
# 保留需要的代码

# 4. 标记为已解决
git add 冲突文件

# 5. 完成合并
git commit
```

## 🎯 最佳实践

### 1. 频繁提交

- ✅ 每次完成一个小功能就提交
- ✅ 提交信息要清晰明确
- ✅ 不要提交未完成的代码

### 2. 提交前检查

```powershell
# Windows上提交前
git status          # 确认要提交的文件
git diff            # 查看修改内容
git commit -m "..." # 提交
```

### 3. 推送前拉取

```powershell
# 推送前先拉取，避免冲突
git pull origin main
git push origin main
```

### 4. Ubuntu上更新前备份

```bash
# 如果有重要修改，先创建分支
git checkout -b backup/当前日期
git add .
git commit -m "备份"
git checkout main
git pull origin main
```

## 📚 快速参考

### Windows → GitHub → Ubuntu 流程

```powershell
# === Windows ===
cd E:\network\anquannchanpin
git add .
git commit -m "fix: 修复问题"
git push origin main

# === Ubuntu ===
cd ~/projects/anquansaomiao
git pull origin main
docker-compose restart  # 或重建
```

---

**现在您可以：**
1. 在Windows上修改代码
2. 提交并推送到GitHub
3. 在Ubuntu上pull更新
4. 重启服务使更新生效

如有问题，请告诉我！

