# 按照OpenRASP官方文档使用RaspInstall.jar安装

参考文档：https://rasp.baidu.com/doc/install/manual/spring-boot.html

## 官方文档方法

根据OpenRASP官方文档，推荐使用`RaspInstall.jar`来安装和配置OpenRASP Agent。

## 步骤1：检查RaspInstall.jar

```bash
# 检查RaspInstall.jar是否存在
ls -la /home/enen/openrasp/rasp-2023-03-31/rasp/RaspInstall.jar

# 如果不存在，查找其他位置
find /home/enen/openrasp -name "RaspInstall.jar" 2>/dev/null
```

## 步骤2：从管理后台获取应用ID和密钥

根据官方文档，需要从OpenRASP管理后台获取：
- `app_id`：应用ID
- `app_secret`：应用密钥
- `backend_url`：管理后台地址（已知：`http://192.168.203.141:8086`）

### 获取方法

1. 访问：`http://192.168.203.141:8086`
2. 登录（用户名：`openrasp`，密码：`zzy100416`）
3. 进入"应用管理"
4. 点击应用 `zhinengtiyingyong`
5. 查看应用详情，找到应用ID和密钥
6. 或者在"添加主机"对话框中查看示例命令

## 步骤3：使用RaspInstall.jar安装

根据官方文档，安装命令格式：

```bash
cd /home/enen/openrasp/rasp-2023-03-31/rasp

# 使用RaspInstall.jar安装（需要替换app_id和app_secret）
java -jar RaspInstall.jar \
  -nodetect \
  -install ~/projects/bailianyingyong/chatbotAi \
  -backendurl http://192.168.203.141:8086 \
  -appsecret <从管理后台获取的应用密钥> \
  -appid <从管理后台获取的应用ID>
```

**注意**：
- `-nodetect`：不自动检测服务器类型
- `-install`：Spring Boot应用目录
- `-backendurl`：管理后台地址
- `-appsecret`：应用密钥
- `-appid`：应用ID

## 步骤4：验证安装

安装后，RaspInstall.jar会：
1. 在应用目录下创建`rasp`目录
2. 复制OpenRASP文件到应用目录
3. 配置`rasp/conf/openrasp.yml`

```bash
# 检查是否创建了rasp目录
ls -la ~/projects/bailianyingyong/chatbotAi/rasp/

# 检查配置文件
cat ~/projects/bailianyingyong/chatbotAi/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
```

## 步骤5：配置启动参数

根据官方文档，对于JDK 11+，需要添加`--add-opens`参数：

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止应用
pkill -f "spring-boot:run"
sleep 2

# 使用安装后的rasp.jar（在应用目录下）
export MAVEN_OPTS="-javaagent:~/projects/bailianyingyong/chatbotAi/rasp/rasp.jar \
--add-opens=java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.lang=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED"

# 或者使用绝对路径
export MAVEN_OPTS="-javaagent:/home/enen/projects/bailianyingyong/chatbotAi/rasp/rasp.jar \
--add-opens=java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.lang=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED"

# 启动应用
mvn spring-boot:run
```

## 步骤6：验证安装成功

根据官方文档，验证方法：

1. **检查响应头**：
   ```bash
   # 访问应用，检查响应头
   curl -I http://localhost:9988
   # 应该看到：X-Protected-By: OpenRASP
   ```

2. **查看启动日志**：
   - 应该看到：`[OpenRASP] Engine Initialized`
   - 不应该有YAML解析错误

3. **查看OpenRASP日志**：
   ```bash
   tail -50 ~/projects/bailianyingyong/chatbotAi/rasp/logs/rasp.log
   ```

4. **在管理后台验证**：
   - 访问：`http://192.168.203.141:8086`
   - 在"主机管理"中查看是否有主机注册
   - 等待几分钟，看是否有心跳信息

## 完整安装脚本

```bash
#!/bin/bash

echo "=== 按照OpenRASP官方文档安装 ==="
echo ""

# 1. 检查RaspInstall.jar
echo "步骤1: 检查RaspInstall.jar"
RASP_DIR="/home/enen/openrasp/rasp-2023-03-31/rasp"
RASP_INSTALL_JAR="$RASP_DIR/RaspInstall.jar"

if [ ! -f "$RASP_INSTALL_JAR" ]; then
    echo "✗ 未找到 RaspInstall.jar: $RASP_INSTALL_JAR"
    echo "  请检查OpenRASP安装路径"
    exit 1
fi

echo "✓ 找到 RaspInstall.jar: $RASP_INSTALL_JAR"
echo ""

# 2. 提示用户输入appid和appsecret
echo "步骤2: 需要从管理后台获取应用ID和密钥"
echo "请访问: http://192.168.203.141:8086"
echo "在'应用管理'中查看应用 'zhinengtiyingyong' 的详细信息"
echo "或者在'添加主机'对话框中查看示例命令"
echo ""
read -p "请输入应用ID (appid): " APP_ID
read -p "请输入应用密钥 (appsecret): " APP_SECRET

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
    echo "✗ 应用ID或密钥不能为空"
    exit 1
fi

# 3. 备份应用目录（可选）
echo ""
echo "步骤3: 备份应用目录（可选）"
APP_DIR="$HOME/projects/bailianyingyong/chatbotAi"
if [ -d "$APP_DIR/rasp" ]; then
    echo "  发现已存在的rasp目录，备份中..."
    mv "$APP_DIR/rasp" "$APP_DIR/rasp.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 4. 使用RaspInstall.jar安装
echo ""
echo "步骤4: 使用RaspInstall.jar安装"
cd "$RASP_DIR"

java -jar RaspInstall.jar \
  -nodetect \
  -install "$APP_DIR" \
  -backendurl http://192.168.203.141:8086 \
  -appsecret "$APP_SECRET" \
  -appid "$APP_ID"

if [ $? -eq 0 ]; then
    echo "✓ 安装成功"
else
    echo "✗ 安装失败"
    exit 1
fi

# 5. 验证配置
echo ""
echo "步骤5: 验证配置"
if [ -f "$APP_DIR/rasp/conf/openrasp.yml" ]; then
    echo "✓ 配置文件已创建"
    echo ""
    echo "配置内容："
    cat "$APP_DIR/rasp/conf/openrasp.yml" | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret" || echo "未找到cloud配置"
else
    echo "✗ 配置文件未创建"
fi

echo ""
echo "=== 安装完成 ==="
echo ""
echo "下一步："
echo "1. 配置启动参数（使用应用目录下的rasp.jar）"
echo "2. 重启应用"
echo "3. 验证安装是否成功"
```

## 如果找不到appid和appsecret

### 方法1：查看管理后台URL

在管理后台，查看应用详情页面的URL，可能包含应用ID。

### 方法2：查看"添加主机"对话框

在管理后台点击"添加主机"，选择"Java 服务器"，查看示例命令中的`appid`和`appsecret`。

### 方法3：使用应用名称

如果实在找不到，可以尝试：
1. 使用应用名称 `zhinengtiyingyong` 作为appid
2. 或者联系OpenRASP管理员获取

## 注意事项

1. **安装路径**：`-install`参数指向Spring Boot项目的根目录
2. **rasp.jar位置**：安装后，使用应用目录下的`rasp/rasp.jar`，而不是原始安装目录的
3. **配置文件**：安装后，配置文件在应用目录下的`rasp/conf/openrasp.yml`
4. **重启应用**：安装后必须重启应用才能生效

