# 查找OpenRASP API路径指南

## 问题

OpenRASP的API路径不确定，需要找到正确的端点。

## 方法1：通过浏览器开发者工具查找

1. **打开OpenRASP管理后台**
   - 访问：`http://192.168.203.141:8086`
   - 登录管理后台

2. **打开浏览器开发者工具**
   - 按 `F12` 或右键选择"检查"
   - 切换到 `Network`（网络）标签

3. **查看API请求**
   - 在管理后台中点击"攻击事件"或"事件列表"
   - 在Network标签中查看实际的API请求
   - 找到请求的URL，例如：
     - `http://192.168.203.141:8086/api/v1/attack?page=1&size=10`
     - `http://192.168.203.141:8086/api/attack/list`

4. **记录正确的API路径**
   - 复制实际的API路径
   - 更新代码中的API路径

## 方法2：查看OpenRASP API文档

1. **访问OpenRASP文档**
   - 主文档：https://rasp.baidu.com/doc/install/main.html
   - 查找"API文档"或"接口文档"部分

2. **查找事件相关的API**
   - 查找获取攻击事件的API端点
   - 查看请求方法和参数

## 方法3：直接测试API路径

在Ubuntu上测试：

```bash
# 测试不同的API路径
curl http://192.168.203.141:8086/api/v1/attack
curl http://192.168.203.141:8086/api/v1/attack/list
curl http://192.168.203.141:8086/api/attack
curl http://192.168.203.141:8086/api/events

# 如果返回JSON数据，说明路径正确
# 如果返回404，说明路径不对
```

## 方法4：查看OpenRASP源代码或配置文件

如果OpenRASP是开源的，可以：
1. 查看源代码中的路由定义
2. 查看配置文件中的API路径
3. 查看数据库中的API配置

## 当前代码已尝试的路径

代码会自动尝试以下路径：
- `/api/v1/attack` - 攻击事件API（最常见）
- `/api/v1/attack/list` - 攻击事件列表
- `/api/v1/event` - 事件API
- `/api/v1/event/list` - 事件列表
- `/api/attack` - 简化路径
- `/api/events` - 事件API
- `/api/v1/events` - v1事件API
- `/events` - 直接路径

## 找到正确路径后如何更新

1. **更新环境变量**（推荐）：
   ```bash
   # 在docker-compose.yml中
   - OPENRASP_API_URL=http://192.168.203.141:8086
   ```

2. **或者直接修改代码**：
   在 `backend/app/scanners/rasp_scanner.py` 中，找到 `api_paths` 列表，将正确的路径放在最前面。

## 建议

**最快的方法**：使用浏览器开发者工具查看OpenRASP前端实际调用的API路径，这是最准确的方法。

