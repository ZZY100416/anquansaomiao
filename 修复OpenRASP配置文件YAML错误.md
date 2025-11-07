# 修复OpenRASP配置文件YAML格式错误

## 问题

启动日志显示YAML解析错误：
```
while parsing a block mapping
 in 'reader', line 47, column 1:
    hooks.ignore: http_output
    ^
expected <block end>, but found '<block mapping start>'
 in 'reader', line 72, column 2:
     cloud.enable: true
     ^
```

这说明`openrasp.yml`文件的YAML格式有问题，特别是第47行和第72行之间的缩进或结构不正确。

## 解决方案

### 步骤1：查看配置文件的结构

```bash
# 查看第47行附近的内容
sed -n '40,80p' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
```

### 步骤2：检查YAML格式

YAML对缩进非常敏感，`cloud`配置应该与`hooks`等配置在同一层级。

### 步骤3：修复YAML格式

```bash
# 备份配置文件
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml.bak2

# 使用Python脚本修复YAML格式
python3 << 'EOF'
import re

config_file = '/home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml'

# 读取文件
with open(config_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修复cloud配置的缩进
fixed_lines = []
for i, line in enumerate(lines, 1):
    # 如果是cloud配置行，确保缩进正确（应该是顶格，没有前导空格）
    if re.match(r'^\s*cloud\.', line):
        # 移除前导空格，确保顶格
        fixed_lines.append(re.sub(r'^\s+', '', line))
    else:
        fixed_lines.append(line)

# 写回文件
with open(config_file, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✓ YAML格式已修复")
EOF
```

### 步骤4：验证YAML格式

```bash
# 使用Python验证YAML格式
python3 << 'EOF'
import yaml

config_file = '/home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml'

try:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print("✓ YAML格式正确")
    print(f"cloud.enable: {config.get('cloud', {}).get('enable', 'N/A')}")
    print(f"cloud.backend_url: {config.get('cloud', {}).get('backend_url', 'N/A')}")
    print(f"cloud.app_id: {config.get('cloud', {}).get('app_id', 'N/A')}")
except yaml.YAMLError as e:
    print(f"✗ YAML格式错误: {e}")
EOF
```

### 步骤5：如果Python验证失败，手动修复

如果YAML验证仍然失败，需要手动检查并修复：

```bash
# 查看cloud配置部分
sed -n '70,75p' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml

# 手动编辑
nano /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
```

确保：
1. `cloud.enable: true` 顶格（没有前导空格）
2. `cloud.backend_url: http://192.168.203.141:8086` 顶格
3. `cloud.app_id: zhinengtiyingyong` 顶格
4. 这些行之间没有空行或格式问题

## 完整修复脚本

```bash
#!/bin/bash

echo "=== 修复OpenRASP配置文件YAML格式 ==="
echo ""

# 1. 备份
echo "步骤1: 备份配置文件"
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml.bak2
echo "✓ 已备份"
echo ""

# 2. 查看问题区域
echo "步骤2: 查看问题区域（第40-80行）"
sed -n '40,80p' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
echo ""

# 3. 修复cloud配置的缩进
echo "步骤3: 修复cloud配置的缩进"
python3 << 'PYTHON_SCRIPT'
import re

config_file = '/home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml'

# 读取文件
with open(config_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修复cloud配置的缩进（确保顶格）
fixed_lines = []
for line in lines:
    # 如果是cloud配置行，确保顶格
    if re.match(r'^\s+cloud\.', line):
        # 移除前导空格
        fixed_lines.append(re.sub(r'^\s+', '', line))
    else:
        fixed_lines.append(line)

# 写回文件
with open(config_file, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✓ cloud配置缩进已修复")
PYTHON_SCRIPT

# 4. 验证YAML格式
echo ""
echo "步骤4: 验证YAML格式"
python3 << 'PYTHON_SCRIPT'
import yaml

config_file = '/home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml'

try:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print("✓ YAML格式正确")
    if 'cloud' in config:
        print(f"  cloud.enable: {config['cloud'].get('enable', 'N/A')}")
        print(f"  cloud.backend_url: {config['cloud'].get('backend_url', 'N/A')}")
        print(f"  cloud.app_id: {config['cloud'].get('app_id', 'N/A')}")
    else:
        print("  ⚠ cloud配置未找到")
except yaml.YAMLError as e:
    print(f"✗ YAML格式错误: {e}")
    print("  请手动检查配置文件")
except Exception as e:
    print(f"✗ 错误: {e}")
PYTHON_SCRIPT

echo ""
echo "=== 修复完成 ==="
echo ""
echo "如果YAML格式正确，请重启应用"
```

## 重启应用

修复YAML格式后，重启应用：

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 停止应用
pkill -f "spring-boot:run"
sleep 2

# 启动应用
export MAVEN_OPTS="-javaagent:/home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar \
--add-opens=java.base/jdk.internal.loader=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.lang=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED"

mvn spring-boot:run
```

启动后，应该不再看到YAML解析错误，并且应该能看到OpenRASP连接到管理后台的日志。

