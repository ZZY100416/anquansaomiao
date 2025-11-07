# 修复MySQL认证 - 正确命令

## 问题

容器名应该是 `rasp-mysql`，不是 `rasp`。

## 正确的修复命令

```bash
# 修复MySQL认证（使用正确的容器名）
docker exec -it rasp-mysql mysql -u root -p123456 << 'EOF'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT user, host, plugin FROM mysql.user WHERE user='root';
EOF
```

## 完整修复和启动流程

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 1. 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 2. 修复MySQL认证（注意：容器名是 rasp-mysql）
echo "=== 修复MySQL认证 ==="
docker exec -it rasp-mysql mysql -u root -p123456 << 'EOF'
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

# 3. 测试连接
echo ""
echo "=== 测试MySQL连接 ==="
mysql -h 127.0.0.1 -P 3306 -u root -p123456 -e "SHOW DATABASES;" 2>&1 | head -5

# 4. 修改应用配置使用127.0.0.1（更可靠）
sed -i 's|jdbc:mysql://localhost:3306|jdbc:mysql://127.0.0.1:3306|g' src/main/resources/application.properties

# 5. 设置OpenRASP
echo ""
echo "=== 设置OpenRASP ==="
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

echo "MAVEN_OPTS: $MAVEN_OPTS"
echo "RASP_APP_ID: $RASP_APP_ID"
echo ""

# 6. 启动应用
echo "=== 启动应用 ==="
mvn spring-boot:run
```

