# GitHub安全扫描配置指南

## 概述

本指南说明如何在GitHub上配置SAST（静态应用安全测试）和SCA（软件组成分析）扫描，实现DevSecOps流程中的自动化安全检测。

## 已配置的扫描工具

### SAST扫描工具

1. **Semgrep** - 静态代码安全分析
   - 支持多种语言
   - 自动检测常见安全漏洞
   - 配置：`.github/workflows/security-scan.yml`

2. **Bandit** - Python代码安全扫描
   - 专门针对Python代码
   - 检测常见安全问题
   - 配置：`.github/workflows/security-scan.yml`

3. **GitHub CodeQL** - GitHub官方代码分析
   - 深度代码分析
   - 自动发现漏洞模式
   - 配置：`.github/workflows/codeql-analysis.yml`

### SCA扫描工具

1. **pip-audit** - Python依赖漏洞扫描
   - 检查Python包的安全漏洞
   - 基于PyPI安全数据库

2. **npm audit** - Node.js依赖漏洞扫描
   - 检查npm包的安全漏洞
   - 集成npm官方安全数据库

3. **OWASP Dependency-Check** - 综合依赖扫描
   - 支持多种语言和包管理器
   - 使用NVD数据库
   - 生成详细报告

4. **Syft** - SBOM生成工具
   - 生成软件物料清单
   - 支持多种格式（SPDX、CycloneDX）

### 容器扫描工具

1. **Trivy** - 容器镜像漏洞扫描
   - 扫描Docker镜像
   - 检测已知CVE漏洞

2. **Hadolint** - Dockerfile安全检查
   - Dockerfile最佳实践检查
   - 安全配置验证

## 工作流说明

### 1. 安全扫描工作流 (`security-scan.yml`)

**触发条件**:
- 推送到 main/develop 分支
- 创建Pull Request
- 每天凌晨2点定时扫描

**执行任务**:
- SAST扫描（Semgrep + Bandit）
- SCA扫描（pip-audit + npm audit + Dependency-Check）
- SBOM生成（Syft）
- 容器镜像扫描（Trivy）

### 2. CodeQL分析工作流 (`codeql-analysis.yml`)

**触发条件**:
- 推送到 main/develop 分支
- 创建Pull Request
- 每天凌晨3点定时扫描

**执行任务**:
- Python代码分析
- JavaScript代码分析
- 结果上传到GitHub Security标签

### 3. Docker安全扫描工作流 (`docker-security.yml`)

**触发条件**:
- Dockerfile文件变更时
- 推送到main分支

**执行任务**:
- Dockerfile语法和最佳实践检查
- 容器镜像漏洞扫描

### 4. Dependabot自动依赖更新 (`dependabot.yml`)

**功能**:
- 每周自动检查依赖更新
- 自动创建更新PR
- 支持Python和Node.js依赖

## 使用步骤

### 步骤1: 将代码推送到GitHub

```bash
# 在Ubuntu虚拟机上执行

# 1. 初始化Git仓库（如果还没初始化）
cd ~/projects/unified-security-scanner
git init

# 2. 添加所有文件
git add .

# 3. 创建初始提交
git commit -m "feat: 初始提交 - 统一安全扫描平台"

# 4. 添加远程仓库
git remote add origin git@github.com:your-username/unified-security-scanner.git

# 5. 推送到GitHub
git branch -M main
git push -u origin main
```

### 步骤2: 在GitHub上启用安全功能

1. **启用GitHub Actions**
   - 访问仓库设置: Settings → Actions → General
   - 确保 "Allow all actions and reusable workflows" 已启用

2. **启用Dependabot**
   - 访问仓库设置: Settings → Security → Code security and analysis
   - 启用 "Dependabot alerts"
   - 启用 "Dependabot security updates"

3. **启用Code Scanning**
   - 访问: Settings → Security → Code security and analysis
   - 启用 "Code scanning"
   - 启用 "Secret scanning"

### 步骤3: 查看扫描结果

#### 查看GitHub Actions结果

1. 访问仓库的 "Actions" 标签
2. 选择对应的Workflow
3. 查看运行结果和日志
4. 下载Artifacts查看详细报告

#### 查看Security标签

1. 访问仓库的 "Security" 标签
2. 查看:
   - **Code scanning alerts**: CodeQL发现的问题
   - **Dependabot alerts**: 依赖漏洞警报
   - **Secret scanning**: 泄露的密钥

#### 查看Pull Request中的结果

