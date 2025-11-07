# 解决Java版本问题

## 问题分析

错误信息：`error: release version 17 not supported`

**原因**：项目配置需要Java 17，但系统安装的是Java 21。虽然Java 21向后兼容，但Maven编译器插件可能配置了特定的Java版本。

## 解决方案

### 方案1：安装Java 17（推荐，如果项目必须使用Java 17）

```bash
# 安装Java 17
sudo apt update
sudo apt install -y openjdk-17-jdk

# 查看已安装的Java版本
update-alternatives --list java

# 切换Java版本（如果需要）
sudo update-alternatives --config java
# 选择Java 17

# 验证
java -version
# 应该显示：openjdk version "17.x.x"

# 设置JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 验证Maven使用的Java版本
mvn -version
```

### 方案2：修改项目配置使用Java 21（如果项目可以升级）

```bash
cd ~/projects/bailianyingyong/chatbotAi

# 查看pom.xml中的Java版本配置
grep -A 5 "<maven.compiler" pom.xml
# 或
cat pom.xml | grep -E "java.version|maven.compiler|source|target"

# 修改pom.xml，将Java版本从17改为21
# 找到类似这样的配置：
# <maven.compiler.source>17</maven.compiler.source>
# <maven.compiler.target>17</maven.compiler.target>
# 改为：
# <maven.compiler.source>21</maven.compiler.source>
# <maven.compiler.target>21</maven.compiler.target>
```

## 快速修复（推荐方案1）

```bash
# 1. 安装Java 17
sudo apt install -y openjdk-17-jdk

# 2. 设置JAVA_HOME（临时，当前会话）
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 3. 验证
java -version
mvn -version

# 4. 重新编译
cd ~/projects/bailianyingyong/chatbotAi
mvn clean compile
```

## 永久设置Java版本

```bash
# 编辑 ~/.bashrc 或 ~/.profile
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc

# 重新加载
source ~/.bashrc

# 验证
java -version
```

## 如果两个版本都需要

可以同时安装Java 17和Java 21，然后使用`update-alternatives`切换：

```bash
# 安装Java 17
sudo apt install -y openjdk-17-jdk

# 配置alternatives
sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-17-openjdk-amd64/bin/java 1
sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-21-openjdk-amd64/bin/java 2

# 切换版本
sudo update-alternatives --config java
# 选择Java 17（输入1）

# 验证
java -version
```

## 下一步

解决Java版本问题后：

1. **重新编译项目**：
   ```bash
   cd ~/projects/bailianyingyong/chatbotAi
   mvn clean compile
   ```

2. **如果编译成功，继续安装OpenRASP**：
   ```bash
   # 下载OpenRASP Agent
   cd /opt
   sudo wget https://github.com/baidu/openrasp/releases/download/v1.3.0/rasp-java.tar.gz
   sudo tar -xzf rasp-java.tar.gz
   sudo chown -R $USER:$USER /opt/rasp-java
   ```

3. **启动应用（带OpenRASP）**：
   ```bash
   cd ~/projects/bailianyingyong/chatbotAi
   export JAVA_OPTS="-javaagent:/opt/rasp-java/rasp.jar"
   export RASP_APP_ID=bailianyingyong-backend
   export RASP_BACKEND_URL=http://192.168.203.141:8086
   mvn spring-boot:run
   ```

