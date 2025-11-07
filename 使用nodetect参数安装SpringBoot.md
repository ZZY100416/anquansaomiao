# 使用-nodetect参数安装Spring Boot应用

## 错误信息

```
[ERROR 10004] Unable to determine application server type in: /home/enen/projects/bailianyingyong/chatbotAi
```

## 原因

RaspInstall.jar无法自动检测Spring Boot应用类型。它支持：
- Tomcat
- Resin
- Weblogic
- JbossEAP
- Wildfly
- JBoss 4-6

但Spring Boot不在这个列表中。

## 解决方案：使用-nodetect参数

根据OpenRASP官方文档，对于Spring Boot应用，需要使用`-nodetect`参数跳过自动检测：

```bash
cd /home/enen/openrasp/rasp-2023-03-31

# 使用-nodetect参数跳过自动检测
java -jar RaspInstall.jar \
  -nodetect \
  -heartbeat 90 \
  -appid 0c91b98f2aa79983228f10fc37725da726bd31d6 \
  -appsecret "03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU" \
  -backendurl http://192.168.203.141:8086/ \
  -install ~/projects/bailianyingyong/chatbotAi
```

**重要参数说明**：
- `-nodetect`：不自动检测服务器类型（Spring Boot需要）
- `-appid`：应用ID（注意第一个字符是小写`0`，不是大写`O`）
- `-appsecret`：应用密钥（用引号包裹，因为包含`@`字符）

## 验证安装

```bash
# 检查是否创建了rasp目录
ls -la ~/projects/bailianyingyong/chatbotAi/rasp/

# 检查配置文件
cat ~/projects/bailianyingyong/chatbotAi/rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
```

## 重启应用

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

## 完整安装命令

```bash
cd /home/enen/openrasp/rasp-2023-03-31

java -jar RaspInstall.jar \
  -nodetect \
  -heartbeat 90 \
  -appid 0c91b98f2aa79983228f10fc37725da726bd31d6 \
  -appsecret "03HUqrDFqauBGqsHhkp@yxyMc871U83NuIGxQBoStIU" \
  -backendurl http://192.168.203.141:8086/ \
  -install ~/projects/bailianyingyong/chatbotAi
```

## 如果仍然失败

如果使用`-nodetect`仍然失败，可以手动配置（不使用RaspInstall.jar）：

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 1. 创建rasp目录结构
mkdir -p rasp/conf rasp/logs rasp/plugins

# 2. 复制rasp.jar
cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp.jar rasp/
cp /home/enen/openrasp/rasp-2023-03-31/rasp/rasp-engine.jar rasp/

# 3. 复制并修改配置文件
cp /home/enen/openrasp/rasp-2023-03-31/rasp/conf/openrasp.yml rasp/conf/

# 4. 修改配置文件
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

# 5. 验证配置
cat rasp/conf/openrasp.yml | grep -E "cloud.enable|cloud.backend_url|cloud.app_id|cloud.app_secret"
```

