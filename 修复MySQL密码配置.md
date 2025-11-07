# 修复MySQL密码配置

## 问题确认

从检查结果看：
- **MySQL容器实际密码**：`123456`（从 `docker inspect rasp-mysql` 看到）
- **应用配置的密码**：`root123`（在 `application.properties` 中）
- **结果**：密码不匹配，导致认证失败

## 立即修复

### 修改应用配置使用正确的密码

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 将密码从root123改为123456
sed -i 's/spring.datasource.password=root123/spring.datasource.password=123456/g' src/main/resources/application.properties

# 验证修改
grep "datasource.password" src/main/resources/application.properties
```

### 测试MySQL连接

```bash
# 使用正确的密码测试
mysql -h localhost -P 3306 -u root -p123456 -e "SHOW DATABASES;"
```

### 使用MAVEN_OPTS启动应用（带OpenRASP）

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 设置OpenRASP（使用MAVEN_OPTS）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar"
export RASP_APP_ID=zhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 验证
echo "MAVEN_OPTS: $MAVEN_OPTS"
echo "RASP_APP_ID: $RASP_APP_ID"

# 启动应用
mvn spring-boot:run
```

## 一键修复脚本

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 1. 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 2. 修复MySQL密码配置
sed -i 's/spring.datasource.password=root123/spring.datasource.password=123456/g' src/main/resources/application.properties

# 3. 验证密码配置
echo "=== MySQL密码配置 ==="
grep "datasource.password" src/main/resources/application.properties

# 4. 测试MySQL连接
echo ""
echo "=== 测试MySQL连接 ==="
mysql -h localhost -P 3306 -u root -p123456 -e "SHOW DATABASES;" 2>&1 | head -5

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

## 验证步骤

### 1. 验证MySQL连接成功

启动后，应该不再看到 `Access denied` 错误。

### 2. 验证OpenRASP已加载

启动后检查：

```bash
# 应该能看到 -javaagent 参数
ps aux | grep java | grep javaagent

# 或者查看日志，应该显示：
# [INFO] Attaching agents: [-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar]
```

### 3. 在OpenRASP管理后台验证

1. 访问：`http://192.168.203.141:8086`
2. 登录
3. 选择应用：`zhinengtiyingyong`
4. 查看是否有数据

## 总结

修复内容：
1. ✅ MySQL密码：`root123` → `123456`
2. ✅ OpenRASP加载：使用 `MAVEN_OPTS` 而不是 `JAVA_OPTS`
3. ✅ 应用ID：使用 `zhinengtiyingyong`（与管理后台一致）

