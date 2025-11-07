# OpenRASP使用指南 - 如何扫描项目

## 重要说明

**OpenRASP不是静态扫描工具**，它是**运行时应用自我保护（Runtime Application Self-Protection）**系统。

### OpenRASP vs 静态扫描

| 特性 | OpenRASP (RASP) | SAST/SCA (静态扫描) |
|------|----------------|-------------------|
| **扫描时机** | 应用运行时 | 代码提交/构建时 |
| **扫描方式** | 监控运行时行为 | 分析源代码/依赖 |
| **检测内容** | 实际攻击行为 | 潜在漏洞 |
| **集成方式** | 在应用中安装Agent | 上传代码文件 |

## 工作流程

```
1. 在你的应用中安装OpenRASP Agent
   ↓
2. 启动应用（OpenRASP自动监控）
   ↓
3. 应用运行时，OpenRASP检测攻击并记录事件
   ↓
4. 事件发送到OpenRASP管理后台（http://192.168.203.141:8086）
   ↓
5. 统一安全扫描平台从管理后台获取事件
   ↓
6. 在平台中查看和处理安全事件
```

## 第一步：在项目中安装OpenRASP Agent

### Java项目

#### 1. 下载OpenRASP Java Agent

```bash
# 在Ubuntu上
cd /opt
wget https://github.com/baidu/openrasp/releases/download/v1.3.0/rasp-java.tar.gz
tar -xzf rasp-java.tar.gz
cd rasp-java
```

#### 2. 配置应用启动参数

**方式1：通过环境变量（推荐）**

```bash
export JAVA_OPTS="$JAVA_OPTS -javaagent:/opt/rasp-java/rasp.jar"
export RASP_APP_ID=my-java-app  # 应用ID，用于在管理后台识别
export RASP_BACKEND_URL=http://192.168.203.141:8086  # OpenRASP管理后台地址

# 启动你的Java应用
java $JAVA_OPTS -jar your-app.jar
```

**方式2：在启动脚本中**

```bash
#!/bin/bash
java -javaagent:/opt/rasp-java/rasp.jar \
     -DRASP_APP_ID=my-java-app \
     -DRASP_BACKEND_URL=http://192.168.203.141:8086 \
     -jar your-app.jar
```

**方式3：在Docker中**

```dockerfile
# Dockerfile
FROM openjdk:11-jre-slim

# 复制OpenRASP Agent
COPY rasp-java /opt/rasp-java

# 设置启动参数
ENV JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
ENV RASP_APP_ID=my-java-app
ENV RASP_BACKEND_URL=http://192.168.203.141:8086

CMD java $JAVA_OPTS -jar app.jar
```

### Python项目

#### 1. 安装OpenRASP Python插件

```bash
pip install openrasp
```

#### 2. 在应用启动时加载

```python
# app.py 或 main.py
import openrasp

# 在应用启动时初始化
openrasp.start(
    app_id='my-python-app',
    backend_url='http://192.168.203.141:8086'
)

# 你的应用代码
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
```

### PHP项目

#### 1. 安装OpenRASP PHP扩展

```bash
# 下载PHP扩展
wget https://github.com/baidu/openrasp/releases/download/v1.3.0/rasp-php.tar.gz
tar -xzf rasp-php.tar.gz

# 安装扩展
cd rasp-php
phpize
./configure
make && make install

# 在php.ini中添加
echo "extension=openrasp.so" >> /etc/php/7.4/fpm/php.ini
```

#### 2. 配置应用ID

在应用根目录创建 `rasp.ini`：

```ini
[openrasp]
app_id = my-php-app
backend_url = http://192.168.203.141:8086
```

## 第二步：启动应用并测试

### 1. 启动你的应用

```bash
# Java应用
java $JAVA_OPTS -jar your-app.jar

# Python应用
python app.py

# PHP应用
php-fpm 或通过Web服务器（Nginx/Apache）
```

### 2. 检查OpenRASP连接

在OpenRASP管理后台（http://192.168.203.141:8086）：
- 登录管理后台
- 查看"应用列表"，应该能看到你的应用（app_id）
- 如果看不到，检查：
  - 应用是否已启动
  - RASP_APP_ID是否正确配置
  - RASP_BACKEND_URL是否正确
  - 网络是否连通

### 3. 触发测试攻击（可选）

为了测试OpenRASP是否正常工作，可以模拟一个攻击：

