# 修复OpenRASP配置文件

## 问题

OpenRASP配置文件显示：
- `cloud.enable` 被注释（云功能未启用）
- `cloud.backend_url` 被注释（未配置管理后台地址）
- `cloud.app_id` 是占位符 `XXX`（不是实际应用ID）

## 解决方案

### 步骤1：备份配置文件

```bash
# 备份原配置文件
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml.bak
```

### 步骤2：修改配置文件

```bash
# 编辑配置文件
nano /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
```

需要修改的内容：
1. 取消注释 `cloud.enable`，设置为 `true`
2. 取消注释 `cloud.backend_url`，设置为 `http://192.168.203.141:8086`
3. 修改 `cloud.app_id`，设置为 `zhinengtiyingyong`

### 步骤3：使用sed命令快速修改（推荐）

```bash
# 取消注释并设置 cloud.enable
sed -i 's/^#cloud.enable: true/cloud.enable: true/' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml

# 取消注释并设置 cloud.backend_url
sed -i 's|^#cloud.backend_url: http://XXX|cloud.backend_url: http://192.168.203.141:8086|' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml

# 修改 cloud.app_id
sed -i 's/^cloud.app_id: XXX/cloud.app_id: zhinengtiyingyong/' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml

# 验证修改
echo "=== 修改后的配置 ==="
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id"
```

### 步骤4：重启应用

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止应用
pkill -f "spring-boot:run"
sleep 2

# 设置OpenRASP（现在配置文件已正确，可以简化MAVEN_OPTS）
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar \
--add-opens java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens java.base/java.lang=ALL-UNNAMED \
--add-opens java.base/java.util=ALL-UNNAMED"

# 启动应用
mvn spring-boot:run
```

### 步骤5：验证配置

启动后，查看日志中是否有：
```
[OpenRASP] Connecting to backend: http://192.168.203.141:8086
[OpenRASP] App ID: zhinengtiyingyong
[OpenRASP] Registered successfully
```

或者查看OpenRASP日志：
```bash
tail -50 /home/enen/openrasp/rasp-2023-03-31/rasp/logs/rasp.log | grep -E "app_id|backend|cloud|connect|register"
```

## 完整修改脚本

```bash
#!/bin/bash

# 1. 备份配置文件
echo "=== 备份配置文件 ==="
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml.bak
echo "✓ 配置文件已备份"

# 2. 修改配置
echo ""
echo "=== 修改配置 ==="
sed -i 's/^#cloud.enable: true/cloud.enable: true/' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
sed -i 's|^#cloud.backend_url: http://XXX|cloud.backend_url: http://192.168.203.141:8086|' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
sed -i 's/^cloud.app_id: XXX/cloud.app_id: zhinengtiyingyong/' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
echo "✓ 配置已修改"

# 3. 验证修改
echo ""
echo "=== 验证配置 ==="
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id"

# 4. 停止应用
echo ""
echo "=== 停止应用 ==="
cd ~/projects/bailianyingyong/chatbotAi
pkill -f "spring-boot:run"
sleep 2
echo "✓ 应用已停止"

# 5. 启动应用
echo ""
echo "=== 启动应用 ==="
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar \
--add-opens java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens java.base/java.lang=ALL-UNNAMED \
--add-opens java.base/java.util=ALL-UNNAMED"

cd ~/projects/bailianyingyong/chatbotAi
mvn spring-boot:run
```

## 注意事项

1. **配置文件路径**：确保路径 `/home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml` 正确
2. **应用ID**：确保 `zhinengtiyingyong` 与管理后台中的应用ID一致
3. **管理后台地址**：确保 `http://192.168.203.141:8086` 可以访问
4. **重启应用**：修改配置后必须重启应用才能生效

## 如果修改后仍然无法连接

1. **检查网络连接**：
   ```bash
   curl http://192.168.203.141:8086
   ```

2. **查看OpenRASP日志**：
   ```bash
   tail -100 /home/enen/openrasp/rasp-2023-03-31/rasp/logs/rasp.log
   ```

3. **检查管理后台**：
   - 确认管理后台正在运行
   - 确认管理后台允许Agent连接
   - 检查是否有防火墙阻止连接

