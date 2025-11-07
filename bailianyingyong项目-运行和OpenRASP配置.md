# bailianyingyong项目 - 运行和OpenRASP配置指南

## 项目结构分析

根据检查结果：
- **前端**：Node.js/React项目（`package.json`，项目名：`react-07`）
- **后端**：Java/Spring Boot项目（`chatbotAi/pom.xml`）
- **运行环境**：Node.js ✓、Java ✓、Python ✓、Maven ✗（需要安装）

## 第一步：安装Maven（Java项目需要）

```bash
# 安装Maven
sudo apt update
sudo apt install -y maven

# 验证安装
mvn --version
```

## 第二步：检查项目是否能运行

### 2.1 检查前端项目

```bash
cd ~/projects/bailianyingyong

# 查看package.json的启动脚本
cat package.json | grep -A 10 '"scripts"'

# 检查依赖是否已安装
ls node_modules 2>/dev/null && echo "依赖已安装" || echo "需要安装依赖"

# 如果需要，安装依赖
npm install
```

### 2.2 检查后端项目

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 查看pom.xml
cat pom.xml | head -30

# 尝试编译（不运行）
mvn clean compile

# 如果编译成功，尝试打包
mvn clean package -DskipTests
```

## 第三步：安装OpenRASP Agent

### 3.1 为Java后端安装OpenRASP Agent

```bash
# 1. 下载OpenRASP Java Agent
cd /opt
sudo wget https://github.com/baidu/openrasp/releases/download/v1.3.0/rasp-java.tar.gz
sudo tar -xzf rasp-java.tar.gz
sudo chown -R $USER:$USER /opt/rasp-java

# 验证安装
ls -la /opt/rasp-java/rasp.jar
```

### 3.2 为Node.js前端安装OpenRASP（可选）

**注意**：OpenRASP主要用于后端应用防护。如果前端只是静态页面或API调用，通常不需要OpenRASP。

如果前端有Node.js后端服务（如Express），可以安装：

```bash
cd ~/projects/bailianyingyong
npm install openrasp
```

## 第四步：配置和启动应用

### 4.1 启动Java后端（带OpenRASP）

#### 方式1：使用Maven启动（开发环境）

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 创建启动脚本
cat > start-with-rasp.sh << 'EOF'
#!/bin/bash
export JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
export RASP_APP_ID=bailianyingyong-backend
export RASP_BACKEND_URL=http://192.168.203.141:8086

echo "启动Java后端（带OpenRASP）..."
mvn spring-boot:run
EOF

chmod +x start-with-rasp.sh

# 启动
./start-with-rasp.sh
```

#### 方式2：运行jar包（生产环境）

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 先打包
mvn clean package -DskipTests

# 创建启动脚本
cat > start-jar-with-rasp.sh << 'EOF'
#!/bin/bash
export JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
export RASP_APP_ID=bailianyingyong-backend
export RASP_BACKEND_URL=http://192.168.203.141:8086

# 找到jar包
JAR_FILE=$(find target -name "*.jar" -not -name "*sources.jar" | head -1)
if [ -z "$JAR_FILE" ]; then
    echo "错误: 找不到jar包，请先运行 mvn clean package"
    exit 1
fi

echo "启动Java后端: $JAR_FILE"
java $JAVA_OPTS -jar $JAR_FILE
EOF

chmod +x start-jar-with-rasp.sh

# 启动
./start-jar-with-rasp.sh
```

### 4.2 启动Node.js前端

```bash
cd ~/projects/bailianyingyong

# 安装依赖（如果还没安装）
npm install

# 查看启动脚本
cat package.json | grep -A 5 '"scripts"'

# 启动前端（根据package.json中的scripts）
# 通常是以下之一：
npm start
# 或
npm run dev
# 或
npm run serve
```

**如果前端需要OpenRASP**（有Node.js后端服务），修改入口文件：

```bash
# 找到入口文件（通常是 src/index.js 或 src/main.js 或 app.js）
# 在文件最开头添加：
cat >> src/index.js << 'EOF'

// OpenRASP配置（添加到文件最开头）
const openrasp = require('openrasp');
openrasp.start({
    app_id: 'bailianyingyong-frontend',
    backend_url: 'http://192.168.203.141:8086'
});

EOF
```

## 第五步：验证OpenRASP连接

### 5.1 检查应用是否启动

```bash
# 检查Java后端端口（通常是8080或8081）
netstat -tlnp | grep -E ':(8080|8081|5000)'

# 检查Node.js前端端口（通常是3000）
netstat -tlnp | grep 3000
```

### 5.2 在OpenRASP管理后台查看

1. 访问OpenRASP管理后台：`http://192.168.203.141:8086`
2. 登录（用户名：`openrasp`，密码：`zzy100416`）
3. 查看"应用列表"或"应用管理"
4. 应该能看到：
   - `bailianyingyong-backend`（Java后端）
   - `bailianyingyong-frontend`（如果前端也安装了OpenRASP）

