# 使用现有的RaspInstall.jar安装OpenRASP

## 发现

`RaspInstall.jar` 位于：`/home/enen/openrasp/rasp-2023-03-31/RaspInstall.jar`

## 从管理后台获取的信息

- **appid**: `0c91b98f2aa79983228f10fc37725da726bd31d6`
- **appsecret**: `03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU`
- **backendurl**: `http://192.168.203.141:8086/`

## 安装步骤

### 步骤1：使用RaspInstall.jar安装

```bash
cd /home/enen/openrasp/rasp-2023-03-31

# 使用RaspInstall.jar安装
java -jar RaspInstall.jar \
  -heartbeat 90 \
  -appid 0c91b98f2aa79983228f10fc37725da726bd31d6 \
  -appsecret 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU \
  -backendurl http://192.168.203.141:8086/ \
  -install ~/projects/bailianyingyong/chatbotAi
```

### 步骤2：验证安装

```bash
# 检查是否创建了rasp目录
ls -la ~/projects/bailianyingyong/chatbotAi/rasp/

# 检查配置文件
cat ~/projects/bailianyingyong/chatbotAi/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
```

### 步骤3：配置启动参数

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止应用
pkill -f "spring-boot:run"
sleep 2

# 使用安装后的rasp.jar（在应用目录下）
export MAVEN_OPTS="-javaagent:/home/enen/projects/bailianyingyong/chatbotAi/rasp/rasp.jar \
--add-opens=java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.lang=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED"

# 启动应用
mvn spring-boot:run
```

### 步骤4：验证安装成功

1. **检查响应头**：
   ```bash
   curl -I http://localhost:9988
   # 应该看到：X-Protected-By: OpenRASP
   ```

2. **查看启动日志**：应该看到`[OpenRASP] Engine Initialized`，没有YAML错误

3. **在管理后台验证**：
   - 访问：`http://192.168.203.141:8086`
   - 在"主机管理"中查看是否有主机注册
   - 等待几分钟，看是否有心跳信息

## 完整安装命令

```bash
# 1. 安装
cd /home/enen/openrasp/rasp-2023-03-31
java -jar RaspInstall.jar \
  -heartbeat 90 \
  -appid 0c91b98f2aa79983228f10fc37725da726bd31d6 \
  -appsecret 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU \
  -backendurl http://192.168.203.141:8086/ \
  -install ~/projects/bailianyingyong/chatbotAi

# 2. 验证
echo "=== 验证安装 ==="
ls -la ~/projects/bailianyingyong/chatbotAi/rasp/
echo ""
cat ~/projects/bailianyingyong/chatbotAi/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"

# 3. 重启应用
cd ~/projects/bailianyingyong/chatbotAi
pkill -f "spring-boot:run"
sleep 2

export MAVEN_OPTS="-javaagent:/home/enen/projects/bailianyingyong/chatbotAi/rasp/rasp.jar \
--add-opens=java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.lang=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED"

mvn spring-boot:run
```

