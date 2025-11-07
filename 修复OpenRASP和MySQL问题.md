# 修复OpenRASP和MySQL问题

## 问题分析

### 问题1：OpenRASP Agent未加载
从 `ps aux` 输出看，Java进程**没有** `-javaagent` 参数，说明OpenRASP Agent没有被加载。

### 问题2：MySQL端口不匹配
- 应用配置：`jdbc:mysql://localhost:3307/chatbotai_db`
- MySQL容器：运行在 `3306` 端口
- 需要修改应用配置或检查MySQL端口映射

### 问题3：应用ID可能不匹配
- OpenRASP管理后台显示：`zhinengtiyingyong`
- 启动时设置：`bailianyingyong-backend`
- 可能需要使用 `zhinengtiyingyong` 作为应用ID

## 解决方案

### 步骤1：停止当前应用

```bash
# 找到Java进程并停止
pkill -f "spring-boot:run"
# 或
kill 135720 135515
```

### 步骤2：修复MySQL端口配置

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 检查MySQL容器端口映射
docker port rasp-mysql

# 如果MySQL容器映射到3306，修改应用配置
# 编辑 application.properties
nano src/main/resources/application.properties

# 将：
# spring.datasource.url=jdbc:mysql://localhost:3307/chatbotai_db
# 改为：
# spring.datasource.url=jdbc:mysql://localhost:3306/chatbotai_db
```

### 步骤3：检查MySQL容器端口映射

```bash
# 查看MySQL容器详细信息
docker inspect rasp-mysql | grep -A 10 "Ports"

# 如果端口未映射到宿主机，需要：
# 1. 停止容器
docker stop rasp-mysql

# 2. 重新启动并映射端口
docker run -d --name rasp-mysql-new \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=root123 \
  mysql:5.7

# 或者如果已经有数据，使用现有容器但添加端口映射
```

### 步骤4：使用正确的应用ID启动（带OpenRASP）

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 创建启动脚本（使用zhinengtiyingyong作为应用ID）
cat > start-with-rasp.sh << 'EOF'
#!/bin/bash

# OpenRASP配置
export JAVA_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

echo "=== 启动bailianyingyong后端（带OpenRASP）==="
echo "OpenRASP Agent: /home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
echo "应用ID: $RASP_APP_ID"
echo "管理后台: $RASP_BACKEND_URL"
echo "JAVA_OPTS: $JAVA_OPTS"
echo ""

# 验证JAVA_OPTS已设置
if [ -z "$JAVA_OPTS" ]; then
    echo "错误: JAVA_OPTS未设置"
    exit 1
fi

# 启动应用
mvn spring-boot:run
EOF

chmod +x start-with-rasp.sh

# 启动应用
./start-with-rasp.sh
```

### 步骤5：验证OpenRASP已加载

启动后，检查：

```bash
# 检查Java进程是否包含javaagent
ps aux | grep java | grep javaagent

# 应该能看到：
# -javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar
```

## 快速修复命令

```bash
# 1. 停止当前应用
pkill -f "spring-boot:run"

# 2. 检查MySQL端口
docker port rasp-mysql

# 3. 如果MySQL在3306，修改应用配置
cd ~/projects/bailianyingyong/chatbotAi
sed -i 's/localhost:3307/localhost:3306/g' src/main/resources/application.properties

# 4. 使用正确的应用ID和OpenRASP启动
export JAVA_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 5. 启动应用
mvn spring-boot:run
```

## 验证步骤

### 1. 检查OpenRASP Agent是否加载

```bash
# 启动后检查
ps aux | grep java | grep javaagent

# 应该看到 -javaagent 参数
```

### 2. 检查MySQL连接

```bash
# 测试MySQL连接
mysql -h localhost -P 3306 -u root -proot123 -e "SHOW DATABASES;"
```

### 3. 在OpenRASP管理后台验证

1. 访问：`http://192.168.203.141:8086`
2. 登录
3. 在"当前应用"下拉菜单中选择 `zhinengtiyingyong`
4. 查看是否有安全事件

## 如果MySQL端口确实是3307

如果MySQL确实在3307端口，需要：

```bash
# 检查是否有其他MySQL实例
netstat -tlnp | grep 3307

# 或者检查MySQL容器是否映射到3307
docker port rasp-mysql | grep 3307
```

## 完整启动流程

```bash
# 1. 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 2. 修复MySQL端口（如果需要）
cd ~/projects/bailianyingyong/chatbotAi
# 检查配置中的端口
grep "3307\|3306" src/main/resources/application.properties

# 3. 设置OpenRASP环境变量
export JAVA_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 4. 验证环境变量
echo "JAVA_OPTS: $JAVA_OPTS"
echo "RASP_APP_ID: $RASP_APP_ID"

# 5. 启动应用
mvn spring-boot:run
```

