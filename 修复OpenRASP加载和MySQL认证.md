# 修复OpenRASP加载和MySQL认证问题

## 问题分析

### 问题1：OpenRASP Agent未加载
- 日志显示：`[INFO] Attaching agents: []`
- 原因：Maven的`spring-boot:run`不会自动使用`JAVA_OPTS`环境变量
- 解决方案：使用`MAVEN_OPTS`或直接在Maven命令中传递参数

### 问题2：MySQL认证失败
- 错误：`Access denied for user 'root'@'localhost'`
- 原因：MySQL密码可能不正确，或需要检查MySQL容器的配置

## 解决方案

### 步骤1：修复OpenRASP加载问题

Maven的`spring-boot:run`需要使用`MAVEN_OPTS`而不是`JAVA_OPTS`：

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止当前应用
pkill -f "spring-boot:run"

# 使用MAVEN_OPTS（Maven会将其传递给Java进程）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 验证
echo "MAVEN_OPTS: $MAVEN_OPTS"
echo "RASP_APP_ID: $RASP_APP_ID"

# 启动应用
mvn spring-boot:run
```

### 步骤2：修复MySQL认证问题

#### 2.1 检查MySQL容器配置

```bash
# 查看MySQL容器的环境变量
docker inspect rasp-mysql | grep -A 10 "Env"

# 查看MySQL容器的启动命令
docker inspect rasp-mysql | grep -A 5 "Cmd"
```

#### 2.2 测试MySQL连接

```bash
# 尝试连接MySQL（使用配置的密码）
mysql -h localhost -P 3306 -u root -proot123 -e "SHOW DATABASES;" 2>&1

# 如果失败，尝试其他常见密码
mysql -h localhost -P 3306 -u root -p -e "SHOW DATABASES;" 2>&1
# 输入密码时尝试：root123, root, password, 空密码等
```

#### 2.3 重置MySQL密码（如果需要）

```bash
# 进入MySQL容器
docker exec -it rasp-mysql bash

# 在容器内连接MySQL
mysql -u root -p
# 输入当前密码（如果知道）

# 或者重置密码
mysql -u root -p << EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root123';
FLUSH PRIVILEGES;
EOF
```

#### 2.4 检查应用配置的密码

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 查看当前配置的密码
grep "datasource.password" src/main/resources/application.properties

# 如果密码不对，修改它
# 先测试MySQL的实际密码
```

### 步骤3：完整的启动脚本（修复两个问题）

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 1. 修复MySQL密码（如果需要）
# 先测试MySQL连接，找到正确的密码
echo "测试MySQL连接..."
mysql -h localhost -P 3306 -u root -proot123 -e "SELECT 1;" 2>&1 | head -3

# 如果失败，提示用户检查密码
# 2. 设置OpenRASP（使用MAVEN_OPTS）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 3. 启动应用
mvn spring-boot:run
```

## 快速修复命令

### 方案A：使用MAVEN_OPTS（推荐）

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止旧进程
pkill -f "spring-boot:run"

# 设置MAVEN_OPTS（Maven会传递给Java）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 启动
mvn spring-boot:run
```

### 方案B：直接在Maven命令中传递参数

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止旧进程
pkill -f "spring-boot:run"

# 直接在Maven命令中传递Java参数
mvn spring-boot:run \
  -Dspring-boot.run.jvmArguments="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar" \
  -DRASP_APP_ID=zhinengtiyingyong \
  -DRASP_BACKEND_URL=http://192.168.203.141:8086
```

## 修复MySQL认证

### 方法1：检查MySQL容器的实际密码

```bash
# 查看MySQL容器的环境变量
docker inspect rasp-mysql | grep -i "MYSQL_ROOT_PASSWORD\|MYSQL_PASSWORD"

# 或者查看容器的启动日志
docker logs rasp-mysql | grep -i "password\|root"
```

### 方法2：重置MySQL密码

```bash
# 进入MySQL容器
docker exec -it rasp-mysql mysql -u root -p

# 如果不知道密码，尝试重置
docker exec -it rasp-mysql mysql -u root << EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root123';
ALTER USER 'root'@'%' IDENTIFIED BY 'root123';
FLUSH PRIVILEGES;
EOF
```

### 方法3：修改应用配置使用正确的密码

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 如果MySQL的实际密码不是root123，修改配置
# 例如，如果密码是password：
sed -i 's/spring.datasource.password=root123/spring.datasource.password=password/g' src/main/resources/application.properties
```

## 验证步骤

### 1. 验证OpenRASP已加载

启动后检查：

```bash
# 应该能看到 -javaagent 参数
ps aux | grep java | grep javaagent

# 或者查看日志，应该显示：
# [INFO] Attaching agents: [-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar]
```

### 2. 验证MySQL连接

```bash
# 测试MySQL连接
mysql -h localhost -P 3306 -u root -proot123 -e "SHOW DATABASES;"
```

### 3. 在OpenRASP管理后台验证

1. 访问：`http://192.168.203.141:8086`
2. 登录
3. 选择应用：`zhinengtiyingyong`
4. 查看是否有数据

## 完整启动脚本

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 1. 测试并修复MySQL连接
echo "=== 测试MySQL连接 ==="
if mysql -h localhost -P 3306 -u root -proot123 -e "SELECT 1;" 2>/dev/null; then
    echo "✓ MySQL连接成功，密码正确"
else
    echo "✗ MySQL连接失败，请检查密码"
    echo "尝试查看MySQL容器配置..."
    docker inspect rasp-mysql | grep -i "MYSQL_ROOT_PASSWORD"
    echo "如果需要，请重置MySQL密码或修改application.properties中的密码"
fi

# 2. 设置OpenRASP（使用MAVEN_OPTS）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

echo ""
echo "=== OpenRASP配置 ==="
echo "MAVEN_OPTS: $MAVEN_OPTS"
echo "RASP_APP_ID: $RASP_APP_ID"
echo "RASP_BACKEND_URL: $RASP_BACKEND_URL"
echo ""

# 3. 启动应用
echo "=== 启动应用 ==="
mvn spring-boot:run
```