1. 创建Pull Request时，GitHub Actions会自动运行
2. 在PR页面可以看到：
   - 检查状态（✅ 或 ❌）
   - 安全扫描结果摘要
   - 详细的评论报告

## 扫描结果处理

### 严重级别说明

- **CRITICAL（严重）**: 必须立即修复
- **HIGH（高危）**: 应该尽快修复
- **MEDIUM（中危）**: 计划修复
- **LOW（低危）**: 评估修复
- **INFO（信息）**: 了解即可

### 处理流程

1. **查看警报**
   ```
   GitHub仓库 → Security标签 → Code scanning alerts
   ```

2. **分析问题**
   - 查看漏洞详情
   - 理解影响范围
   - 评估修复优先级

3. **创建修复分支**
   ```bash
   git checkout -b fix/security-issue-123
   ```

4. **修复问题**
   - 根据建议修复代码
   - 更新依赖版本
   - 添加安全配置

5. **提交修复**
   ```bash
   git add .
   git commit -m "fix(security): 修复CVE-2023-XXXXX漏洞"
   git push origin fix/security-issue-123
   ```

6. **创建PR**
   - 创建Pull Request
   - 等待扫描验证
   - 合并修复

## 配置优化

### 自定义扫描规则

#### Semgrep规则

创建 `.semgrep.yml` 文件：

```yaml
rules:
  - id: detect-sql-injection
    pattern: |
      query = "SELECT * FROM $X WHERE id = " + $Y
    message: 检测到SQL注入风险
    languages: [python]
    severity: ERROR
```

#### Bandit配置

创建 `.bandit` 文件：

```ini
[bandit]
exclude_dirs = tests,venv,node_modules
skips = B101,B601
```

### 设置扫描门禁

在 `.github/workflows/security-scan.yml` 中设置：

```yaml
# 如果发现严重漏洞，阻止合并
- name: Check scan results
  run: |
    if [ -f semgrep-results.json ]; then
      python3 -c "
      import json
      with open('semgrep-results.json') as f:
        data = json.load(f)
        critical = [r for r in data.get('results', []) 
                   if r.get('extra', {}).get('severity') == 'ERROR']
        if critical:
          print(f'Found {len(critical)} critical issues')
          exit(1)
      "
    fi
```

### 通知配置

#### 邮件通知

在仓库设置中配置：
- Settings → Notifications
- 启用 "Security alerts"

#### Slack集成

使用GitHub Apps集成Slack：
1. 安装GitHub App到Slack
2. 配置通知频道
3. 选择安全警报类型

## 最佳实践

### 1. 定期扫描

- ✅ 每次代码推送自动扫描
- ✅ 每天定时扫描
- ✅ Pull Request时扫描

### 2. 及时处理

- ✅ 严重漏洞24小时内修复
- ✅ 高危漏洞一周内修复
- ✅ 定期审查所有警报

### 3. 依赖管理

- ✅ 定期更新依赖
- ✅ 使用Dependabot自动更新
- ✅ 审查依赖更新

### 4. 安全门禁

- ✅ 设置严重漏洞阻止合并
- ✅ 要求安全扫描通过才能合并
- ✅ 代码审查包含安全检查

### 5. 文档记录

- ✅ 记录安全修复过程
- ✅ 更新安全策略
- ✅ 分享安全经验

## 常见问题

### Q1: 扫描失败怎么办？

**A**: 
1. 查看GitHub Actions日志
2. 检查网络连接
3. 确认依赖已正确安装
4. 查看错误信息并修复

### Q2: 如何忽略误报？

**A**: 
1. 在Semgrep中使用 `# nosemgrep` 注释
2. 在Bandit中使用 `# nosec` 注释
3. 在GitHub Security中标记为误报

### Q3: 如何加快扫描速度？

**A**:
1. 使用缓存（已配置）
2. 只扫描变更的文件
3. 并行运行多个扫描任务
4. 使用更快的扫描工具

### Q4: 如何查看历史扫描结果？

**A**:
1. GitHub Actions → 查看历史运行
2. Security标签 → 查看警报历史
3. 下载Artifacts查看详细报告

## 参考资源

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [CodeQL文档](https://codeql.github.com/docs/)
- [Semgrep文档](https://semgrep.dev/docs/)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [Trivy文档](https://aquasecurity.github.io/trivy/)

## 下一步

1. ✅ 将代码推送到GitHub
2. ✅ 启用GitHub Actions
3. ✅ 查看首次扫描结果
4. ✅ 处理发现的安全问题
5. ✅ 配置通知和门禁策略

---

**配置完成时间**: 2024-01-01  
**维护者**: 安全团队

