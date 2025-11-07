# 检查项目运行和OpenRASP配置

## 第一步：检查OpenRASP管理后台是否运行

你的Ubuntu上已经有OpenRASP管理后台，需要确认它是否正在运行：

```bash
# 检查OpenRASP管理后台是否运行
curl http://192.168.203.141:8086

# 或检查端口是否开放
netstat -tlnp | grep 8086
# 或
ss -tlnp | grep 8086

# 如果使用Docker运行
docker ps | grep openrasp
```

**如果OpenRASP管理后台已经在运行，你不需要重新安装！** 只需要在你的项目中安装OpenRASP Agent并配置连接即可。

## 第二步：检查项目是否能在Ubuntu上运行

### 1. 检查项目结构

```bash
cd ~/projects/bailianzhinengtiyingyong

# 查看项目结构
ls -la

# 检查是否有package.json（Node.js项目）
ls package.json

# 检查是否有pom.xml（Java项目）
find . -name "pom.xml"

# 检查是否有requirements.txt（Python项目）
find . -name "requirements.txt"
```

### 2. 根据项目类型检查依赖

#### 如果是Node.js项目

```bash
# 检查Node.js是否安装
node --version
npm --version

# 检查项目依赖
cat package.json

# 尝试安装依赖（不运行）
npm install --dry-run
```

#### 如果是Java项目

```bash
# 检查Java是否安装
java -version
mvn --version

# 检查项目配置
cat pom.xml | head -20

# 尝试编译（不运行）
mvn compile
```

#### 如果是Python项目

```bash
# 检查Python是否安装
python3 --version
pip3 --version

# 检查项目依赖
cat requirements.txt

# 尝试安装依赖（不运行）
pip3 install --dry-run -r requirements.txt
```

### 3. 检查启动脚本或配置文件

```bash
# 查找启动脚本
find . -name "*.sh"
find . -name "start.sh"
find . -name "run.sh"

# 查找Docker配置
find . -name "Dockerfile"
find . -name "docker-compose.yml"

# 查找配置文件
find . -name "application.properties"
find . -name "application.yml"
find . -name "config.js"
find . -name ".env"
```

## 第三步：如果项目能运行，安装OpenRASP Agent

### 方案A：Java项目

```bash
# 1. 下载OpenRASP Java Agent（如果还没下载）
cd /opt
sudo wget https://github.com/baidu/openrasp/releases/download/v1.3.0/rasp-java.tar.gz
sudo tar -xzf rasp-java.tar.gz
sudo chown -R $USER:$USER /opt/rasp-java

# 2. 回到项目目录
cd ~/projects/bailianzhinengtiyingyong

# 3. 创建启动脚本（带OpenRASP）
cat > start-with-rasp.sh << 'EOF'
#!/bin/bash
export JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
export RASP_APP_ID=bailianzhinengtiyingyong
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 根据你的项目启动方式选择：
# 方式1：Maven启动
# mvn spring-boot:run

# 方式2：运行jar包
# java $JAVA_OPTS -jar target/your-app.jar

# 方式3：其他启动方式
# 在这里添加你的启动命令
EOF

chmod +x start-with-rasp.sh
```

### 方案B：Node.js项目

```bash
# 1. 安装OpenRASP插件
cd ~/projects/bailianzhinengtiyingyong
npm install openrasp

# 2. 修改应用入口文件（app.js或server.js或index.js）
# 在文件最开头添加：
cat >> app.js << 'EOF'

// OpenRASP配置（添加到文件最开头）
const openrasp = require('openrasp');
openrasp.start({
    app_id: 'bailianzhinengtiyingyong',
    backend_url: 'http://192.168.203.141:8086'
});

EOF
```

### 方案C：Python项目

```bash
# 1. 安装OpenRASP Python插件
cd ~/projects/bailianzhinengtiyingyong
pip3 install openrasp

# 2. 修改应用入口文件
# 在文件最开头添加：
cat >> app.py << 'EOF'

# OpenRASP配置（添加到文件最开头）
import openrasp
openrasp.start(
    app_id='bailianzhinengtiyingyong',
    backend_url='http://192.168.203.141:8086'
)

EOF
```

