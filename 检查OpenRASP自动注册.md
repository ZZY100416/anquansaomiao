# 检查OpenRASP Agent自动注册

## 问题

OpenRASP管理后台中的 `zhinengtiyingyong` 是手动添加的，说明Agent没有自动注册应用。

## 原因分析

OpenRASP Agent需要：
1. 正确配置 `RASP_APP_ID` 环境变量
2. 正确配置 `RASP_BACKEND_URL` 环境变量
3. Agent能够连接到管理后台
4. 应用ID与管理后台中的配置匹配

## 检查步骤

### 步骤1：检查OpenRASP Agent配置

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 检查OpenRASP配置文件
ls -la /home/enen/openrasp/rasp-2023-03-31/rasp/conf/
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -E "app_id|backend_url|cloud_address"
```

### 步骤2：检查环境变量是否正确传递

```bash
# 查看当前环境变量
echo "RASP_APP_ID: $RASP_APP_ID"
echo "RASP_BACKEND_URL: $RASP_BACKEND_URL"
echo "MAVEN_OPTS: $MAVEN_OPTS"

# 检查Java进程的环境变量
ps aux | grep java | grep javaagent
```

### 步骤3：查看OpenRASP日志

```bash
# OpenRASP日志通常在以下位置
ls -la /home/enen/openrasp/rasp-2023-03-31/rasp/logs/
tail -50 /home/enen/openrasp/rasp-2023-03-31/rasp/logs/rasp.log
```

### 步骤4：检查应用启动日志中的OpenRASP信息

启动应用时，应该能看到OpenRASP的连接信息，例如：
- `[OpenRASP] Connecting to backend: http://192.168.203.141:8086`
- `[OpenRASP] App ID: zhinengtiyingyong`
- `[OpenRASP] Registered successfully`

## 解决方案

### 方案1：通过配置文件设置应用ID（推荐）

OpenRASP Agent可以通过配置文件设置应用ID，而不是环境变量：

```bash
# 编辑OpenRASP配置文件
nano /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml

# 查找并设置：
# cloud.enable: true
# cloud.address: http://192.168.203.141:8086
# cloud.app_id: zhinengtiyingyong
```

### 方案2：通过JVM系统属性设置

在 `MAVEN_OPTS` 中添加系统属性：

```bash
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar \
-Drasp.app_id=zhinengtiyingyong \
-Drasp.cloud.enable=true \
-Drasp.cloud.address=http://192.168.203.141:8086 \
--add-opens java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens java.base/java.lang=ALL-UNNAMED \
--add-opens java.base/java.util=ALL-UNNAMED"
```

### 方案3：检查OpenRASP版本和文档

不同版本的OpenRASP配置方式可能不同：

```bash
# 查看OpenRASP版本
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | head -20

# 查看README或文档
ls -la /home/enen/openrasp/rasp-2023-03-31/rasp/
cat /home/enen/openrasp/rasp-2023-03-31/rasp/README.md 2>/dev/null || echo "README not found"
```

## 完整启动脚本（使用系统属性）

```bash
#!/bin/bash

cd ~/projects/bailianyingyong/chatbotAi

# 1. 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 2. 设置OpenRASP（使用JVM系统属性）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar \
-Drasp.app_id=zhinengtiyingyong \
-Drasp.cloud.enable=true \
-Drasp.cloud.address=http://192.168.203.141:8086 \
--add-opens java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens java.base/java.lang=ALL-UNNAMED \
--add-opens java.base/java.util=ALL-UNNAMED"

# 3. 验证配置
echo "=== 配置检查 ==="
echo "MAVEN_OPTS: $MAVEN_OPTS"
echo ""

# 4. 启动应用
echo "=== 启动应用 ==="
mvn spring-boot:run
```

## 验证步骤

1. **查看启动日志**：
   启动后，查看是否有OpenRASP连接信息：
   ```
   [OpenRASP] Connecting to backend: http://192.168.203.141:8086
   [OpenRASP] App ID: zhinengtiyingyong
   ```

2. **查看OpenRASP日志**：
   ```bash
   tail -f /home/enen/openrasp/rasp-2023-03-31/rasp/logs/rasp.log
   ```

3. **在管理后台检查**：
   - 访问：`http://192.168.203.141:8086`
   - 在"应用管理"中查看是否有新应用自动注册
   - 或者查看 `zhinengtiyingyong` 应用是否有新的连接/心跳

4. **触发一些请求**：
   - 访问应用的API端点
   - 在OpenRASP后台查看是否有安全事件

## 如果仍然无法自动注册

如果使用系统属性后仍然无法自动注册，可能需要：

1. **检查OpenRASP管理后台配置**：
   - 确认管理后台允许自动注册
   - 检查是否有白名单或认证要求

2. **手动配置应用ID**：
   如果自动注册失败，可以：
   - 在管理后台手动添加应用（已经做了）
   - 确保Agent使用的应用ID与后台一致
   - Agent会自动连接到已存在的应用

3. **查看OpenRASP文档**：
   - 访问：https://rasp.baidu.com/doc/install/main.html
   - 查找"应用注册"或"Agent配置"相关章节

