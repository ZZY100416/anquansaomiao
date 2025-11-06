# 修复容器扫描和OpenRASP问题

## 问题1：容器扫描 - image_name提取失败

### 现象
- config解析成功：`{"image_name": "mysql:8"}`
- 但image_name提取为空：`提取的image_name: ''`

### 已修复
1. 添加了详细的调试日志，打印config的所有键值对
2. 改进了image_name提取逻辑，直接使用字典访问而不是`.get()`
3. 支持多种键名：`image_name`、`imageName`、`image`

### 测试步骤
```bash
# 重启后端
docker-compose restart backend
sleep 10

# 查看日志
docker-compose logs -f backend | grep -E "\[Container\]"
```

## 问题2：OpenRASP连接失败

### 现象
- 错误：`Connection refused` 到 `localhost:11111`
- 状态显示：未连接

### 已修复
1. 在`docker-compose.yml`中添加了OpenRASP环境变量：
   - `OPENRASP_API_URL=${OPENRASP_API_URL:-http://host.docker.internal:11111/api}`
   - `OPENRASP_API_KEY=${OPENRASP_API_KEY:-}`

### 配置OpenRASP地址

如果OpenRASP运行在Ubuntu主机上（端口11111），已经配置为 `host.docker.internal:11111`。

如果OpenRASP运行在其他地方，需要：

1. **创建`.env`文件**（在项目根目录）：
```bash
OPENRASP_API_URL=http://your-openrasp-host:11111/api
OPENRASP_API_KEY=your-api-key
```

2. **或者直接修改docker-compose.yml**中的地址：
```yaml
- OPENRASP_API_URL=http://192.168.x.x:11111/api
```

3. **重启后端容器**：
```bash
docker-compose restart backend
```

### 验证OpenRASP连接

```bash
# 在Ubuntu上测试OpenRASP是否可访问
curl http://localhost:11111/api/status

# 或者在容器内测试
docker-compose exec backend curl http://host.docker.internal:11111/api/status
```

## 如果OpenRASP不在当前机器

如果OpenRASP运行在其他服务器上，需要：

1. 确保OpenRASP服务已启动
2. 确保网络可达
3. 修改`OPENRASP_API_URL`为正确的地址
4. 如果OpenRASP需要认证，设置`OPENRASP_API_KEY`

## 下一步

1. 重启后端容器
2. 重新创建容器扫描任务，查看详细日志
3. 检查OpenRASP连接状态

