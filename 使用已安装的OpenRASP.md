# 使用已安装的OpenRASP

## 找到的OpenRASP路径

- **rasp.jar路径**：`/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar`
- **OpenRASP目录**：`/home/enen/openrasp`
- **管理后台**：已运行，端口 `8086`
- **MySQL数据库**：`rasp-mysql` 容器运行中

## 使用OpenRASP启动应用

### 方式1：使用环境变量启动（推荐）

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 设置OpenRASP环境变量
export JAVA_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=bailianyingyong-backend
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 启动应用
mvn spring-boot:run
```

### 方式2：创建启动脚本（方便重复使用）

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 创建启动脚本
cat > start-with-rasp.sh << 'EOF'
#!/bin/bash

# OpenRASP配置
export JAVA_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=bailianyingyong-backend
export RASP_BACKEND_URL=http://192.168.203.141:8086

echo "=== 启动bailianyingyong后端（带OpenRASP）==="
echo "OpenRASP Agent: /home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
echo "应用ID: $RASP_APP_ID"
echo "管理后台: $RASP_BACKEND_URL"
echo ""

# 启动应用
mvn spring-boot:run
EOF

chmod +x start-with-rasp.sh

# 使用脚本启动
./start-with-rasp.sh
```

### 方式3：如果使用jar包启动

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 先打包
mvn clean package -DskipTests

# 创建jar启动脚本
cat > start-jar-with-rasp.sh << 'EOF'
#!/bin/bash

# OpenRASP配置
export JAVA_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=bailianyingyong-backend
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 找到jar包
JAR_FILE=$(find target -name "*.jar" -not -name "*sources.jar" | head -1)

if [ -z "$JAR_FILE" ]; then
    echo "错误: 找不到jar包，请先运行 mvn clean package"
    exit 1
fi

echo "=== 启动bailianyingyong后端（带OpenRASP）==="
echo "JAR文件: $JAR_FILE"
echo "OpenRASP Agent: /home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
echo "应用ID: $RASP_APP_ID"
echo "管理后台: $RASP_BACKEND_URL"
echo ""

# 启动应用
java $JAVA_OPTS -jar $JAR_FILE
EOF

chmod +x start-jar-with-rasp.sh

# 使用脚本启动
./start-jar-with-rasp.sh
```

## 验证OpenRASP连接

### 1. 检查应用是否启动

```bash
# 查看应用日志，应该能看到OpenRASP相关的信息
# 或者检查应用端口（通常是8080或8081）
netstat -tlnp | grep -E ':(8080|8081)'
```

### 2. 在OpenRASP管理后台查看

1. 访问OpenRASP管理后台：`http://192.168.203.141:8086`
2. 登录（用户名：`openrasp`，密码：`zzy100416`）
3. 查看"应用列表"或"应用管理"
4. 应该能看到应用：`bailianyingyong-backend`

### 3. 测试攻击检测（可选）

为了验证OpenRASP是否正常工作，可以模拟一个攻击：

```bash
# 假设应用运行在8080端口
curl "http://localhost:8080/api/users?id=1' OR '1'='1"
```

如果OpenRASP正常工作，这个SQL注入攻击会被检测并记录到管理后台。

## 检查OpenRASP管理后台状态

```bash
# 检查管理后台是否运行
ps aux | grep rasp-cloud

# 检查端口8086
netstat -tlnp | grep 8086

# 测试管理后台连接
curl http://192.168.203.141:8086
```

## 常见问题

### Q1: 应用启动后，在OpenRASP管理后台看不到应用？

**A**: 检查以下几点：

1. **应用是否已启动**：
   ```bash
   ps aux | grep java | grep bailianyingyong
   ```

2. **OpenRASP Agent是否加载**：
   查看应用启动日志，应该能看到OpenRASP相关的信息

3. **网络连接**：
   ```bash
   # 从应用服务器测试管理后台连接
   curl http://192.168.203.141:8086
   ```

4. **环境变量是否正确**：
   ```bash
   echo $JAVA_OPTS
   echo $RASP_APP_ID
   echo $RASP_BACKEND_URL
   ```

### Q2: 如何确认OpenRASP正在工作？

**A**: 
1. 查看应用日志，应该有OpenRASP相关的启动信息
2. 在OpenRASP管理后台查看"应用列表"
3. 触发一个测试攻击，看是否被检测

### Q3: 如何停止应用？

**A**: 
```bash
# 查找Java进程
ps aux | grep java | grep bailianyingyong

# 停止进程
kill <PID>

# 或使用pkill
pkill -f "spring-boot:run"
```

## 完整启动流程

```bash
# 1. 进入项目目录
cd ~/projects/bailianyingyong/chatbotAi

# 2. 确保Java版本正确（如果需要Java 17）
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 3. 设置OpenRASP环境变量
export JAVA_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=bailianyingyong-backend
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 4. 启动应用
mvn spring-boot:run

# 5. 在另一个终端验证
# - 访问OpenRASP管理后台：http://192.168.203.141:8086
# - 查看应用列表，应该能看到 bailianyingyong-backend
```

## 下一步

1. ✅ OpenRASP路径已找到
2. ✅ 管理后台已运行
3. ⏳ 解决Java版本问题（如果需要）
4. ⏳ 启动应用（带OpenRASP）
5. ⏳ 在管理后台验证应用连接
6. ⏳ 在统一安全扫描平台中同步事件

