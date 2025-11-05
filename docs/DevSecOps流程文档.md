# 团队DevSecOps流程文档

## 目录

1. [概述](#概述)
2. [DevSecOps流程](#devsecops流程)
3. [工具链集成](#工具链集成)
4. [安全门禁](#安全门禁)
5. [最佳实践](#最佳实践)
6. [团队角色](#团队角色)

## 概述

本文档定义了团队内部的DevSecOps（开发安全运维一体化）流程，旨在将安全实践无缝集成到软件开发生命周期的各个阶段。

### 目标

- **左移安全**: 在开发早期阶段发现和修复安全问题
- **自动化**: 减少手动安全检查，提高效率
- **持续改进**: 通过反馈循环持续优化安全流程
- **合规性**: 满足安全合规要求

### 原则

1. **安全即代码**: 安全策略和配置作为代码管理
2. **自动化优先**: 自动化所有可自动化的安全检查
3. **可见性**: 安全状态对所有相关方可见
4. **协作**: 开发、安全、运维团队紧密协作

## DevSecOps流程

### 阶段1: Plan（规划阶段）

#### 1.1 安全需求管理

**目标**: 在需求阶段定义安全策略和标准

**活动**:
- 识别安全需求
- 定义安全测试标准
- 设置安全门禁（Security Gates）

**工具**:
- Jira + Security Plugin
- 需求文档模板（包含安全章节）

**输出**:
- 安全需求文档
- 安全测试标准
- 威胁模型

#### 1.2 威胁建模

**目标**: 识别系统设计中的潜在安全威胁

**活动**:
- 系统架构分析
- 威胁识别
- 风险评估
- 制定缓解措施

**工具**:
- OWASP Threat Dragon
- Microsoft Threat Modeling Tool

**输出**:
- 威胁模型文档
- 风险矩阵
- 安全设计建议

### 阶段2: Code（开发阶段）

#### 2.1 代码安全检查（SAST）

**目标**: 在编码阶段发现安全漏洞

**活动**:
- 代码提交前本地扫描
- 代码审查时安全检查
- IDE集成安全扫描

**工具**:
- Semgrep（IDE插件）
- SonarQube
- Git Hooks

**流程**:

```bash
# 开发人员本地执行
git commit -m "feat: add new feature"
# 触发 pre-commit hook，执行SAST扫描
# 如果发现高危漏洞，阻止提交
```

**门禁规则**:
- 严重漏洞：阻止提交
- 高危漏洞：阻止提交
- 中危漏洞：警告，允许提交
- 低危/信息：记录，允许提交

#### 2.2 依赖漏洞扫描（SCA）

**目标**: 检查第三方依赖库的已知漏洞

**活动**:
- 依赖库清单管理
- 自动漏洞扫描
- 漏洞修复追踪

**工具**:
- OWASP Dependency-Check
- npm audit / pip-audit
- 统一安全扫描平台

**流程**:

```bash
# 每次安装依赖时自动扫描
npm install
# 自动触发SCA扫描
# 生成依赖漏洞报告
```

**门禁规则**:
- CVSS >= 9.0：阻止构建
- CVSS >= 7.0：警告，允许构建但需要修复计划
- CVSS < 7.0：记录，跟踪修复

#### 2.3 代码签名与完整性校验

**目标**: 确保源代码未被篡改

**活动**:
- Git提交签名
- 代码完整性校验
- 供应链安全

**工具**:
- Git GPG签名
- Sigstore

### 阶段3: Build（构建阶段）

#### 3.1 构建安全与合规扫描

**目标**: 对构建产物进行安全审计

**活动**:
- 构建产物扫描
- 许可证合规检查
- 安全策略验证

**工具**:
- Trivy
- Anchore Engine

**CI/CD集成**:

```yaml
# .github/workflows/security.yml
- name: Build Security Scan
  run: |
    docker build -t myapp:${{ github.sha }} .
    trivy image myapp:${{ github.sha }}
```

#### 3.2 CI/CD 管道安全控制

**目标**: 在CI/CD中集成安全扫描和策略校验

**活动**:
- 自动化安全扫描
- 安全策略执行
- 扫描结果通知

**工具**:
- GitHub Actions / GitLab CI
- 统一安全扫描平台API

**流程**:

```yaml
stages:
  - build
  - security-scan
  - test
  - deploy

security-scan:
  script:
    - python security_scanner.py --project $CI_PROJECT_ID --type sast
    - python security_scanner.py --project $CI_PROJECT_ID --type sca
  allow_failure: false  # 安全扫描失败则阻止部署
```

### 阶段4: Test（测试阶段）

#### 4.1 动态应用安全测试（DAST）

**目标**: 模拟攻击测试运行中的Web应用

**活动**:
- 自动化安全测试
- 漏洞验证
- 渗透测试（可选）

**工具**:
- OWASP ZAP
- 统一安全扫描平台

**流程**:

```bash
# 在测试环境部署后
zap-baseline.py -t https://test.example.com
# 生成DAST报告
```

#### 4.2 交互式应用安全测试（IAST）

**目标**: 在应用运行时检测漏洞

**活动**:
- 运行时安全监控
- 实时漏洞检测
- 性能影响最小化

**工具**:
- Contrast Security Community Edition

### 阶段5: Release（发布阶段）

#### 5.1 容器镜像安全扫描

**目标**: 扫描Docker镜像中的漏洞与配置风险

**活动**:
- 镜像漏洞扫描
- 配置安全检查
- 镜像签名

**工具**:
- Trivy
- 统一安全扫描平台

**流程**:

```bash
# 发布前扫描
trivy image myapp:1.0.0
# 如果发现严重漏洞，阻止发布
```

#### 5.2 签名与策略管理

**目标**: 发布前进行镜像签名、策略验证

**活动**:
- 镜像签名
- 策略合规检查
- 发布审批流程

**工具**:
- Cosign
- Notary v2

### 阶段6: Deploy（部署阶段）

#### 6.1 基础设施即代码安全（IaC Security）

**目标**: 检查Terraform/K8s/YAML等配置安全性

**活动**:
- IaC配置扫描
- 安全策略验证
- 合规性检查

**工具**:
- Checkov
- Terrascan
- kube-score

#### 6.2 配置合规检测

**目标**: 自动验证系统/云环境配置是否符合基线

**活动**:
- 配置基线检查
- 合规性审计
- 自动修复建议

**工具**:
- OpenSCAP
- CIS-CAT

### 阶段7: Operate（运行阶段）

#### 7.1 容器与主机运行时安全

**目标**: 监控容器、进程、网络行为异常

**活动**:
- 运行时行为监控
- 异常检测
- 安全事件响应

**工具**:
- Falco
- Sysdig OSS

#### 7.2 日志与审计分析

**目标**: 集中收集日志，检测攻击行为

**活动**:
- 日志聚合
- 安全事件分析
- 威胁检测

**工具**:
- ELK Stack
- Wazuh

### 阶段8: Monitor（持续监控）

#### 8.1 安全监控与告警

**目标**: 持续监测安全事件、基线偏移

**活动**:
- 实时安全监控
- 告警通知
- 事件响应

**工具**:
- Prometheus + Alertmanager
- Grafana

#### 8.2 合规性与报告

**目标**: 输出安全态势报告与审计追踪

**活动**:
- 定期安全报告
- 合规性审计
- 趋势分析

**工具**:
- 统一安全扫描平台报告功能
- DefectDojo

## 工具链集成

### 工具清单

| 阶段 | 工具 | 用途 |
|------|------|------|
| Code | Semgrep | SAST扫描 |
| Code | Dependency-Check | SCA扫描 |
| Build | Trivy | 容器扫描 |
| Test | OWASP ZAP | DAST扫描 |
| Deploy | Checkov | IaC安全 |
| Operate | Falco | 运行时安全 |
| Monitor | Prometheus | 监控告警 |

### 统一安全扫描平台集成

统一安全扫描平台作为核心工具，集成多个扫描引擎：

```python
# CI/CD集成示例
import requests

def run_security_scan(project_id, scan_type):
    api_url = "http://security-scanner:5000/api"
    token = os.getenv("SCANNER_TOKEN")
    
    # 创建扫描任务
    response = requests.post(
        f"{api_url}/scans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "project_id": project_id,
            "scan_type": scan_type,
            "config": {}
        }
    )
    
    scan_id = response.json()["id"]
    
    # 等待扫描完成
    while True:
        status = get_scan_status(scan_id)
        if status == "completed":
            break
        elif status == "failed":
            raise Exception("扫描失败")
        time.sleep(5)
    
    # 检查结果
    results = get_scan_results(scan_id)
    critical_vulns = [r for r in results if r["severity"] == "critical"]
    
    if critical_vulns:
        raise Exception("发现严重漏洞，阻止部署")
```

## 安全门禁

### 门禁策略

#### 代码提交门禁

- ✅ 通过SAST扫描（无严重/高危漏洞）
- ✅ 通过代码审查
- ✅ 通过单元测试
- ✅ 通过依赖扫描（无严重漏洞）

#### 构建门禁

- ✅ 通过构建安全扫描
- ✅ 通过许可证合规检查
- ✅ 通过镜像漏洞扫描

#### 部署门禁

- ✅ 通过DAST扫描
- ✅ 通过IaC安全扫描
- ✅ 通过配置合规检查
- ✅ 安全团队审批（高危漏洞）

### 门禁配置示例

```yaml
# .security-gates.yml
gates:
  commit:
    sast:
      enabled: true
      block_on: ["critical", "high"]
    sca:
      enabled: true
      block_on_cvss: 9.0
  
  build:
    container_scan:
      enabled: true
      block_on: ["critical"]
  
  deploy:
    dast:
      enabled: true
      block_on: ["critical"]
    approval_required:
      enabled: true
      when: "high_vulnerabilities > 5"
```

## 最佳实践

### 1. 安全左移

- 在需求阶段考虑安全
- 编码时遵循安全编码规范
- 使用安全框架和库
- 定期进行安全培训

### 2. 自动化优先

- 所有安全检查自动化
- 集成到CI/CD流程
- 减少人工干预
- 快速反馈

### 3. 持续改进

- 定期审查安全流程
- 分析安全事件
- 优化扫描规则
- 更新工具链

### 4. 协作文化

- 安全团队与开发团队协作
- 共享安全知识
- 建立安全社区
- 奖励安全贡献

### 5. 可见性

- 安全仪表盘
- 实时安全状态
- 定期安全报告
- 安全指标追踪

## 团队角色

### 开发人员

**职责**:
- 编写安全代码
- 执行本地安全扫描
- 修复安全漏洞
- 参与代码审查

**工具使用**:
- IDE安全插件
- 本地扫描工具
- Git Hooks

### 安全工程师

**职责**:
- 定义安全策略
- 配置安全工具
- 分析安全事件
- 安全培训

**工具使用**:
- 统一安全扫描平台
- 安全分析工具
- 威胁建模工具

### DevOps工程师

**职责**:
- 集成安全工具到CI/CD
- 维护安全基础设施
- 监控安全状态
- 自动化安全流程

**工具使用**:
- CI/CD平台
- 容器编排工具
- 监控工具

### 项目经理

**职责**:
- 协调安全活动
- 管理安全资源
- 跟踪安全指标
- 报告安全状态

## 指标和度量

### 安全指标

- **漏洞发现率**: 每个阶段发现的漏洞数量
- **漏洞修复时间**: 从发现到修复的平均时间
- **安全扫描覆盖率**: 扫描覆盖的代码比例
- **门禁通过率**: 通过安全门禁的构建比例

### 度量示例

```json
{
  "period": "2024-01",
  "metrics": {
    "vulnerabilities_found": 150,
    "vulnerabilities_fixed": 120,
    "avg_fix_time_days": 3.5,
    "scan_coverage": 95,
    "gate_pass_rate": 92
  }
}
```

## 持续改进

### 定期审查

- **周度**: 安全事件回顾
- **月度**: 安全指标分析
- **季度**: 流程优化
- **年度**: 策略审查

### 反馈循环

```
发现问题 → 分析原因 → 制定方案 → 实施改进 → 验证效果
```

## 参考资料

- [OWASP DevSecOps Guidelines](https://owasp.org/www-project-devsecops-guideline/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls/)

