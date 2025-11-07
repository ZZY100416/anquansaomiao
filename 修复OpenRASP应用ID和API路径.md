# 修复OpenRASP应用ID和API路径问题

## 问题分析

1. **OpenRASP应用ID不匹配**：
   - 后台显示的应用名：`zhinengtiyingyong`
   - 启动时设置的 `RASP_APP_ID`：`bailianzhinengtiyingyong`
   - **需要修改为**：`zhinengtiyingyong`

2. **404错误**：
   - 应用在运行，但根路径 `/` 没有路由
   - 需要找到实际的API路径

## 解决方案

### 步骤1：修改OpenRASP应用ID

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止应用
pkill -f "spring-boot:run"
sleep 2

# 修改RASP_APP_ID为后台显示的名称
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar --add-opens java.base/jdk.internal.loader=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/java.util=ALL-UNNAMED"
export RASP_APP_ID=zhinengtiyingyong  # 改为后台显示的名称
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 重新启动
mvn spring-boot:run
```

### 步骤2：查找Spring Boot应用的API路径

Spring Boot应用通常有以下路径：

1. **健康检查**：
   ```bash
   # 在Ubuntu上测试
   curl http://localhost:9988/actuator/health
   curl http://localhost:9988/health
   ```

2. **查看应用日志**：
   启动日志中通常会显示映射的路径，例如：
   ```
   Mapped "{[/api/chat],methods=[POST]}" onto ...
   ```

3. **查看源代码**：
   ```bash
   cd ~/projects/bailianyingyong/chatbotAi
   # 查找控制器
   find src -name "*Controller.java" -o -name "*Controller.kt"
   grep -r "@RequestMapping\|@GetMapping\|@PostMapping" src/
   ```

4. **常见路径**：
   - `/api/chat` - 聊天接口
   - `/api/message` - 消息接口
   - `/api/history` - 历史记录
   - `/actuator/health` - Spring Boot Actuator健康检查

### 步骤3：测试应用API

```bash
# 在Ubuntu上测试本地连接
curl http://localhost:9988/actuator/health
curl http://localhost:9988/api/chat
curl http://localhost:9988/api/message

# 从Windows访问（需要确保防火墙允许）
# 在Windows浏览器中访问：
# http://192.168.203.141:9988/actuator/health
# http://192.168.203.141:9988/api/chat
```

### 步骤4：检查防火墙和端口映射

如果从Windows无法访问Ubuntu的9988端口：

```bash
# 在Ubuntu上检查端口监听
sudo netstat -tlnp | grep 9988
# 或
sudo ss -tlnp | grep 9988

# 检查防火墙
sudo ufw status
# 如果需要开放端口
sudo ufw allow 9988/tcp

# 检查应用是否绑定到0.0.0.0（允许外部访问）
# 在application.properties中应该配置：
# server.address=0.0.0.0
# 或
# server.address=
```

## 完整启动脚本（修正版）

```bash
#!/bin/bash

cd ~/projects/bailianyingyong/chatbotAi

# 1. 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 2. 设置OpenRASP（使用正确的应用ID）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar --add-opens java.base/jdk.internal.loader=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/java.util=ALL-UNNAMED"
export RASP_APP_ID=zhinengtiyingyong  # 使用后台显示的名称
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 3. 验证配置
echo "=== 配置检查 ==="
echo "MAVEN_OPTS: $MAVEN_OPTS"
echo "RASP_APP_ID: $RASP_APP_ID"
echo "RASP_BACKEND_URL: $RASP_BACKEND_URL"
echo ""

# 4. 启动应用
echo "=== 启动应用 ==="
mvn spring-boot:run
```

## 验证步骤

1. **检查OpenRASP后台**：
   - 访问：`http://192.168.203.141:8086`
   - 在"当前应用"下拉菜单中选择 `zhinengtiyingyong`
   - 查看是否有新的安全事件

2. **测试应用API**：
   ```bash
   # 在Ubuntu上
   curl http://localhost:9988/actuator/health
   
   # 从Windows浏览器
   # http://192.168.203.141:9988/actuator/health
   ```

3. **触发一些请求**：
   - 访问应用的API端点
   - 在OpenRASP后台查看是否有安全事件记录

## 如果仍然404

如果所有路径都返回404，可能需要：

1. **检查应用配置**：
   ```bash
   # 查看application.properties
   cat src/main/resources/application.properties | grep -E "server|context|path"
   ```

2. **查看启动日志**：
   启动时查看是否有路径映射信息

3. **添加测试端点**：
   如果应用没有配置任何路由，可以添加一个简单的测试端点

