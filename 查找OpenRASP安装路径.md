# 查找OpenRASP安装路径

## 快速查找命令

在Ubuntu上执行以下命令来查找OpenRASP的安装位置：

### 1. 查找OpenRASP Java Agent

```bash
# 查找rasp.jar文件
find / -name "rasp.jar" 2>/dev/null

# 查找rasp-java目录
find / -type d -name "rasp-java" 2>/dev/null

# 查找包含"rasp"的目录
find /opt /usr/local /home -type d -name "*rasp*" 2>/dev/null

# 查找OpenRASP相关的文件
find /opt /usr/local -name "*rasp*" 2>/dev/null
```

### 2. 查找OpenRASP管理后台（Docker）

```bash
# 查找OpenRASP相关的Docker容器
docker ps -a | grep -i rasp

# 查找OpenRASP相关的Docker镜像
docker images | grep -i rasp

# 查找OpenRASP相关的Docker卷
docker volume ls | grep -i rasp
```

### 3. 查找OpenRASP配置文件

```bash
# 查找OpenRASP配置文件
find / -name "*rasp*.conf" -o -name "*rasp*.ini" -o -name "*rasp*.yml" 2>/dev/null

# 查找OpenRASP日志文件
find /var/log -name "*rasp*" 2>/dev/null

# 查找OpenRASP数据目录
find /var/lib -type d -name "*rasp*" 2>/dev/null
```

### 4. 检查常见安装位置

```bash
# 检查常见安装目录
echo "=== 检查常见安装位置 ==="
[ -d /opt/rasp-java ] && echo "✓ 找到: /opt/rasp-java" && ls -la /opt/rasp-java
[ -d /opt/openrasp ] && echo "✓ 找到: /opt/openrasp" && ls -la /opt/openrasp
[ -d /usr/local/rasp-java ] && echo "✓ 找到: /usr/local/rasp-java" && ls -la /usr/local/rasp-java
[ -d /usr/local/openrasp ] && echo "✓ 找到: /usr/local/openrasp" && ls -la /usr/local/openrasp
[ -d ~/rasp-java ] && echo "✓ 找到: ~/rasp-java" && ls -la ~/rasp-java
[ -d ~/openrasp ] && echo "✓ 找到: ~/openrasp" && ls -la ~/openrasp
```

### 5. 检查进程和端口

```bash
# 检查OpenRASP管理后台是否在运行（端口8086）
netstat -tlnp | grep 8086
# 或
ss -tlnp | grep 8086

# 检查OpenRASP相关进程
ps aux | grep -i rasp

# 检查Docker容器
docker ps | grep -i rasp
```

### 6. 检查环境变量

```bash
# 检查环境变量
env | grep -i rasp

# 检查bash历史记录（可能包含安装命令）
history | grep -i rasp | tail -20
```

## 一键查找脚本

执行以下脚本，自动查找OpenRASP的所有可能位置：

```bash
cat > find-openrasp.sh << 'EOF'
#!/bin/bash

echo "=== 查找OpenRASP安装路径 ==="
echo ""

echo "1. 查找rasp.jar文件："
find /opt /usr/local /home -name "rasp.jar" 2>/dev/null | head -5
echo ""

echo "2. 查找rasp-java目录："
find /opt /usr/local /home -type d -name "rasp-java" 2>/dev/null
echo ""

echo "3. 查找openrasp目录："
find /opt /usr/local /home -type d -name "*openrasp*" 2>/dev/null
echo ""

echo "4. 检查常见安装位置："
for dir in /opt/rasp-java /opt/openrasp /usr/local/rasp-java /usr/local/openrasp ~/rasp-java ~/openrasp; do
    if [ -d "$dir" ]; then
        echo "✓ 找到: $dir"
        ls -la "$dir" | head -5
        echo ""
    fi
done

echo "5. 检查Docker容器："
docker ps -a | grep -i rasp || echo "未找到OpenRASP Docker容器"
echo ""

echo "6. 检查端口8086（OpenRASP管理后台）："
netstat -tlnp 2>/dev/null | grep 8086 || ss -tlnp 2>/dev/null | grep 8086 || echo "端口8086未监听"
echo ""

echo "7. 检查OpenRASP进程："
ps aux | grep -i rasp | grep -v grep || echo "未找到OpenRASP进程"
echo ""

echo "8. 检查环境变量："
env | grep -i rasp || echo "未找到OpenRASP环境变量"
echo ""

echo "=== 查找完成 ==="
EOF

chmod +x find-openrasp.sh
./find-openrasp.sh
```

## 根据找到的路径使用OpenRASP

### 如果找到rasp.jar文件

假设找到的路径是 `/opt/rasp-java/rasp.jar` 或 `/usr/local/rasp-java/rasp.jar`：

```bash
# 记录路径
RASP_JAR_PATH=$(find /opt /usr/local /home -name "rasp.jar" 2>/dev/null | head -1)

if [ -n "$RASP_JAR_PATH" ]; then
    echo "找到OpenRASP Agent: $RASP_JAR_PATH"
    
    # 获取目录
    RASP_DIR=$(dirname "$RASP_JAR_PATH")
    echo "OpenRASP目录: $RASP_DIR"
    
    # 使用OpenRASP启动应用
    export JAVA_OPTS="-javaagent:$RASP_JAR_PATH"
    export RASP_APP_ID=bailianyingyong-backend
    export RASP_BACKEND_URL=http://192.168.203.141:8086
    
    echo "环境变量已设置："
    echo "JAVA_OPTS=$JAVA_OPTS"
    echo "RASP_APP_ID=$RASP_APP_ID"
    echo "RASP_BACKEND_URL=$RASP_BACKEND_URL"
else
    echo "未找到rasp.jar，可能需要重新安装"
fi
```

### 如果找到Docker容器

```bash
# 查看容器信息
docker ps -a | grep -i rasp

# 查看容器详细信息
docker inspect <container_name> | grep -A 10 "Mounts"

# 查看容器日志
docker logs <container_name>
```

## 常见安装位置

根据OpenRASP的安装方式，常见位置包括：

1. **手动安装**：
   - `/opt/rasp-java/rasp.jar`
   - `/usr/local/rasp-java/rasp.jar`
   - `~/rasp-java/rasp.jar`

2. **Docker安装**：
   - 容器名称通常包含 `openrasp` 或 `rasp`
   - 数据卷通常在 `/var/lib/docker/volumes/` 下

3. **管理后台**：
   - 通常运行在端口 `8086`
   - 如果是Docker，容器名可能是 `openrasp-cloud` 或类似

## 下一步

找到OpenRASP路径后：

1. **如果是Java Agent**：
   ```bash
   # 使用找到的路径
   export JAVA_OPTS="-javaagent:/找到的路径/rasp.jar"
   export RASP_APP_ID=bailianyingyong-backend
   export RASP_BACKEND_URL=http://192.168.203.141:8086
   ```

2. **如果是Docker容器**：
   ```bash
   # 查看容器状态
   docker ps | grep rasp
   
   # 如果容器未运行，启动它
   docker start <container_name>
   ```

3. **验证连接**：
   ```bash
   # 测试OpenRASP管理后台
   curl http://192.168.203.141:8086
   ```

