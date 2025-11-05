# OpenRASP集成指南

## 目录

1. [概述](#概述)
2. [OpenRASP简介](#openrasp简介)
3. [集成准备](#集成准备)
4. [配置说明](#配置说明)
5. [使用方法](#使用方法)
6. [API接口](#api接口)
7. [常见问题](#常见问题)

## 概述

统一安全扫描平台已集成OpenRASP（运行时应用自我保护）功能，可以实时监控应用程序运行时的安全事件，并提供统一的管理界面。

### 功能特性

- **实时监控**: 从OpenRASP管理后台获取运行时安全事件
- **事件管理**: 查看、筛选、处理安全事件
- **状态监控**: 监控OpenRASP服务连接状态
- **事件同步**: 手动或自动同步RASP事件到平台

## OpenRASP简介

OpenRASP是百度开源的应用运行时自我保护（Runtime Application Self-Protection）解决方案。

### 主要功能

- **实时防护**: 在应用运行时检测和阻止攻击
- **漏洞检测**: 检测SQL注入、XSS、命令注入等常见漏洞
- **零侵入**: 无需修改应用代码
- **多语言支持**: 支持Java、PHP、Python等

### 官方网站

- GitHub: https://github.com/baidu/openrasp
- 文档: https://rasp.baidu.com/

## 集成准备

### 1. 安装OpenRASP

#### Java应用

```bash
# 下载OpenRASP Java Agent
wget https://github.com/baidu/openrasp/releases/download/v1.3.0/rasp-java.tar.gz
tar -xzf rasp-java.tar.gz

# 配置Java应用启动参数
export JAVA_OPTS="$JAVA_OPTS -javaagent:/path/to/rasp/rasp.jar"
```

#### PHP应用

```bash
# 安装OpenRASP PHP扩展
pecl install openrasp

# 或下载预编译版本
wget https://github.com/baidu/openrasp/releases/download/v1.3.0/rasp-php.tar.gz
tar -xzf rasp-php.tar.gz
```

#### Python应用

```bash
# 安装OpenRASP Python插件
pip install openrasp

# 在应用启动时加载
import openrasp
openrasp.start()
```

### 2. 启动OpenRASP管理后台

OpenRASP管理后台用于收集和管理安全事件。

```bash
# 使用Docker启动管理后台
docker run -d \
  --name openrasp-cloud \
  -p 8086:8086 \
  -p 11111:11111 \
  baidu/openrasp-cloud
```

### 3. 配置应用连接到管理后台

在应用配置中设置OpenRASP管理后台地址：

```properties
# Java应用配置
rasp.cloud.backend_url=http://localhost:11111

# PHP应用配置
openrasp.cloud_backend_url=http://localhost:11111

# Python应用配置
OPENRASP_BACKEND_URL=http://localhost:11111
```

## 配置说明

### 环境变量配置

在统一安全扫描平台中配置OpenRASP连接信息：

```bash
# 后端环境变量 (.env文件)
OPENRASP_API_URL=http://localhost:11111/api
OPENRASP_API_KEY=your-api-key-here
```

### Docker Compose配置

如果需要将OpenRASP管理后台集成到docker-compose中：

```yaml
# docker-compose.yml
services:
  openrasp-cloud:
    image: baidu/openrasp-cloud:latest
    container_name: openrasp-cloud
    ports:
      - "8086:8086"  # Web管理界面
      - "11111:11111"  # API接口
    volumes:
      - openrasp_data:/var/lib/openrasp
    networks:
      - scanner-network
    environment:
      - MYSQL_HOST=postgres
      - MYSQL_PORT=5432
      - MYSQL_DB=openrasp
      - MYSQL_USER=openrasp
      - MYSQL_PASS=openrasp123

volumes:
  openrasp_data:
```

### 应用配置示例

#### Java应用

```java
// application.properties
rasp.cloud.backend_url=http://openrasp-cloud:11111
rasp.cloud.app_id=my-java-app
rasp.cloud.app_secret=my-secret-key
```

#### PHP应用

```php
// php.ini
openrasp.cloud_backend_url=http://openrasp-cloud:11111
openrasp.app_id=my-php-app
openrasp.app_secret=my-secret-key
```

#### Python应用

```python
# 环境变量或配置文件中
OPENRASP_BACKEND_URL=http://openrasp-cloud:11111
OPENRASP_APP_ID=my-python-app
OPENRASP_APP_SECRET=my-secret-key
```

## 使用方法

### 1. 在Web界面中查看RASP事件

1. 登录统一安全扫描平台
2. 点击左侧菜单 "RASP事件"
3. 查看实时安全事件列表

### 2. 创建RASP扫描任务

1. 点击 "扫描任务" → "新建扫描"
2. 选择扫描类型: **RASP - 运行时安全扫描**
3. 配置扫描参数:
   ```json
   {
     "app_id": "my-app-id",
     "start_time": "2024-01-01T00:00:00",
     "end_time": "2024-01-01T23:59:59"
   }
   ```
4. 点击 "确定" 启动扫描

### 3. 同步RASP事件

在RASP事件页面：

1. 点击 "同步事件" 按钮
2. 选择要同步的应用ID（可选）
3. 等待同步完成
4. 查看同步的事件列表

### 4. 处理安全事件

1. 在事件列表中点击 "详情" 查看详细信息
2. 分析事件类型和攻击参数
3. 点击 "标记已处理" 标记事件为已处理
4. 根据事件信息采取相应的安全措施

## API接口

### 获取RASP状态

**GET** `/api/rasp/status`

获取OpenRASP服务连接状态。

**响应**:
```json
{
  "status": "connected",
  "data": {
    "version": "1.3.0",
    "uptime": 3600
  }
}
```

### 获取RASP事件列表

**GET** `/api/rasp/events`

获取RASP事件列表。

**查询参数**:
- `app_id` (可选): 应用ID
- `severity` (可选): 严重级别 (critical, high, medium, low, info)
- `handled` (可选): 是否已处理 (true/false)
- `start_time` (可选): 开始时间 (ISO格式)
- `end_time` (可选): 结束时间 (ISO格式)
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，默认20

**响应**:
```json
{
  "events": [
    {
      "id": 1,
      "app_id": "my-app",
      "event_id": "event-123",
      "attack_type": "SQL Injection",
      "severity": "high",
      "message": "检测到SQL注入攻击",
      "url": "/api/users",
      "client_ip": "192.168.1.100",
      "event_time": "2024-01-01T10:00:00",
      "handled": false
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

### 获取RASP事件详情

**GET** `/api/rasp/events/{event_id}`

获取指定事件的详细信息。

### 标记事件为已处理

**POST** `/api/rasp/events/{event_id}/handle`

标记RASP事件为已处理。

### 同步RASP事件

**POST** `/api/rasp/events/sync`

从OpenRASP管理后台同步事件到平台。

**请求体**:
```json
{
  "app_id": "my-app-id",
  "start_time": "2024-01-01T00:00:00",
  "end_time": "2024-01-01T23:59:59"
}
```

## 常见问题

### Q1: 无法连接到OpenRASP管理后台？

**A**: 检查以下几点：

1. **网络连接**: 确保应用可以访问OpenRASP管理后台地址
2. **端口开放**: 确保11111端口未被防火墙阻止
3. **配置正确**: 检查OPENRASP_API_URL配置是否正确
4. **服务运行**: 确认OpenRASP管理后台服务正在运行

```bash
# 测试连接
curl http://localhost:11111/api/status

# 检查服务状态
docker ps | grep openrasp
```

### Q2: 没有收到RASP事件？

**A**: 可能的原因：

1. **应用未正确配置**: 检查应用中的OpenRASP配置
2. **Agent未加载**: 确认OpenRASP Agent已正确加载
3. **无攻击事件**: 如果没有攻击，自然不会产生事件
4. **事件被过滤**: 检查OpenRASP的过滤规则

### Q3: 如何测试RASP功能？

**A**: 可以手动触发攻击测试：

```bash
# SQL注入测试
curl "http://your-app/api/users?id=1' OR '1'='1"

# XSS测试
curl "http://your-app/api/search?q=<script>alert('xss')</script>"

# 命令注入测试
curl "http://your-app/api/exec?cmd=ls;rm -rf /"
```

### Q4: RASP事件太多怎么办？

**A**: 可以：

1. **设置过滤规则**: 在OpenRASP中配置过滤规则
2. **调整严重级别**: 只关注高危和严重事件
3. **批量处理**: 使用批量处理功能标记事件
4. **自动化处理**: 配置自动处理规则

### Q5: 如何与现有OpenRASP环境集成？

**A**: 

1. **获取API密钥**: 从OpenRASP管理后台获取API密钥
2. **配置环境变量**: 设置OPENRASP_API_URL和OPENRASP_API_KEY
3. **测试连接**: 使用状态检查接口测试连接
4. **同步事件**: 手动或自动同步现有事件

### Q6: RASP会影响应用性能吗？

**A**: OpenRASP设计为轻量级，对性能影响很小：

- **延迟**: 通常增加1-5ms延迟
- **资源**: 内存占用约10-50MB
- **CPU**: CPU占用通常<1%

如果性能影响较大，可以：
- 调整检测规则
- 降低日志级别
- 优化过滤规则

## 最佳实践

### 1. 监控关键应用

优先在以下应用部署OpenRASP：
- 面向互联网的应用
- 处理敏感数据的应用
- 历史上有安全问题的应用

### 2. 定期审查事件

- 每天检查未处理的高危事件
- 每周审查所有事件趋势
- 每月生成安全报告

### 3. 建立响应流程

1. **检测**: RASP检测到攻击
2. **告警**: 平台发送告警通知
3. **分析**: 安全团队分析事件
4. **响应**: 采取相应安全措施
5. **修复**: 修复漏洞或加强防护

### 4. 持续优化

- 根据实际攻击调整检测规则
- 减少误报率
- 提高检测准确性

## 参考资料

- [OpenRASP官方文档](https://rasp.baidu.com/doc/)
- [OpenRASP GitHub](https://github.com/baidu/openrasp)
- [RASP技术白皮书](https://rasp.baidu.com/doc/)

## 技术支持

如有问题，请：

1. 查看本文档的常见问题部分
2. 查看OpenRASP官方文档
3. 提交GitHub Issue
4. 联系技术支持团队

