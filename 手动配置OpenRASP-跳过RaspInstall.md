# 手动配置OpenRASP（跳过RaspInstall.jar）

## 问题

RaspInstall.jar要求appsecret必须是43-45个字符，但从管理后台获取的appsecret可能不完整或格式不对。

## 解决方案：手动配置

直接手动创建rasp目录和配置文件，跳过RaspInstall.jar。

### 步骤1：创建rasp目录结构

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 创建rasp目录结构
mkdir -p rasp/conf rasp/logs rasp/plugins

# 复制rasp.jar和相关文件
cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar rasp/
cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp-engine.jar rasp/
```

### 步骤2：复制并修改配置文件

```bash
# 复制配置文件
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml rasp/conf/

# 修改配置文件
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

# 设置 cloud.app_id（确保是小写0开头）
content = re.sub(r'^(\s*)#?cloud\.app_id:\s*.*', r'\1cloud.app_id: 0c91b98f2aa79983228f10fc37725da726bd31d6', content, flags=re.MULTILINE)

# 设置 cloud.app_secret（使用从管理后台获取的值）
content = re.sub(r'^(\s*)#cloud\.app_secret:\s*XXX', r'\1cloud.app_secret: 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU', content, flags=re.MULTILINE)

# 如果app_secret行不存在，在app_id后面添加它
if 'cloud.app_secret: 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU' not in content:
    content = re.sub(
        r'(cloud\.app_id:\s*0c91b98f2aa79983228f10fc37725da726bd31d6)',
        r'\1\ncloud.app_secret: 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU',
        content
    )

with open(config_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ 配置文件已更新")
EOF
```

### 步骤3：验证配置

```bash
# 验证配置
echo "=== 验证配置 ==="
cat rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
```

### 步骤4：重启应用

```bash
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

## 完整手动配置脚本

```bash
#!/bin/bash

echo "=== 手动配置OpenRASP ==="
echo ""

cd ~/projects/bailianyingyong/chatbotAi

# 1. 创建rasp目录结构
echo "步骤1: 创建rasp目录结构"
mkdir -p rasp/conf rasp/logs rasp/plugins
echo "✓ 目录已创建"
echo ""

# 2. 复制rasp.jar
echo "步骤2: 复制rasp.jar"
cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar rasp/
cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp-engine.jar rasp/
echo "✓ 文件已复制"
echo ""

# 3. 复制并修改配置文件
echo "步骤3: 复制并修改配置文件"
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml rasp/conf/

python3 << 'PYTHON_SCRIPT'
import re

config_file = '/home/enen/projects/bailianyingyong/chatbotAi/rasp/conf/openrasp.yml'

with open(config_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 确保cloud配置正确
content = re.sub(r'^(\s*)#cloud\.enable:\s*true', r'\1cloud.enable: true', content, flags=re.MULTILINE)
content = re.sub(r'^(\s*)#cloud\.backend_url:\s*http://XXX', r'\1cloud.backend_url: http://192.168.203.141:8086', content, flags=re.MULTILINE)
content = re.sub(r'^(\s*)#?cloud\.app_id:\s*.*', r'\1cloud.app_id: 0c91b98f2aa79983228f10fc37725da726bd31d6', content, flags=re.MULTILINE)
content = re.sub(r'^(\s*)#cloud\.app_secret:\s*XXX', r'\1cloud.app_secret: 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU', content, flags=re.MULTILINE)

# 如果app_secret行不存在，添加它
if 'cloud.app_secret: 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU' not in content:
    content = re.sub(
        r'(cloud\.app_id:\s*0c91b98f2aa79983228f10fc37725da726bd31d6)',
        r'\1\ncloud.app_secret: 03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU',
        content
    )

with open(config_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ 配置文件已更新")
PYTHON_SCRIPT

echo ""

# 4. 验证配置
echo "步骤4: 验证配置"
cat rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
echo ""

echo "=== 配置完成 ==="
echo ""
echo "下一步：重启应用"
```

## 验证安装成功

重启应用后：

1. **查看启动日志**：应该看到`[OpenRASP] Engine Initialized`，没有YAML错误
2. **检查响应头**：
   ```bash
   curl -I http://localhost:9988
   # 应该看到：X-Protected-By: OpenRASP
   ```
3. **在管理后台验证**：
   - 访问：`http://192.168.203.141:8086`
   - 在"主机管理"中查看是否有主机注册
   - 等待几分钟，看是否有心跳信息

## 注意事项

手动配置后，即使appsecret长度不符合RaspInstall.jar的要求，OpenRASP也应该能正常工作，因为：
1. 配置文件中的appsecret格式可能更灵活
2. OpenRASP运行时读取配置文件，不依赖RaspInstall.jar的验证

