# 修复MySQL认证问题（错误1698）

## 问题分析

从诊断结果看：
- ✅ 容器内连接成功（密码123456正确）
- ❌ 宿主机连接失败：`ERROR 1698 (28000): Access denied for user 'root'@'localhost'`
- 错误1698通常表示MySQL 8.0的认证插件问题（auth_socket vs caching_sha2_password）

## 解决方案

### 方案1：修改root用户认证方式（推荐）

```bash
# 进入MySQL容器
docker exec -it rasp-mysql mysql -u root -p123456 << EOF

# 查看当前root用户的认证插件
SELECT user, host, plugin FROM mysql.user WHERE user='root';

# 修改root@'localhost'的认证方式
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';

# 创建或修改root@'%'（允许外部连接）
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '123456';
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

# 刷新权限
FLUSH PRIVILEGES;

# 验证
SELECT user, host, plugin FROM mysql.user WHERE user='root';

EOF
```

### 方案2：使用127.0.0.1而不是localhost

有时`localhost`和`127.0.0.1`在MySQL中有不同的认证方式：

```bash
# 测试使用127.0.0.1
mysql -h 127.0.0.1 -P 3306 -u root -p123456 -e "SELECT 1;"

# 如果成功，修改应用配置
cd ~/projects/bailianyingyong/chatbotAi
sed -i 's|jdbc:mysql://localhost:3306|jdbc:mysql://127.0.0.1:3306|g' src/main/resources/application.properties
```

### 方案3：创建新用户（如果root无法修复）

```bash
docker exec -it rasp-mysql mysql -u root -p123456 << EOF

# 创建新用户
CREATE USER 'chatbot'@'%' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON chatbotai_db.* TO 'chatbot'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'chatbot'@'%';
FLUSH PRIVILEGES;

EOF

# 修改应用配置使用新用户
cd ~/projects/bailianyingyong/chatbotAi
sed -i 's/spring.datasource.username=root/spring.datasource.username=chatbot/g' src/main/resources/application.properties
```

## 快速修复（推荐方案1）

```bash
# 1. 修复MySQL认证
docker exec -it rasp-mysql mysql -u root -p123456 << 'EOF'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT user, host, plugin FROM mysql.user WHERE user='root';
EOF

# 2. 测试连接
mysql -h localhost -P 3306 -u root -p123456 -e "SHOW DATABASES;" 2>&1 | head -5

# 3. 如果还是失败，尝试127.0.0.1
mysql -h 127.0.0.1 -P 3306 -u root -p123456 -e "SHOW DATABASES;" 2>&1 | head -5

# 4. 如果127.0.0.1成功，修改应用配置
cd ~/projects/bailianyingyong/chatbotAi
sed -i 's|jdbc:mysql://localhost:3306|jdbc:mysql://127.0.0.1:3306|g' src/main/resources/application.properties
```

## 验证步骤

修复后验证：

```bash
# 1. 测试localhost连接
mysql -h localhost -P 3306 -u root -p123456 -e "SHOW DATABASES;" 2>&1 | head -5

# 2. 测试127.0.0.1连接
mysql -h 127.0.0.1 -P 3306 -u root -p123456 -e "SHOW DATABASES;" 2>&1 | head -5

# 3. 检查应用配置
cd ~/projects/bailianyingyong/chatbotAi
grep "datasource" src/main/resources/application.properties | grep -E "url|username|password"
```

## 完整启动流程

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 1. 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 2. 修复MySQL认证
echo "=== 修复MySQL认证 ==="
docker exec -it rasp-mysql mysql -u root -p123456 << 'EOF'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

# 3. 测试连接（尝试两种方式）
echo ""
echo "=== 测试MySQL连接 ==="
mysql -h localhost -P 3306 -u root -p123456 -e "SELECT 1;" 2>&1 | head -3 || \
mysql -h 127.0.0.1 -P 3306 -u root -p123456 -e "SELECT 1;" 2>&1 | head -3

# 4. 如果127.0.0.1成功，修改应用配置
if mysql -h 127.0.0.1 -P 3306 -u root -p123456 -e "SELECT 1;" 2>/dev/null; then
    echo "使用127.0.0.1连接成功，修改应用配置..."
    sed -i 's|jdbc:mysql://localhost:3306|jdbc:mysql://127.0.0.1:3306|g' src/main/resources/application.properties
fi

# 5. 设置OpenRASP
echo ""
echo "=== 设置OpenRASP ==="
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 6. 启动应用
echo ""
echo "=== 启动应用 ==="
mvn spring-boot:run
```

