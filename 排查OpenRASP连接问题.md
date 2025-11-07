# 排查OpenRASP连接问题

## 当前状态

从日志看：
- `[RASP] OpenRASP基础地址: http://192.168.203.141:8086` ✓
- `[RASP] 已配置用户名密码，将尝试登录获取Cookie` ✓
- 但没有看到登录尝试的日志

## 问题分析

`get_rasp_status()` 方法被调用了，但可能：
1. 登录方法没有被正确调用
2. 登录API路径不对
3. 需要查看更详细的日志

## 排查步骤

### 1. 查看完整的RASP日志

```bash
docker-compose logs --tail=200 backend | grep -E "\[RASP\]"
```

### 2. 查看登录尝试日志

```bash
docker-compose logs --tail=200 backend | grep -E "登录|login|Cookie"
```

### 3. 手动测试登录API

在Ubuntu上测试登录：

```bash
# 测试登录API
curl -X POST http://192.168.203.141:8086/v1/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"openrasp","password":"zzy100416"}' \
  -v

# 查看响应头中的Set-Cookie
```

### 4. 如果登录API路径不对

查看OpenRASP管理后台的Network标签，找到登录请求的URL。

## 可能的问题

1. **登录API路径不对**：可能不是 `/v1/api/user/login`
2. **登录请求格式不对**：可能需要不同的参数格式
3. **Cookie提取失败**：响应中可能没有Set-Cookie头

## 快速修复

如果登录一直失败，可以手动获取Cookie：

1. 在浏览器中登录OpenRASP
2. 打开开发者工具（F12）
3. 在Network标签中查看任意请求的Cookie
4. 复制 `RASP_AUTH_ID` 的值
5. 在 `docker-compose.yml` 中配置：
   ```yaml
   - OPENRASP_AUTH_COOKIE=RASP_AUTH_ID=你的cookie值
   ```

