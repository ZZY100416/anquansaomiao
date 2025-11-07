# 正确修改OpenRASP配置文件

## 问题

sed命令执行后，配置仍然没有改变，说明命令可能没有匹配到正确的格式。

## 解决方案

### 步骤1：查看实际配置文件内容

```bash
# 查看cloud相关的配置行（包括注释和实际内容）
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -A 2 -B 2 "cloud"
```

### 步骤2：使用更精确的sed命令

如果配置行前面有空格或制表符，需要匹配：

```bash
# 方法1：匹配可能的前导空格
sed -i 's/^[[:space:]]*#cloud.enable: true/cloud.enable: true/' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
sed -i 's|^[[:space:]]*#cloud.backend_url: http://XXX|cloud.backend_url: http://192.168.203.141:8086|' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
sed -i 's/^[[:space:]]*#cloud.app_id: XXX/cloud.app_id: zhinengtiyingyong/' /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
```

### 步骤3：直接编辑文件（推荐）

如果sed命令仍然不工作，直接编辑文件：

```bash
# 使用nano编辑器
nano /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml
```

需要修改的内容：
1. 找到 `#cloud.enable: true`，删除前面的 `#`，改为 `cloud.enable: true`
2. 找到 `#cloud.backend_url: http://XXX`，删除前面的 `#`，改为 `cloud.backend_url: http://192.168.203.141:8086`
3. 找到 `cloud.app_id: XXX`，改为 `cloud.app_id: zhinengtiyingyong`

保存：`Ctrl+O`，回车，`Ctrl+X`

### 步骤4：使用Python脚本修改（最可靠）

```bash
# 创建Python脚本
cat > /tmp/fix_openrasp_config.py << 'EOF'
#!/usr/bin/env python3
import re

config_file = '/home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml'

# 读取文件
with open(config_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 修改配置
# 取消注释 cloud.enable
content = re.sub(r'^(\s*)#cloud\.enable:\s*true', r'\1cloud.enable: true', content, flags=re.MULTILINE)

# 取消注释并设置 cloud.backend_url
content = re.sub(r'^(\s*)#cloud\.backend_url:\s*http://XXX', r'\1cloud.backend_url: http://192.168.203.141:8086', content, flags=re.MULTILINE)

# 设置 cloud.app_id
content = re.sub(r'^(\s*)cloud\.app_id:\s*XXX', r'\1cloud.app_id: zhinengtiyingyong', content, flags=re.MULTILINE)

# 写回文件
with open(config_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ 配置文件已修改")
EOF

# 执行脚本
python3 /tmp/fix_openrasp_config.py

# 验证修改
echo "=== 修改后的配置 ==="
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id"
```

## 完整修复脚本

```bash
#!/bin/bash

echo "=== 修复OpenRASP配置文件 ==="
echo ""

# 1. 备份
echo "步骤1: 备份配置文件"
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml.bak
echo "✓ 已备份"
echo ""

# 2. 查看当前配置
echo "步骤2: 查看当前配置"
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id"
echo ""

# 3. 使用Python脚本修改
echo "步骤3: 使用Python脚本修改配置"
python3 << 'PYTHON_SCRIPT'
import re

config_file = '/home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml'

# 读取文件
with open(config_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 修改配置
# 取消注释 cloud.enable
content = re.sub(r'^(\s*)#cloud\.enable:\s*true', r'\1cloud.enable: true', content, flags=re.MULTILINE)

# 取消注释并设置 cloud.backend_url
content = re.sub(r'^(\s*)#cloud\.backend_url:\s*http://XXX', r'\1cloud.backend_url: http://192.168.203.141:8086', content, flags=re.MULTILINE)

# 设置 cloud.app_id（可能被注释也可能没被注释）
content = re.sub(r'^(\s*)#?cloud\.app_id:\s*XXX', r'\1cloud.app_id: zhinengtiyingyong', content, flags=re.MULTILINE)

# 写回文件
with open(config_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ 配置文件已修改")
PYTHON_SCRIPT

# 4. 验证修改
echo ""
echo "步骤4: 验证修改后的配置"
cat /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id"
echo ""

echo "=== 配置修改完成 ==="
```

