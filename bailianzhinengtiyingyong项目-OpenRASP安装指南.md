# bailianzhinengtiyingyong项目 - OpenRASP安装指南

## 项目结构

根据之前的扫描结果，`bailianzhinengtiyingyong` 项目包含：
- **Node.js部分**：`package.json` 在项目根目录
- **Java部分**：`pom.xml` 在 `chatbotAi/` 子目录

## 安装步骤

### 方案1：如果主要运行的是Java应用（chatbotAi）

#### 1. 下载OpenRASP Java Agent

在Ubuntu服务器上：

```bash
# 进入项目目录
cd ~/projects/bailianzhinengtiyingyong

# 下载OpenRASP Java Agent
cd /opt
sudo wget https://github.com/baidu/openrasp/releases/download/v1.3.0/rasp-java.tar.gz
sudo tar -xzf rasp-java.tar.gz
sudo chown -R $USER:$USER /opt/rasp-java
```

#### 2. 配置Java应用启动参数

**如果使用Maven启动**：

```bash
cd ~/projects/bailianzhinengtiyingyong/chatbotAi

# 方式1：通过环境变量
export JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
export RASP_APP_ID=bailianzhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 启动应用
mvn spring-boot:run
# 或
java $JAVA_OPTS -jar target/chatbotAi-*.jar
```

**如果使用Docker运行**：

修改 `Dockerfile` 或 `docker-compose.yml`：

```dockerfile
# Dockerfile
FROM openjdk:11-jre-slim

# 复制OpenRASP Agent
COPY rasp-java /opt/rasp-java

# 复制应用
COPY chatbotAi/target/*.jar /app/app.jar

# 设置环境变量
ENV JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
ENV RASP_APP_ID=bailianzhinengtiyingyong
ENV RASP_BACKEND_URL=http://192.168.203.141:8086

CMD java $JAVA_OPTS -jar /app/app.jar
```

**如果使用启动脚本**：

创建 `start-with-rasp.sh`：

```bash
#!/bin/bash
cd ~/projects/bailianzhinengtiyingyong/chatbotAi

export JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
export RASP_APP_ID=bailianzhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

java $JAVA_OPTS -jar target/chatbotAi-*.jar
```

### 方案2：如果主要运行的是Node.js应用

#### 1. 安装OpenRASP Node.js插件

```bash
cd ~/projects/bailianzhinengtiyingyong

# 安装OpenRASP Node.js插件
npm install openrasp

# 或使用yarn
yarn add openrasp
```

#### 2. 在应用启动时加载

在应用入口文件（通常是 `app.js`、`server.js` 或 `index.js`）的最开始添加：

```javascript
// 在文件最开头加载OpenRASP
const openrasp = require('openrasp');

// 初始化OpenRASP
openrasp.start({
    app_id: 'bailianzhinengtiyingyong',
    backend_url: 'http://192.168.203.141:8086'
});

// 你的应用代码
const express = require('express');
const app = express();
// ... 其他代码
```

### 方案3：如果同时运行Java和Node.js

需要为**每个运行的应用**分别安装OpenRASP：

1. **Java应用**：按照方案1安装Java Agent
2. **Node.js应用**：按照方案2安装Node.js插件

每个应用使用不同的 `app_id`：
- Java应用：`bailianzhinengtiyingyong-java`
- Node.js应用：`bailianzhinengtiyingyong-nodejs`

## 验证安装

### 1. 启动应用

```bash
# Java应用
cd ~/projects/bailianzhinengtiyingyong/chatbotAi
java $JAVA_OPTS -jar target/chatbotAi-*.jar

# 或Node.js应用
cd ~/projects/bailianzhinengtiyingyong
node app.js
```

### 2. 检查OpenRASP连接

在OpenRASP管理后台（http://192.168.203.141:8086）：
1. 登录管理后台（用户名：`openrasp`，密码：`zzy100416`）
2. 查看"应用列表"或"应用管理"
3. 应该能看到你的应用（`app_id: bailianzhinengtiyingyong`）

### 3. 测试攻击检测（可选）

为了验证OpenRASP是否正常工作，可以模拟一个攻击：

```bash
# SQL注入测试
curl "http://your-app-url/api/users?id=1' OR '1'='1"

# XSS测试
curl "http://your-app-url/search?q=<script>alert('xss')</script>"
```

