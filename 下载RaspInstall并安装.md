# 下载RaspInstall并安装OpenRASP

## 从管理后台获取的信息

从"添加主机"对话框中可以看到：
- **appid**: `0c91b98f2aa79983228f10fc37725da726bd31d6`
- **appsecret**: `03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU`
- **backendurl**: `http://192.168.203.141:8086/`

## 方案1：下载安装包并使用RaspInstall.jar（推荐）

### 步骤1：下载OpenRASP安装包

```bash
# 下载OpenRASP Java安装包
cd /tmp
curl https://packages.baidu.com/app/openrasp/release/1.3.7/rasp-java.tar.gz -o rasp-java.tar.gz

# 解压
tar -xvf rasp-java.tar.gz

# 进入解压目录
cd rasp-*

# 查看RaspInstall.jar
ls -la RaspInstall.jar
```

### 步骤2：使用RaspInstall.jar安装

```bash
# 使用从管理后台获取的appid和appsecret
java -jar RaspInstall.jar \
  -heartbeat 90 \
  -appid 0c91b98f2aa79983228f10fc37725da726bd31d6 \
  -appsecret 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU \
  -backendurl http://192.168.203.141:8086/ \
  -install ~/projects/bailianyingyong/chatbotAi
```

### 步骤3：验证安装

```bash
# 检查是否创建了rasp目录
ls -la ~/projects/bailianyingyong/chatbotAi/rasp/

# 检查配置文件
cat ~/projects/bailianyingyong/chatbotAi/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
```

## 方案2：手动配置（如果下载失败）

如果无法下载安装包，可以手动配置：

### 步骤1：在应用目录创建rasp目录结构

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 创建rasp目录结构
mkdir -p rasp/conf rasp/logs rasp/plugins

# 复制rasp.jar
cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar rasp/
cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp-engine.jar rasp/
```

### 步骤2：创建配置文件

```bash
# 复制配置文件
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml rasp/conf/

# 修改配置文件，添加app_secret
python3 << 'EOF'
import re

config_file = '/home/enen/projects/bailianyingyong/chatbotAi/rasp/conf/openrasp.yml'

with open(config_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 确保cloud配置正确
# 取消注释 cloud.enable
content = re.sub(r'^(\s*)#cloud\.enable:\s*true', r'\1cloud.enable: true', content, flags=re.MULTILINE)

# 取消注释并设置 cloud.backend_url
content = re.sub(r'^(\s*)#cloud\.backend_url:\s*http://XXX', r'\1cloud.backend_url: http://192.168.203.141:8086', content, flags=re.MULTILINE)

# 设置 cloud.app_id
content = re.sub(r'^(\s*)#?cloud\.app_id:\s*.*', r'\1cloud.app_id: 0c91b98f2aa79983228f10fc37725da726bd31d6', content, flags=re.MULTILINE)

# 取消注释并设置 cloud.app_secret
content = re.sub(r'^(\s*)#cloud\.app_secret:\s*XXX', r'\1cloud.app_secret: 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU', content, flags=re.MULTILINE)

# 如果app_secret行不存在，添加它
if 'cloud.app_secret:' not in content or 'cloud.app_secret: XXX' in content:
    # 在app_id后面添加app_secret
    content = re.sub(
        r'(cloud\.app_id:\s*0c91b98f2aa79983228f10fc37725da726bd31d6)',
        r'\1\ncloud.app_secret: 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU',
        content
    )

with open(config_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ 配置文件已更新")
EOF

# 验证配置
cat rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
```

## 步骤3：配置启动参数

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止应用
pkill -f "spring-boot:run"
sleep 2

# 使用应用目录下的rasp.jar
export MAVEN_OPTS="-javaagent:/home/enen/projects/bailianyingyong/chatbotAi/rasp/rasp.jar \
--add-opens=java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.lang=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED"

# 启动应用
mvn spring-boot:run
```

## 完整安装脚本（方案1）

```bash
#!/bin/bash

echo "=== 下载并安装OpenRASP ==="
echo ""

# 1. 下载安装包
echo "步骤1: 下载OpenRASP安装包"
cd /tmp
if [ ! -f "rasp-java.tar.gz" ]; then
    curl https://packages.baidu.com/app/openrasp/release/1.3.7/rasp-java.tar.gz -o rasp-java.tar.gz
    if [ $? -eq 0 ]; then
        echo "✓ 下载成功"
    else
        echo "✗ 下载失败，请检查网络"
        exit 1
    fi
else
    echo "✓ 安装包已存在"
fi

# 2. 解压
echo ""
echo "步骤2: 解压安装包"
if [ ! -d "rasp-1.3.7" ]; then
    tar -xvf rasp-java.tar.gz
    echo "✓ 解压成功"
else
    echo "✓ 已解压"
fi

# 3. 使用RaspInstall.jar安装
echo ""
echo "步骤3: 使用RaspInstall.jar安装"
cd rasp-1.3.7

java -jar RaspInstall.jar \
  -heartbeat 90 \
  -appid 0c91b98f2aa79983228f10fc37725da726bd31d6 \
  -appsecret 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU \
  -backendurl http://192.168.203.141:8086/ \
  -install ~/projects/bailianyingyong/chatbotAi

if [ $? -eq 0 ]; then
    echo "✓ 安装成功"
else
    echo "✗ 安装失败"
    exit 1
fi

# 4. 验证安装
echo ""
echo "步骤4: 验证安装"
if [ -d "$HOME/projects/bailianyingyong/chatbotAi/rasp" ]; then
    echo "✓ rasp目录已创建"
    echo ""
    echo "配置内容："
    cat "$HOME/projects/bailianyingyong/chatbotAi/rasp/conf/openrasp.yml" | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret" || echo "未找到cloud配置"
else
    echo "✗ rasp目录未创建"
fi

echo ""
echo "=== 安装完成 ==="
echo "请重启应用以使配置生效"
```

## 验证安装成功

安装并重启应用后：

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

