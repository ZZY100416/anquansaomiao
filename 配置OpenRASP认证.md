# 配置OpenRASP认证

## 问题

从Network标签看到，OpenRASP API需要Cookie认证：
- `Cookie: RASP_AUTH_ID=c55cf235acfa64fca8bc0473c2a31c23`

## 解决方案

有两种方式配置认证：

### 方式1：直接配置Cookie（推荐，如果已有Cookie）

1. **获取Cookie值**
   - 在浏览器中登录OpenRASP管理后台
   - 打开开发者工具（F12）
   - 在Network标签中查看任意请求的Cookie
   - 复制 `RASP_AUTH_ID` 的值

2. **配置环境变量**
   
   在Ubuntu上创建 `.env` 文件（在项目根目录）：
   ```bash
   OPENRASP_API_URL=http://192.168.203.141:8086
   OPENRASP_AUTH_COOKIE=RASP_AUTH_ID=你的cookie值
   ```
   
   或者直接在 `docker-compose.yml` 中修改：
   ```yaml
   - OPENRASP_AUTH_COOKIE=RASP_AUTH_ID=c55cf235acfa64fca8bc0473c2a31c23
   ```

### 方式2：使用用户名密码自动登录

1. **配置用户名密码**
   
   在 `.env` 文件中：
   ```bash
   OPENRASP_API_URL=http://192.168.203.141:8086
   OPENRASP_USERNAME=你的用户名
   OPENRASP_PASSWORD=你的密码
   ```
   
   或者在 `docker-compose.yml` 中：
   ```yaml
   - OPENRASP_USERNAME=admin
   - OPENRASP_PASSWORD=你的密码
   ```

2. **代码会自动登录获取Cookie**

## 立即配置

### 快速配置（使用Cookie）

```bash
# 在Ubuntu上
cd ~/projects/anquansaomiao

# 编辑docker-compose.yml，找到backend的environment部分
# 添加：
# - OPENRASP_AUTH_COOKIE=RASP_AUTH_ID=你的cookie值

# 或者创建.env文件
cat > .env << EOF
OPENRASP_API_URL=http://192.168.203.141:8086
OPENRASP_AUTH_COOKIE=RASP_AUTH_ID=c55cf235acfa64fca8bc0473c2a31c23
EOF
```

### 重启后端

```bash
docker-compose restart backend
```

## 查看Payload参数

请在Network标签中点击 `search` 请求，查看 **Payload** 标签，看看POST请求体需要什么参数，然后告诉我，我会更新代码。

## 验证

重启后端后，创建RASP扫描任务，查看日志：

```bash
docker-compose logs --tail=100 backend | grep -E "\[RASP\]"
```

应该看到：
- `[RASP] 使用Cookie认证`
- `[RASP] POST请求返回状态码: 200`

