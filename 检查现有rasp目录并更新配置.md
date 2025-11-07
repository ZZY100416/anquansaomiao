# 检查现有rasp目录并更新配置

## 检查应用目录下的rasp目录

```bash
# 检查应用目录下是否已有rasp目录
ls -la ~/projects/bailianyingyong/chatbotAi/rasp/ 2>/dev/null && echo "✓ rasp目录已存在" || echo "✗ rasp目录不存在"

# 如果存在，查看其内容
if [ -d ~/projects/bailianyingyong/chatbotAi/rasp ]; then
    echo "=== rasp目录内容 ==="
    ls -la ~/projects/bailianyingyong/chatbotAi/rasp/
    echo ""
    echo "=== conf目录内容 ==="
    ls -la ~/projects/bailianyingyong/chatbotAi/rasp/conf/ 2>/dev/null || echo "conf目录不存在"
    echo ""
    echo "=== 当前配置文件 ==="
    cat ~/projects/bailianyingyong/chatbotAi/rasp/conf/openrasp.yml 2>/dev/null | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret" || echo "配置文件不存在或没有cloud配置"
fi
```

## 如果rasp目录已存在

### 方案1：更新现有配置文件

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 备份现有配置文件
if [ -f rasp/conf/openrasp.yml ]; then
    cp rasp/conf/openrasp.yml rasp/conf/openrasp.yml.bak
    echo "✓ 配置文件已备份"
fi

# 更新配置文件
python3 << 'EOF'
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
EOF

# 验证配置
echo ""
echo "=== 更新后的配置 ==="
cat rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
```

### 方案2：确保rasp.jar存在

```bash
# 检查rasp.jar是否存在
if [ ! -f ~/projects/bailianyingyong/chatbotAi/rasp/rasp.jar ]; then
    echo "rasp.jar不存在，正在复制..."
    cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar ~/projects/bailianyingyong/chatbotAi/rasp/
    cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp-engine.jar ~/projects/bailianyingyong/chatbotAi/rasp/
    echo "✓ rasp.jar已复制"
else
    echo "✓ rasp.jar已存在"
fi
```

## 完整检查和更新脚本

```bash
#!/bin/bash

echo "=== 检查并更新现有rasp目录 ==="
echo ""

APP_RASP_DIR="$HOME/projects/bailianyingyong/chatbotAi/rasp"

# 1. 检查rasp目录是否存在
if [ ! -d "$APP_RASP_DIR" ]; then
    echo "✗ rasp目录不存在，需要创建"
    echo "请运行手动配置脚本"
    exit 1
fi

echo "✓ rasp目录已存在"
echo ""

# 2. 检查rasp.jar
echo "步骤1: 检查rasp.jar"
if [ ! -f "$APP_RASP_DIR/rasp.jar" ]; then
    echo "  rasp.jar不存在，正在复制..."
    cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar "$APP_RASP_DIR/"
    cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp-engine.jar "$APP_RASP_DIR/"
    echo "  ✓ rasp.jar已复制"
else
    echo "  ✓ rasp.jar已存在"
fi
echo ""

# 3. 检查配置文件
echo "步骤2: 检查配置文件"
if [ ! -f "$APP_RASP_DIR/conf/openrasp.yml" ]; then
    echo "  配置文件不存在，正在创建..."
    mkdir -p "$APP_RASP_DIR/conf"
    cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml "$APP_RASP_DIR/conf/"
    echo "  ✓ 配置文件已创建"
else
    echo "  ✓ 配置文件已存在"
    # 备份
    cp "$APP_RASP_DIR/conf/openrasp.yml" "$APP_RASP_DIR/conf/openrasp.yml.bak"
    echo "  ✓ 配置文件已备份"
fi
echo ""

# 4. 更新配置文件
echo "步骤3: 更新配置文件"
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

print("  ✓ 配置文件已更新")
PYTHON_SCRIPT

echo ""

# 5. 验证配置
echo "步骤4: 验证配置"
cat "$APP_RASP_DIR/conf/openrasp.yml" | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
echo ""

echo "=== 更新完成 ==="
echo ""
echo "下一步：重启应用"
```

## 重启应用

更新配置后，重启应用：

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