## 第四步：测试项目运行

### 1. 先测试项目能否正常运行（不带OpenRASP）

```bash
cd ~/projects/bailianzhinengtiyingyong

# 根据项目类型启动
# Node.js: npm start 或 node app.js
# Java: mvn spring-boot:run 或 java -jar target/*.jar
# Python: python3 app.py 或 flask run
```

### 2. 如果项目能正常运行，再测试带OpenRASP

```bash
# 使用带OpenRASP的启动方式
# Java: ./start-with-rasp.sh
# Node.js/Python: 已经修改了代码，直接启动即可
```

### 3. 验证OpenRASP连接

1. 启动应用后，访问OpenRASP管理后台：`http://192.168.203.141:8086`
2. 登录（用户名：`openrasp`，密码：`zzy100416`）
3. 查看"应用列表"，应该能看到你的应用（`app_id: bailianzhinengtiyingyong`）

## 快速检查清单

在Ubuntu上执行以下命令，把结果告诉我：

```bash
# 1. 检查OpenRASP管理后台
echo "=== OpenRASP管理后台状态 ==="
curl -s http://192.168.203.141:8086 | head -5
echo ""

# 2. 检查项目结构
echo "=== 项目结构 ==="
cd ~/projects/bailianzhinengtiyingyong
ls -la
echo ""

# 3. 检查项目类型
echo "=== 项目类型 ==="
[ -f package.json ] && echo "✓ 发现Node.js项目 (package.json)"
[ -f pom.xml ] && echo "✓ 发现Java项目 (pom.xml)"
[ -f requirements.txt ] && echo "✓ 发现Python项目 (requirements.txt)"
find . -maxdepth 2 -name "pom.xml" && echo "✓ 发现Java子项目"
echo ""

# 4. 检查运行环境
echo "=== 运行环境 ==="
node --version 2>/dev/null && echo "✓ Node.js已安装" || echo "✗ Node.js未安装"
java -version 2>&1 | head -1 && echo "✓ Java已安装" || echo "✗ Java未安装"
python3 --version 2>/dev/null && echo "✓ Python3已安装" || echo "✗ Python3未安装"
mvn --version 2>&1 | head -1 && echo "✓ Maven已安装" || echo "✗ Maven未安装"
echo ""

# 5. 检查启动文件
echo "=== 启动文件 ==="
find . -maxdepth 2 -name "*.sh" | head -5
find . -maxdepth 2 -name "Dockerfile" | head -5
find . -maxdepth 2 -name "docker-compose.yml" | head -5
```

## 常见问题

### Q1: OpenRASP管理后台已经运行，还需要做什么？

**A**: 只需要：
1. 在你的项目中安装OpenRASP Agent（根据项目类型）
2. 配置连接信息（`app_id` 和 `backend_url`）
3. 启动应用时加载Agent

**不需要重新安装OpenRASP管理后台！**

### Q2: 项目clone下来后，不知道能不能运行？

**A**: 按照上面的检查清单执行，然后告诉我结果，我会帮你：
1. 判断项目类型
2. 检查依赖是否满足
3. 提供具体的运行步骤

### Q3: 项目有多个服务，怎么处理？

**A**: 为每个服务：
1. 使用不同的 `app_id`（例如：`bailianzhinengtiyingyong-api`、`bailianzhinengtiyingyong-web`）
2. 分别安装OpenRASP Agent
3. 分别启动

### Q4: 项目在Docker中运行，怎么配置？

**A**: 在Dockerfile中添加OpenRASP Agent：

```dockerfile
# 复制OpenRASP Agent
COPY /opt/rasp-java /opt/rasp-java

# 设置环境变量
ENV JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
ENV RASP_APP_ID=bailianzhinengtiyingyong
ENV RASP_BACKEND_URL=http://192.168.203.141:8086
```

## 下一步

1. **执行检查清单**：在Ubuntu上运行上面的检查命令
2. **告诉我结果**：把输出结果发给我
3. **我会帮你**：
   - 判断项目类型
   - 检查是否能运行
   - 提供具体的OpenRASP安装和配置步骤

