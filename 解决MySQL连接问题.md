# 解决MySQL连接问题

## 问题分析

应用已成功启动（端口9988），但无法连接到MySQL数据库：
- 错误：`Connection refused`
- 应用运行在：`http://localhost:9988`

## 检查MySQL状态

### 1. 检查MySQL容器是否运行

```bash
# 检查rasp-mysql容器
docker ps | grep mysql

# 检查容器状态
docker ps -a | grep rasp-mysql

# 如果容器未运行，启动它
docker start rasp-mysql

# 查看容器日志
docker logs rasp-mysql
```

### 2. 检查MySQL端口

```bash
# 检查MySQL端口（默认3306）
netstat -tlnp | grep 3306
# 或
ss -tlnp | grep 3306

# 检查容器端口映射
docker port rasp-mysql
```

### 3. 测试MySQL连接

```bash
# 尝试连接MySQL（需要知道用户名和密码）
# 如果容器在运行，尝试：
docker exec -it rasp-mysql mysql -u root -p

# 或者从宿主机连接（如果端口已映射）
mysql -h localhost -P 3306 -u root -p
```

## 检查应用数据库配置

### 1. 查看应用配置文件

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 查找数据库配置文件
find . -name "application.properties" -o -name "application.yml" -o -name "application.yaml"

# 查看配置
cat src/main/resources/application.properties 2>/dev/null || \
cat src/main/resources/application.yml 2>/dev/null || \
cat src/main/resources/application.yaml 2>/dev/null
```

### 2. 检查数据库连接配置

配置文件可能包含：
- `spring.datasource.url` - 数据库URL
- `spring.datasource.username` - 用户名
- `spring.datasource.password` - 密码
- `spring.datasource.host` - 主机地址

## 解决方案

### 方案1：启动MySQL容器（如果未运行）

```bash
# 启动rasp-mysql容器
docker start rasp-mysql

# 等待几秒让MySQL完全启动
sleep 5

# 验证容器运行
docker ps | grep mysql

# 验证端口
netstat -tlnp | grep 3306
```

### 方案2：检查数据库配置是否正确

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 查看配置文件
cat src/main/resources/application.properties

# 检查数据库URL是否正确
# 如果MySQL在Docker容器中，可能需要使用：
# - localhost（如果端口已映射）
# - 容器名称（如果在同一Docker网络中）
# - 容器IP地址
```

### 方案3：如果MySQL在Docker容器中，检查网络

```bash
# 查看容器网络
docker network ls

# 查看rasp-mysql容器的网络
docker inspect rasp-mysql | grep -A 10 "Networks"

# 如果应用也需要连接到MySQL，可能需要：
# 1. 使用localhost:3306（如果端口已映射）
# 2. 或者将应用也加入Docker网络
```

### 方案4：临时跳过数据库初始化（仅用于测试OpenRASP）

如果只是想测试OpenRASP是否工作，可以临时禁用数据库连接：

```bash
# 在application.properties中添加：
# spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

**注意**：这会导致应用无法使用数据库功能，仅用于测试OpenRASP。

## 验证OpenRASP是否已加载

虽然日志显示 `[INFO] Attaching agents: []`，但OpenRASP可能已经加载。验证方法：

### 1. 检查进程

```bash
# 查看Java进程的启动参数
ps aux | grep java | grep bailianyingyong

# 应该能看到 -javaagent 参数
```

### 2. 在OpenRASP管理后台查看

1. 访问：`http://192.168.203.141:8086`
2. 登录（用户名：`openrasp`，密码：`zzy100416`）
3. 查看"应用列表"，应该能看到 `bailianyingyong-backend`

### 3. 测试应用API（如果应用已启动）

```bash
# 测试应用是否响应（即使数据库连接失败，应用也可能已启动）
curl http://localhost:9988

# 或者访问健康检查端点（如果有）
curl http://localhost:9988/actuator/health
```

## 快速修复步骤

```bash
# 1. 检查并启动MySQL
docker ps -a | grep mysql
docker start rasp-mysql

# 2. 等待MySQL启动
sleep 5

# 3. 验证MySQL运行
docker ps | grep mysql
netstat -tlnp | grep 3306

# 4. 检查应用配置
cd ~/projects/bailianyingyong/chatbotAi
cat src/main/resources/application.properties | grep -E "datasource|mysql|jdbc"

# 5. 如果配置正确，重启应用
# 停止当前应用（Ctrl+C），然后重新启动
```

## 下一步

1. ✅ 应用已启动（端口9988）
2. ✅ OpenRASP Agent已配置
3. ⏳ 修复MySQL连接问题
4. ⏳ 验证OpenRASP连接（在管理后台查看）
5. ⏳ 测试应用功能

## 重要提示

即使数据库连接失败，应用也可能已经启动并运行。OpenRASP可能已经加载。请：
1. 先检查OpenRASP管理后台，看是否能找到应用
2. 然后解决MySQL连接问题
3. 最后验证完整功能

