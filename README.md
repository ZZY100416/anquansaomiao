# 统一安全扫描平台 (Unified Security Scanner Platform)

## 项目简介

统一安全扫描平台是一个集成了多种安全扫描能力的DevSecOps工具，提供代码安全扫描（SAST）、依赖漏洞扫描（SCA）、容器镜像扫描等功能，通过Web界面统一管理和展示扫描结果。

## 功能特性

- **代码安全扫描（SAST）**：使用Semgrep进行静态代码安全分析
- **依赖漏洞扫描（SCA）**：使用OWASP Dependency-Check扫描第三方依赖漏洞
- **容器镜像扫描**：使用Trivy扫描Docker镜像安全漏洞
- **运行时安全扫描（RASP）**：集成OpenRASP实现运行时应用自我保护
- **Web管理界面**：直观的Dashboard展示扫描结果和统计信息
- **报告生成**：支持PDF、HTML格式的安全报告导出
- **项目管理**：支持多项目、多扫描任务管理
- **RASP事件监控**：实时监控和管理运行时安全事件

## 技术栈

- **后端**：Python Flask + SQLAlchemy
- **前端**：React + Ant Design
- **数据库**：PostgreSQL
- **扫描引擎**：Semgrep、OWASP Dependency-Check、Trivy
- **部署**：Docker Compose

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 安装部署

```bash
# 克隆项目
git clone <repository-url>
cd unified-security-scanner

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

访问Web界面：http://localhost:3000

默认管理员账号：
- 用户名：admin
- 密码：admin123

## 项目结构

```
unified-security-scanner/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── scanners/       # 扫描器集成
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/          # 页面
│   │   └── services/       # API服务
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Docker编排配置
├── docs/                   # 文档目录
│   ├── 安装部署手册.md
│   ├── 用户使用手册.md
│   ├── API接口文档.md
│   └── DevSecOps流程文档.md
└── README.md

```

## 开发指南

详见 [开发环境部署指南](docs/开发环境部署指南.md)

## GitHub安全扫描

本项目已配置自动化的SAST和SCA扫描：

- **SAST扫描**: Semgrep, Bandit, CodeQL
- **SCA扫描**: pip-audit, npm audit, OWASP Dependency-Check
- **容器扫描**: Trivy, Hadolint
- **自动依赖更新**: Dependabot

详细配置请查看 [GitHub安全扫描配置指南](docs/GitHub安全扫描配置指南.md)

## 文档

- [安装部署手册](docs/安装部署手册.md)
- [用户使用手册](docs/用户使用手册.md)
- [API接口文档](docs/API接口文档.md)
- [DevSecOps流程文档](docs/DevSecOps流程文档.md)
- [团队分工与Git工作流](docs/团队分工与Git工作流.md)
- [OpenRASP集成指南](docs/OpenRASP集成指南.md)
- [Git工作流程指南](docs/Git工作流程指南.md) - Windows修改同步到Ubuntu

## License

MIT License

