# 彻底修复MySQL连接问题

## 问题分析

即使修复了认证，还是连接不上。可能原因：
1. MySQL修复命令没有成功执行
2. MySQL版本问题（8.0 vs 5.7认证方式不同）
3. 需要检查实际的用户配置

## 详细排查和修复

### 步骤1：检查MySQL版本和用户配置

```bash
# 检查MySQL版本
docker exec -it rasp-mysql mysql -u root -p123456 -e "SELECT VERSION();"

# 查看所有root用户的配置
docker exec -it rasp-mysql mysql -u root -p123456 -e "SELECT user, host, plugin, authentication_string FROM mysql.user WHERE user='root';"
```

### 步骤2：彻底修复认证（适用于MySQL 8.0）

```bash
# 进入MySQL容器并修复
docker exec -it rasp-mysql mysql -u root -p123456 << 'EOF'

-- 查看当前配置
SELECT user, host, plugin FROM mysql.user WHERE user='root';

-- 删除所有root用户（如果存在）
DROP USER IF EXISTS 'root'@'localhost';
DROP USER IF EXISTS 'root'@'%';

-- 重新创建root用户（MySQL 8.0方式）
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';
CREATE USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123456';

-- 授予权限
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证
SELECT user, host, plugin FROM mysql.user WHERE user='root';

EOF
```

### 步骤3：如果MySQL 5.7，使用不同的方式

```bash
docker exec -it rasp-mysql mysql -u root -p123456 << 'EOF'

-- MySQL 5.7方式
UPDATE mysql.user SET plugin='mysql_native_password' WHERE user='root';
UPDATE mysql.user SET authentication_string=PASSWORD('123456') WHERE user='root' AND host='localhost';
UPDATE mysql.user SET authentication_string=PASSWORD('123456') WHERE user='root' AND host='%';
FLUSH PRIVILEGES;

EOF
```

### 步骤4：使用Docker网络IP连接（备选方案）

如果认证修复还是不行，可以获取容器IP并使用IP连接：

```bash
# 获取容器IP
MYSQL_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' rasp-mysql)
echo "MySQL容器IP: $MYSQL_IP"

# 测试连接
mysql -h $MYSQL_IP -P 3306 -u root -p123456 -e "SHOW DATABASES;" 2>&1 | head -5

# 如果成功，修改应用配置
cd ~/projects/bailianyingyong/chatbotAi
sed -i "s|jdbc:mysql://127.0.0.1:3306|jdbc:mysql://$MYSQL_IP:3306|g" src/main/resources/application.properties
```

## 一键修复脚本（自动检测MySQL版本）

```bash
cat > fix-mysql-auth.sh << 'EOF'
#!/bin/bash

echo "=== 修复MySQL认证 ==="

# 检查MySQL版本
MYSQL_VERSION=$(docker exec -it rasp-mysql mysql -u root -p123456 -e "SELECT VERSION();" 2>/dev/null | grep -E "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
echo "MySQL版本: $MYSQL_VERSION"

# 判断是8.0还是5.7
if echo "$MYSQL_VERSION" | grep -q "^8\."; then
    echo "检测到MySQL 8.0，使用8.0修复方式"
    docker exec -it rasp-mysql mysql -u root -p123456 << 'SQL'
DROP USER IF EXISTS 'root'@'localhost';
DROP USER IF EXISTS 'root'@'%';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';
CREATE USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT user, host, plugin FROM mysql.user WHERE user='root';
SQL
else
    echo "检测到MySQL 5.7，使用5.7修复方式"
    docker exec -it rasp-mysql mysql -u root -p123456 << 'SQL'
UPDATE mysql.user SET plugin='mysql_native_password' WHERE user='root';
UPDATE mysql.user SET authentication_string=PASSWORD('123456') WHERE user='root';
FLUSH PRIVILEGES;
SELECT user, host, plugin FROM mysql.user WHERE user='root';
SQL
fi

echo ""
echo "=== 测试连接 ==="
mysql -h 127.0.0.1 -P 3306 -u root -p123456 -e "SHOW DATABASES;" 2>&1 | head -5

EOF

chmod +x fix-mysql-auth.sh
./fix-mysql-auth.sh
```

## 如果还是不行，使用容器IP（最可靠）

```bash
# 获取容器IP
MYSQL_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' rasp-mysql)
echo "MySQL容器IP: $MYSQL_IP"

# 测试连接
mysql -h $MYSQL_IP -P 3306 -u root -p123456 -e "SHOW DATABASES;" 2>&1 | head -5

# 如果成功，修改应用配置
cd ~/projects/bailianyingyong/chatbotAi
sed -i "s|jdbc:mysql://127.0.0.1:3306|jdbc:mysql://$MYSQL_IP:3306|g" src/main/resources/application.properties
sed -i "s|jdbc:mysql://localhost:3306|jdbc:mysql://$MYSQL_IP:3306|g" src/main/resources/application.properties

# 验证
grep "datasource.url" src/main/resources/application.properties
```

## 完整修复流程

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 1. 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 2. 检查MySQL版本
echo "=== 检查MySQL版本 ==="
docker exec -it rasp-mysql mysql -u root -p123456 -e "SELECT VERSION();" 2>&1 | grep -E "[0-9]+\.[0-9]+"

# 3. 修复认证（MySQL 8.0方式）
echo ""
echo "=== 修复MySQL认证 ==="
docker exec -it rasp-mysql mysql -u root -p123456 << 'EOF'
DROP USER IF EXISTS 'root'@'localhost';
DROP USER IF EXISTS 'root'@'%';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';
CREATE USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

# 4. 测试连接（多种方式）
echo ""
echo "=== 测试连接 ==="
mysql -h 127.0.0.1 -P 3306 -u root -p123456 -e "SELECT 1;" 2>&1 | head -3 || \
mysql -h localhost -P 3306 -u root -p123456 -e "SELECT 1;" 2>&1 | head -3 || \
echo "尝试使用容器IP..."

# 5. 如果还是失败，使用容器IP
MYSQL_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' rasp-mysql)
echo "MySQL容器IP: $MYSQL_IP"
mysql -h $MYSQL_IP -P 3306 -u root -p123456 -e "SELECT 1;" 2>&1 | head -3

if [ $? -eq 0 ]; then
    echo "使用容器IP连接成功，修改应用配置..."
    sed -i "s|jdbc:mysql://.*:3306|jdbc:mysql://$MYSQL_IP:3306|g" src/main/resources/application.properties
    grep "datasource.url" src/main/resources/application.properties
fi

# 6. 设置OpenRASP
echo ""
echo "=== 设置OpenRASP ==="
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 7. 启动应用
echo ""
echo "=== 启动应用 ==="
mvn spring-boot:run
```