## 第六步：在统一安全扫描平台中查看事件

### 6.1 确保平台已配置

检查统一安全扫描平台的 `docker-compose.yml`：

```yaml
backend:
  environment:
    - OPENRASP_API_URL=http://192.168.203.141:8086
    - OPENRASP_USERNAME=openrasp
    - OPENRASP_PASSWORD=zzy100416
```

### 6.2 同步事件

1. 登录统一安全扫描平台
2. 进入"RASP事件"页面
3. 点击"同步事件"按钮
4. 在扫描配置中指定 `app_id`：
   ```json
   {
     "app_id": "bailianyingyong-backend"
   }
   ```

## 快速启动脚本

创建一键启动脚本：

```bash
cd ~/projects/bailianyingyong

# 创建启动脚本
cat > start-all.sh << 'EOF'
#!/bin/bash

echo "=== 启动bailianyingyong项目（带OpenRASP）==="

# 检查Maven
if ! command -v mvn &> /dev/null; then
    echo "错误: Maven未安装，请先运行: sudo apt install -y maven"
    exit 1
fi

# 检查OpenRASP Agent
if [ ! -f /opt/rasp-java/rasp.jar ]; then
    echo "错误: OpenRASP Agent未安装"
    echo "请运行: cd /opt && sudo wget https://github.com/baidu/openrasp/releases/download/v1.3.0/rasp-java.tar.gz && sudo tar -xzf rasp-java.tar.gz"
    exit 1
fi

# 启动Java后端（后台运行）
echo "启动Java后端..."
cd chatbotAi
export JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
export RASP_APP_ID=bailianyingyong-backend
export RASP_BACKEND_URL=http://192.168.203.141:8086
nohup mvn spring-boot:run > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Java后端已启动，PID: $BACKEND_PID，日志: backend.log"

# 等待后端启动
sleep 10

# 启动Node.js前端（后台运行）
echo "启动Node.js前端..."
cd ..
npm install > /dev/null 2>&1
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Node.js前端已启动，PID: $FRONTEND_PID，日志: frontend.log"

echo ""
echo "=== 启动完成 ==="
echo "后端PID: $BACKEND_PID"
echo "前端PID: $FRONTEND_PID"
echo "查看日志: tail -f backend.log 或 tail -f frontend.log"
echo "停止服务: kill $BACKEND_PID $FRONTEND_PID"
EOF

chmod +x start-all.sh
```

## 常见问题

### Q1: Maven安装失败？

**A**: 
```bash
# 如果apt安装失败，使用snap
sudo snap install maven --classic

# 或手动安装
wget https://dlcdn.apache.org/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.tar.gz
sudo tar -xzf apache-maven-3.9.9-bin.tar.gz -C /opt
sudo ln -s /opt/apache-maven-3.9.9 /opt/maven
export PATH=/opt/maven/bin:$PATH
```

### Q2: Java后端启动失败？

**A**: 检查：
1. 端口是否被占用：`netstat -tlnp | grep 8080`
2. 数据库是否配置正确
3. 查看日志：`tail -f backend.log`

### Q3: 前端启动失败？

**A**: 
1. 检查依赖：`npm install`
2. 检查端口：`netstat -tlnp | grep 3000`
3. 查看日志：`tail -f frontend.log`

### Q4: OpenRASP管理后台看不到应用？

**A**: 
1. 检查环境变量是否正确设置
2. 检查网络连接：`curl http://192.168.203.141:8086`
3. 查看应用日志，搜索"openrasp"或"rasp"
4. 确认应用已启动并运行一段时间

### Q5: 如何停止服务？

**A**: 
```bash
# 查找进程
ps aux | grep -E 'mvn|node|java.*bailian'

# 停止进程
pkill -f "spring-boot:run"
pkill -f "npm start"
# 或使用PID
kill <PID>
```

## 下一步操作

1. **安装Maven**：`sudo apt install -y maven`
2. **安装OpenRASP Agent**：按照第三步操作
3. **测试运行**：先不带OpenRASP运行，确认项目正常
4. **带OpenRASP运行**：使用启动脚本启动
5. **验证连接**：在OpenRASP管理后台查看应用
6. **同步事件**：在统一安全扫描平台中同步事件

## 检查清单

- [ ] Maven已安装
- [ ] OpenRASP Java Agent已下载
- [ ] Java后端能正常启动（不带OpenRASP）
- [ ] Node.js前端能正常启动
- [ ] Java后端能正常启动（带OpenRASP）
- [ ] 在OpenRASP管理后台能看到应用
- [ ] 在统一安全扫描平台中能同步事件

