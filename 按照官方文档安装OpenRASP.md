# 按照OpenRASP官方文档安装Spring Boot应用

参考文档：https://rasp.baidu.com/doc/install/manual/spring-boot.html

## 官方文档方法：使用RaspInstall.jar

根据OpenRASP官方文档，推荐使用`RaspInstall.jar`来安装和配置OpenRASP Agent。

## 步骤1：检查RaspInstall.jar

```bash
# 检查RaspInstall.jar是否存在
ls -la /home/enen/openrasp/rasp-2023-03-31/rasp/RaspInstall.jar

# 如果不存在，检查其他可能的位置
find /home/enen/openrasp -name "RaspInstall.jar" 2>/dev/null
```

## 步骤2：从管理后台获取应用ID和密钥

根据官方文档，需要从OpenRASP管理后台获取：
- `appid`：应用ID
- `appsecret`：应用密钥

### 方法1：在管理后台查看应用详情

1. 访问：`http://192.168.203.141:8086`
2. 登录（用户名：`openrasp`，密码：`zzy100416`）
3. 进入"应用管理"
4. 点击应用 `zhinengtiyingyong`
5. 查看应用详情，找到：
   - 应用ID（appid）
   - 应用密钥（appsecret）

### 方法2：在"添加主机"对话框中查看

1. 在管理后台点击"添加主机"
2. 选择"Java 服务器"标签
3. 在安装说明中会显示示例命令，包含`appid`和`appsecret`

## 步骤3：使用RaspInstall.jar安装

```bash
cd /home/enen/openrasp/rasp-2023-03-31/rasp

# 使用RaspInstall.jar安装
# 注意：需要替换<appid>和<appsecret>为从管理后台获取的实际值
java -jar RaspInstall.jar \
  -heartbeat 90 \
  -appid <从管理后台获取的应用ID> \
  -appsecret <从管理后台获取的应用密钥> \
  -backendurl http://192.168.203.141:8086/ \
  -install ~/projects/bailianyingyong/chatbotAi
```

## 步骤4：验证安装

安装后，RaspInstall.jar会：
1. 修改配置文件（`openrasp.yml`）
2. 可能创建启动脚本
3. 配置应用ID和密钥

```bash
# 检查配置文件是否被修改
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"

# 检查是否有启动脚本
ls -la ~/projects/bailianyingyong/chatbotAi/*.sh
```

## 步骤5：重启应用

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止应用
pkill -f "spring-boot:run"
sleep 2

# 如果RaspInstall.jar创建了启动脚本，使用它
# 否则，使用原来的方式启动
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar \
--add-opens=java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.lang=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED"

mvn spring-boot:run
```

## 如果找不到appid和appsecret

### 方法1：查看应用列表的详细信息

在管理后台的"应用管理"页面，查看应用的详细信息，可能包含：
- 应用ID
- 应用密钥
- 或其他标识符

### 方法2：使用应用名称

如果找不到具体的appid和appsecret，可以尝试：
1. 使用应用名称 `zhinengtiyingyong`
2. 或者查看管理后台URL中的ID（如果有）

### 方法3：重新创建应用

如果无法获取，可以在管理后台：
1. 删除现有应用
2. 重新创建应用
3. 在创建时记录应用ID和密钥

## 完整安装脚本

```bash
#!/bin/bash

echo "=== 按照OpenRASP官方文档安装 ==="
echo ""

# 1. 检查RaspInstall.jar
echo "步骤1: 检查RaspInstall.jar"
RASP_INSTALL_JAR="/home/enen/openrasp/rasp-2023-03-31/rasp/RaspInstall.jar"
if [ -f "$RASP_INSTALL_JAR" ]; then
    echo "✓ 找到 RaspInstall.jar: $RASP_INSTALL_JAR"
else
    echo "✗ 未找到 RaspInstall.jar"
    echo "  请检查OpenRASP安装路径"
    exit 1
fi

# 2. 提示用户输入appid和appsecret
echo ""
echo "步骤2: 需要从管理后台获取应用ID和密钥"
echo "请访问: http://192.168.203.141:8086"
echo "在'应用管理'中查看应用 'zhinengtiyingyong' 的详细信息"
echo ""
read -p "请输入应用ID (appid): " APP_ID
read -p "请输入应用密钥 (appsecret): " APP_SECRET

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
    echo "✗ 应用ID或密钥不能为空"
    exit 1
fi

# 3. 使用RaspInstall.jar安装
echo ""
echo "步骤3: 使用RaspInstall.jar安装"
cd /home/enen/openrasp/rasp-2023-03-31/rasp

java -jar RaspInstall.jar \
  -heartbeat 90 \
  -appid "$APP_ID" \
  -appsecret "$APP_SECRET" \
  -backendurl http://192.168.203.141:8086/ \
  -install ~/projects/bailianyingyong/chatbotAi

if [ $? -eq 0 ]; then
    echo "✓ 安装成功"
else
    echo "✗ 安装失败"
    exit 1
fi

# 4. 验证配置
echo ""
echo "步骤4: 验证配置"
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
echo ""

echo "=== 安装完成 ==="
echo "请重启应用以使配置生效"
```

## 注意事项

1. **appid和appsecret**：必须从OpenRASP管理后台获取，不能随意设置
2. **安装路径**：`-install`参数指向Spring Boot项目的根目录
3. **配置文件**：RaspInstall.jar会修改`openrasp.yml`，建议先备份
4. **重启应用**：安装后必须重启应用才能生效

## 如果RaspInstall.jar不存在

如果找不到`RaspInstall.jar`，可能需要：
1. 重新下载OpenRASP安装包
2. 或者手动配置（使用之前的方法）

## 验证安装成功

安装并重启应用后：
1. 查看启动日志，确认没有YAML错误
2. 查看OpenRASP日志：`tail -50 /home/enen/openrasp/rasp-2023-03-31/rasp/logs/rasp.log`
3. 在管理后台的"主机管理"中查看是否有主机注册
4. 等待几分钟，看是否有心跳信息

