# 根据OpenRASP官方文档配置Spring Boot应用

参考文档：https://rasp.baidu.com/doc/install/manual/spring-boot.html

## 当前状态

- OpenRASP已安装：`/home/enen/openrasp/rasp-2023-03-31/rasp/`
- Spring Boot应用：`~/projects/bailianyingyong/chatbotAi`
- Java版本：Java 21（需要JDK 11+的配置方式）
- 管理后台：`http://192.168.203.141:8086`
- 应用ID：`zhinengtiyingyong`

## 步骤1：配置OpenRASP配置文件

根据OpenRASP文档，需要配置 `openrasp.yml` 文件来连接管理后台：

```bash
# 1. 备份配置文件
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml.bak

# 2. 修改配置文件
# 取消注释并启用云功能
sed -i 's/^#cloud.enable: true/cloud.enable: true/' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml

# 设置管理后台地址
sed -i 's|^#cloud.backend_url: http://XXX|cloud.backend_url: http://192.168.203.141:8086|' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml

# 设置应用ID
sed -i 's/^cloud.app_id: XXX/cloud.app_id: zhinengtiyingyong/' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml

# 3. 验证配置
echo "=== 修改后的配置 ==="
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id"
```

## 步骤2：配置Spring Boot启动参数

根据OpenRASP文档，对于JDK 11+，需要使用以下启动参数：

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止旧进程
pkill -f "spring-boot:run"
sleep 2

# 设置Maven启动参数（JDK 11+配置）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar \
--add-opens=java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.lang=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED"

# 启动应用
mvn spring-boot:run
```

## 步骤3：验证安装

根据OpenRASP文档，验证安装成功的方法：

### 方法1：检查响应头

启动应用后，访问应用，检查HTTP响应头中是否包含：
```
X-Protected-By: OpenRASP
```

```bash
# 测试本地访问
curl -I http://localhost:9988

# 或从Windows访问
# 在浏览器开发者工具的Network标签中查看响应头
```

### 方法2：查看启动日志

启动后，查看日志中是否有OpenRASP相关信息：
- `[OpenRASP] Engine Initialized`
- `[OpenRASP] Connecting to backend`
- `[OpenRASP] App ID: zhinengtiyingyong`

### 方法3：查看OpenRASP日志

```bash
# 查看OpenRASP日志
tail -50 /home/enen/openrasp/rasp-2023-03-31/rasp/logs/rasp.log | grep -E "app_id|backend|cloud|connect|register|initialized"
```

### 方法4：在管理后台验证

1. 访问：`http://192.168.203.141:8086`
2. 登录（用户名：`openrasp`，密码：`zzy100416`）
3. 在"当前应用"下拉菜单中选择 `zhinengtiyingyong`
4. 查看应用状态、连接信息、安全事件等

## 完整配置脚本

```bash
#!/bin/bash

echo "=== 根据OpenRASP官方文档配置Spring Boot应用 ==="
echo ""

# 1. 备份配置文件
echo "步骤1: 备份配置文件"
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml.bak
echo "✓ 配置文件已备份"
echo ""

# 2. 修改配置文件
echo "步骤2: 修改OpenRASP配置"
sed -i 's/^#cloud.enable: true/cloud.enable: true/' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
sed -i 's|^#cloud.backend_url: http://XXX|cloud.backend_url: http://192.168.203.141:8086|' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
sed -i 's/^cloud.app_id: XXX/cloud.app_id: zhinengtiyingyong/' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
echo "✓ 配置已修改"
echo ""

# 3. 验证配置
echo "步骤3: 验证配置"
echo "---"
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id"
echo "---"
echo ""

# 4. 停止应用
echo "步骤4: 停止应用"
cd ~/projects/bailianyingyong/chatbotAi
pkill -f "spring-boot:run"
sleep 2
echo "✓ 应用已停止"
echo ""

# 5. 设置启动参数（JDK 11+配置）
echo "步骤5: 设置启动参数"
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar \
--add-opens=java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.lang=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED"
echo "MAVEN_OPTS: $MAVEN_OPTS"
echo ""

# 6. 启动应用
echo "步骤6: 启动应用"
echo "请查看启动日志，确认OpenRASP是否成功初始化"
echo ""
mvn spring-boot:run
```

## 注意事项

1. **Java版本**：当前使用Java 21，需要JDK 11+的配置方式（添加`--add-opens`参数）
2. **配置文件路径**：确保OpenRASP配置文件路径正确
3. **应用ID**：确保`zhinengtiyingyong`与管理后台中的应用ID一致
4. **管理后台地址**：确保`http://192.168.203.141:8086`可以访问
5. **重启应用**：修改配置后必须重启应用才能生效

## 故障排查

如果启动后OpenRASP仍然无法连接：

1. **检查网络连接**：
   ```bash
   curl http://192.168.203.141:8086
   ```

2. **查看详细日志**：
   ```bash
   tail -100 /home/enen/openrasp/rasp-2023-03-31/rasp/logs/rasp.log
   ```

3. **检查配置文件语法**：
   ```bash
   cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -A 5 -B 5 "cloud"
   ```

4. **参考官方文档**：
   - 主文档：https://rasp.baidu.com/doc/install/main.html
   - Spring Boot集成：https://rasp.baidu.com/doc/install/manual/spring-boot.html

