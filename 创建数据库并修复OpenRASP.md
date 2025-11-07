# 创建数据库并修复OpenRASP

## 问题1：数据库不存在

错误：`Unknown database 'chatbotai_db'`

### 解决步骤

```bash
# 1. 获取MySQL容器IP（如果还没获取）
MYSQL_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' rasp-mysql)
echo "MySQL容器IP: $MYSQL_IP"

# 2. 创建数据库
docker exec -i rasp-mysql mysql -u root -p123456 << 'EOF'
CREATE DATABASE IF NOT EXISTS chatbotai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES LIKE 'chatbotai_db';
EOF

# 3. 验证数据库已创建
docker exec -i rasp-mysql mysql -u root -p123456 -e "SHOW DATABASES;" | grep chatbotai_db
```

## 问题2：OpenRASP与Java 17不兼容

错误：`module java.base does not "opens jdk.internal.loader" to unnamed module`

### 原因
OpenRASP的旧版本不支持Java 17+的模块系统。

### 解决方案

#### 方案1：添加JVM参数（推荐）

在启动时添加 `--add-opens` 参数来开放必要的模块：

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 设置OpenRASP（添加Java 17兼容参数）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar --add-opens java.base/jdk.internal.loader=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/java.util=ALL-UNNAMED"
export RASP_APP_ID=bailianzhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 启动
mvn spring-boot:run
```

#### 方案2：修改pom.xml（永久解决）

如果方案1不行，可以在`pom.xml`的`spring-boot-maven-plugin`中添加JVM参数：

```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <jvmArguments>
            -javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar
            --add-opens java.base/jdk.internal.loader=ALL-UNNAMED
            --add-opens java.base/java.lang=ALL-UNNAMED
            --add-opens java.base/java.util=ALL-UNNAMED
        </jvmArguments>
    </configuration>
</plugin>
```

#### 方案3：升级OpenRASP（如果可用）

检查是否有支持Java 17的OpenRASP版本：
- 访问：https://rasp.baidu.com/doc/install/main.html
- 查看最新版本是否支持Java 17

## 完整启动脚本

```bash
#!/bin/bash

cd ~/projects/bailianyingyong/chatbotAi

# 1. 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 2. 创建数据库（如果不存在）
MYSQL_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' rasp-mysql)
echo "=== 创建数据库 ==="
docker exec -i rasp-mysql mysql -u root -p123456 << EOF
CREATE DATABASE IF NOT EXISTS chatbotai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES LIKE 'chatbotai_db';
EOF

# 3. 设置OpenRASP（Java 17兼容）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar --add-opens java.base/jdk.internal.loader=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/java.util=ALL-UNNAMED"
export RASP_APP_ID=bailianzhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 4. 验证配置
echo "=== 配置检查 ==="
echo "MAVEN_OPTS: $MAVEN_OPTS"
echo "RASP_APP_ID: $RASP_APP_ID"
echo "MySQL URL: $(grep 'datasource.url' src/main/resources/application.properties | cut -d'=' -f2)"
echo ""

# 5. 启动应用
echo "=== 启动应用 ==="
mvn spring-boot:run
```

## 验证步骤

启动后检查：

1. **数据库连接成功**：不再出现 `Unknown database` 错误
2. **OpenRASP加载成功**：日志中应该显示 `[OpenRASP] Initialized successfully` 或类似信息，而不是 `Failed to initialize`
3. **应用启动成功**：`Tomcat started on port 9988`
4. **在OpenRASP管理后台验证**：
   - 访问：`http://192.168.203.141:8086`
   - 登录后，在"当前应用"下拉菜单中选择 `bailianzhinengtiyingyong`
   - 应该能看到应用状态和数据

## 如果OpenRASP仍然失败

如果添加了`--add-opens`参数后OpenRASP仍然失败，可以：

1. **暂时禁用OpenRASP**：先让应用正常运行，后续再处理OpenRASP
2. **降级Java版本**：使用Java 11或Java 8（如果项目支持）
3. **联系OpenRASP支持**：查看是否有Java 17兼容版本

