# 详细排查MySQL连接问题

## 问题分析

即使密码正确，仍可能连接不上MySQL，常见原因：
1. MySQL容器端口未映射到宿主机
2. MySQL只允许容器内连接，不允许外部连接
3. 需要使用容器名称而不是localhost
4. MySQL用户权限问题

## 详细排查步骤

### 步骤1：检查MySQL容器端口映射

```bash
# 查看MySQL容器的端口映射
docker port rasp-mysql

# 查看容器详细信息
docker inspect rasp-mysql | grep -A 20 "Ports"

# 如果输出为空或只有容器内端口，说明端口未映射到宿主机
```

### 步骤2：检查MySQL是否监听在宿主机

```bash
# 检查3306端口是否在监听
netstat -tlnp | grep 3306
# 或
ss -tlnp | grep 3306

# 如果看不到3306端口，说明MySQL只在容器内监听
```

### 步骤3：测试从容器内连接MySQL

```bash
# 进入MySQL容器测试
docker exec -it rasp-mysql mysql -u root -p123456 -e "SHOW DATABASES;"

# 如果容器内能连接，说明MySQL正常，问题在端口映射
```

### 步骤4：检查MySQL用户权限

```bash
# 进入MySQL容器
docker exec -it rasp-mysql mysql -u root -p123456

# 在MySQL中执行：
SHOW GRANTS FOR 'root'@'localhost';
SHOW GRANTS FOR 'root'@'%';

# 如果root@'%'不存在或没有权限，需要创建：
CREATE USER 'root'@'%' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

## 解决方案

### 方案1：如果端口未映射，重新创建容器（推荐）

```bash
# 1. 停止并删除旧容器（注意：会丢失数据，除非有数据卷）
docker stop rasp-mysql
docker rm rasp-mysql

# 2. 重新创建容器并映射端口
docker run -d \
  --name rasp-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=chatbotai_db \
  mysql:5.7

# 3. 等待MySQL启动
sleep 10

# 4. 测试连接
mysql -h localhost -P 3306 -u root -p123456 -e "SHOW DATABASES;"
```

### 方案2：如果不想重新创建容器，使用Docker网络

```bash
# 1. 检查容器网络
docker inspect rasp-mysql | grep -A 10 "Networks"

# 2. 获取容器IP
docker inspect rasp-mysql | grep "IPAddress"

# 3. 使用容器IP连接（在应用配置中）
# 例如：jdbc:mysql://172.17.0.2:3306/chatbotai_db
```

### 方案3：修改应用配置使用容器名称（如果在Docker网络中）

如果应用也在Docker容器中运行，可以使用容器名称：

```bash
# 修改应用配置
cd ~/projects/bailianyingyong/chatbotAi

# 将localhost改为容器名称或IP
# 但应用在宿主机运行，所以不能直接用容器名
```

### 方案4：配置MySQL允许外部连接

```bash
# 进入MySQL容器
docker exec -it rasp-mysql mysql -u root -p123456

# 在MySQL中执行：
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

# 退出
exit
```

### 方案5：检查MySQL配置文件

```bash
# 查看MySQL容器的配置文件
docker exec -it rasp-mysql cat /etc/mysql/my.cnf | grep bind-address

# 如果bind-address是127.0.0.1，需要改为0.0.0.0
# 但这需要修改MySQL配置并重启容器
```

## 快速诊断脚本

```bash
cat > check-mysql.sh << 'EOF'
#!/bin/bash

echo "=== MySQL连接诊断 ==="
echo ""

echo "1. 检查MySQL容器状态："
docker ps | grep mysql
echo ""

echo "2. 检查端口映射："
docker port rasp-mysql
echo ""

echo "3. 检查宿主机端口监听："
netstat -tlnp | grep 3306 || echo "端口3306未在宿主机监听"
echo ""

echo "4. 检查容器IP："
docker inspect rasp-mysql | grep "IPAddress" | head -1
echo ""

echo "5. 测试容器内连接："
docker exec -it rasp-mysql mysql -u root -p123456 -e "SELECT 1;" 2>&1 | head -3
echo ""

echo "6. 测试宿主机连接："
mysql -h localhost -P 3306 -u root -p123456 -e "SELECT 1;" 2>&1 | head -3
echo ""

echo "7. 检查MySQL用户权限："
docker exec -it rasp-mysql mysql -u root -p123456 -e "SELECT user, host FROM mysql.user WHERE user='root';" 2>&1
echo ""

echo "=== 诊断完成 ==="
EOF

chmod +x check-mysql.sh
./check-mysql.sh
```

## 最可能的解决方案

根据常见情况，最可能的问题是**端口未映射**。执行：

```bash
# 1. 检查端口映射
docker port rasp-mysql

# 2. 如果输出为空，说明端口未映射
# 需要重新创建容器并映射端口：

# 停止并删除旧容器（注意备份数据）
docker stop rasp-mysql
docker rm rasp-mysql

# 重新创建并映射端口
docker run -d \
  --name rasp-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=chatbotai_db \
  mysql:5.7

# 等待启动
sleep 10

# 测试连接
mysql -h localhost -P 3306 -u root -p123456 -e "SHOW DATABASES;"
```

## 如果不想重新创建容器

### 使用容器IP连接

```bash
# 获取容器IP
MYSQL_IP=$(docker inspect rasp-mysql | grep "IPAddress" | head -1 | awk '{print $2}' | tr -d '",')

echo "MySQL容器IP: $MYSQL_IP"

# 测试连接
mysql -h $MYSQL_IP -P 3306 -u root -p123456 -e "SHOW DATABASES;"

# 如果成功，修改应用配置
cd ~/projects/bailianyingyong/chatbotAi
sed -i "s|jdbc:mysql://localhost:3306|jdbc:mysql://$MYSQL_IP:3306|g" src/main/resources/application.properties
```

## 验证步骤

修复后验证：

```bash
# 1. 测试MySQL连接
mysql -h localhost -P 3306 -u root -p123456 -e "SHOW DATABASES;"

# 2. 如果使用容器IP，测试
MYSQL_IP=$(docker inspect rasp-mysql | grep "IPAddress" | head -1 | awk '{print $2}' | tr -d '",')
mysql -h $MYSQL_IP -P 3306 -u root -p123456 -e "SHOW DATABASES;"

# 3. 启动应用
cd ~/projects/bailianyingyong/chatbotAi
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086
mvn spring-boot:run
```