```bash
# SQL注入测试
curl "http://your-app-url/api/users?id=1' OR '1'='1"

# XSS测试
curl "http://your-app-url/search?q=<script>alert('xss')</script>"
```

如果OpenRASP正常工作，这些攻击会被检测并记录到管理后台。

## 第三步：在统一安全扫描平台中查看事件

### 1. 配置平台连接OpenRASP

确保 `docker-compose.yml` 中已配置：

```yaml
backend:
  environment:
    - OPENRASP_API_URL=http://192.168.203.141:8086
    - OPENRASP_USERNAME=openrasp
    - OPENRASP_PASSWORD=zzy100416
```

### 2. 访问RASP事件页面

1. 登录统一安全扫描平台
2. 点击左侧菜单 "RASP事件"
3. 查看OpenRASP连接状态（应该显示"已连接"）
4. 点击"同步事件"按钮，从OpenRASP管理后台同步事件

### 3. 创建RASP扫描任务（可选）

如果你想通过扫描任务的方式获取事件：

1. 进入"扫描任务"页面
2. 点击"新建扫描"
3. 选择扫描类型：**RASP - 运行时安全扫描**
4. 配置扫描参数（JSON格式）：
   ```json
   {
     "app_id": "my-java-app",
     "start_time": "2024-01-01T00:00:00",
     "end_time": "2024-12-31T23:59:59"
   }
   ```
   - `app_id`: 你的应用ID（在安装OpenRASP时配置的）
   - `start_time`: 开始时间（可选，默认最近30天）
   - `end_time`: 结束时间（可选，默认当前时间）

5. 点击"开始扫描"

## 常见问题

### Q1: 我的应用是Spring Boot，怎么集成？

**A**: Spring Boot应用使用Java Agent方式：

```bash
# 启动命令
java -javaagent:/opt/rasp-java/rasp.jar \
     -DRASP_APP_ID=spring-boot-app \
     -DRASP_BACKEND_URL=http://192.168.203.141:8086 \
     -jar spring-boot-app.jar
```

### Q2: 我的应用在Docker容器中，怎么集成？

**A**: 在Dockerfile中添加OpenRASP Agent：

```dockerfile
FROM openjdk:11-jre-slim

# 复制OpenRASP Agent
COPY rasp-java /opt/rasp-java

# 设置环境变量
ENV JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
ENV RASP_APP_ID=my-docker-app
ENV RASP_BACKEND_URL=http://192.168.203.141:8086

# 你的应用
COPY app.jar /app/app.jar
CMD java $JAVA_OPTS -jar /app/app.jar
```

### Q3: 应用启动后，在OpenRASP管理后台看不到应用？

**A**: 检查以下几点：
1. **网络连接**：应用能否访问OpenRASP管理后台（`http://192.168.203.141:8086`）
   ```bash
   curl http://192.168.203.141:8086
   ```
2. **配置正确**：检查 `RASP_APP_ID` 和 `RASP_BACKEND_URL` 是否正确
3. **Agent加载**：检查应用日志，看是否有OpenRASP相关错误
4. **防火墙**：确保端口8086没有被防火墙阻止

### Q4: 如何查看应用是否成功连接OpenRASP？

**A**: 
1. 在OpenRASP管理后台查看"应用列表"
2. 查看应用日志，搜索"openrasp"或"rasp"
3. 在应用中触发一个测试攻击，看是否被检测

### Q5: OpenRASP会影响应用性能吗？

**A**: OpenRASP设计为轻量级，对性能影响很小：
- **延迟**：通常增加1-5ms
- **内存**：约10-50MB
- **CPU**：通常<1%

如果性能影响较大，可以调整检测规则或降低日志级别。

### Q6: 我可以扫描多个项目吗？

**A**: 可以！每个项目使用不同的 `app_id`：

```bash
# 项目1
export RASP_APP_ID=project-1
java -javaagent:/opt/rasp-java/rasp.jar -jar project1.jar

# 项目2
export RASP_APP_ID=project-2
java -javaagent:/opt/rasp-java/rasp.jar -jar project2.jar
```

在统一安全扫描平台中，可以通过 `app_id` 筛选不同项目的事件。

## 总结

1. **安装OpenRASP Agent**到你的应用中
2. **配置应用ID**和OpenRASP管理后台地址
3. **启动应用**，OpenRASP自动开始监控
4. **在统一安全扫描平台**中查看和处理安全事件

**重要**：OpenRASP是运行时保护，不是静态扫描。应用必须运行，OpenRASP才能检测攻击并记录事件。