如果OpenRASP正常工作，这些攻击会被检测并记录到管理后台。

## 在统一安全扫描平台中查看事件

### 1. 确保平台已配置

检查 `docker-compose.yml` 中的配置：

```yaml
backend:
  environment:
    - OPENRASP_API_URL=http://192.168.203.141:8086
    - OPENRASP_USERNAME=openrasp
    - OPENRASP_PASSWORD=zzy100416
```

### 2. 同步事件

1. 登录统一安全扫描平台
2. 进入"RASP事件"页面
3. 点击"同步事件"按钮
4. 在扫描配置中指定 `app_id`：
   ```json
   {
     "app_id": "bailianzhinengtiyingyong"
   }
   ```

## 常见问题

### Q1: 我的应用是Spring Boot，怎么配置？

**A**: Spring Boot应用使用Java Agent方式，在启动时添加参数：

```bash
java -javaagent:/opt/rasp-java/rasp.jar \
     -DRASP_APP_ID=bailianzhinengtiyingyong \
     -DRASP_BACKEND_URL=http://192.168.203.141:8086 \
     -jar target/chatbotAi-*.jar
```

### Q2: 应用在Docker容器中，怎么配置？

**A**: 在Dockerfile中添加OpenRASP Agent：

```dockerfile
FROM openjdk:11-jre-slim

# 复制OpenRASP Agent
COPY rasp-java /opt/rasp-java

# 复制应用
COPY target/*.jar /app/app.jar

# 设置环境变量
ENV JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
ENV RASP_APP_ID=bailianzhinengtiyingyong
ENV RASP_BACKEND_URL=http://192.168.203.141:8086

CMD java $JAVA_OPTS -jar /app/app.jar
```

### Q3: 应用启动后，在OpenRASP管理后台看不到应用？

**A**: 检查以下几点：

1. **网络连接**：应用能否访问OpenRASP管理后台
   ```bash
   curl http://192.168.203.141:8086
   ```

2. **配置正确**：检查环境变量
   ```bash
   echo $RASP_APP_ID
   echo $RASP_BACKEND_URL
   ```

3. **Agent加载**：查看应用日志，搜索"openrasp"或"rasp"
   ```bash
   tail -f logs/application.log | grep -i rasp
   ```

4. **防火墙**：确保端口8086没有被阻止
   ```bash
   telnet 192.168.203.141 8086
   ```

### Q4: 如何确认OpenRASP正在工作？

**A**: 
1. 在OpenRASP管理后台查看"应用列表"，应该能看到你的应用
2. 查看应用日志，应该有OpenRASP相关的启动信息
3. 触发一个测试攻击，看是否被检测并记录

### Q5: 我的项目有多个服务，怎么区分？

**A**: 为每个服务使用不同的 `app_id`：

- 主服务：`bailianzhinengtiyingyong-main`
- 聊天服务：`bailianzhinengtiyingyong-chatbot`
- API服务：`bailianzhinengtiyingyong-api`

在统一安全扫描平台中，可以通过 `app_id` 筛选不同服务的事件。

## 快速开始命令

### Java应用（Spring Boot）

```bash
# 1. 下载OpenRASP
cd /opt
sudo wget https://github.com/baidu/openrasp/releases/download/v1.3.0/rasp-java.tar.gz
sudo tar -xzf rasp-java.tar.gz
sudo chown -R $USER:$USER /opt/rasp-java

# 2. 进入项目目录
cd ~/projects/bailianzhinengtiyingyong/chatbotAi

# 3. 设置环境变量
export JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
export RASP_APP_ID=bailianzhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 4. 启动应用
mvn spring-boot:run
# 或
java $JAVA_OPTS -jar target/chatbotAi-*.jar
```

### Node.js应用

```bash
# 1. 进入项目目录
cd ~/projects/bailianzhinengtiyingyong

# 2. 安装OpenRASP
npm install openrasp

# 3. 在app.js或server.js开头添加：
# const openrasp = require('openrasp');
# openrasp.start({
#     app_id: 'bailianzhinengtiyingyong',
#     backend_url: 'http://192.168.203.141:8086'
# });

# 4. 启动应用
node app.js
# 或
npm start
```

## 下一步

安装完成后：
1. ✅ 启动应用
2. ✅ 在OpenRASP管理后台确认应用已连接
3. ✅ 在统一安全扫描平台中同步事件
4. ✅ 查看和处理安全事件

