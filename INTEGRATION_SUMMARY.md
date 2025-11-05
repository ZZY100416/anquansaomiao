# OpenRASP集成总结

## 集成完成情况

✅ **已完成OpenRASP集成到统一安全扫描平台**

### 新增功能

1. **RASP扫描器** (`backend/app/scanners/rasp_scanner.py`)
   - 集成OpenRASP管理后台API
   - 支持获取运行时安全事件
   - 支持按应用ID和时间范围筛选事件

2. **RASP事件模型** (`backend/app/models/rasp_event.py`)
   - 存储RASP运行时安全事件
   - 支持事件状态管理（已处理/未处理）
   - 记录事件详细信息

3. **RASP API接口** (`backend/app/api/rasp.py`)
   - `/api/rasp/status` - 获取OpenRASP服务状态
   - `/api/rasp/events` - 获取RASP事件列表
   - `/api/rasp/events/{id}` - 获取事件详情
   - `/api/rasp/events/{id}/handle` - 标记事件为已处理
   - `/api/rasp/events/sync` - 同步RASP事件

4. **RASP前端页面** (`frontend/src/pages/RASPEvents.js`)
   - RASP事件列表展示
   - 事件筛选和搜索
   - 事件详情查看
   - 事件处理状态管理
   - OpenRASP连接状态显示

5. **扫描类型扩展**
   - 扫描任务支持RASP类型
   - 前端界面新增RASP扫描选项

6. **集成文档** (`docs/OpenRASP集成指南.md`)
   - OpenRASP安装配置说明
   - 集成步骤详解
   - API接口文档
   - 常见问题解答

## 使用说明

### 1. 配置OpenRASP连接

在环境变量中配置：

```bash
OPENRASP_API_URL=http://localhost:11111/api
OPENRASP_API_KEY=your-api-key
```

### 2. 访问RASP事件页面

1. 登录统一安全扫描平台
2. 点击左侧菜单 "RASP事件"
3. 查看OpenRASP连接状态
4. 点击 "同步事件" 同步RASP事件

### 3. 创建RASP扫描任务

1. 进入 "扫描任务" 页面
2. 点击 "新建扫描"
3. 选择扫描类型: **RASP - 运行时安全扫描**
4. 配置扫描参数（可选）:
   ```json
   {
     "app_id": "your-app-id",
     "start_time": "2024-01-01T00:00:00",
     "end_time": "2024-01-01T23:59:59"
   }
   ```

### 4. 查看和处理事件

1. 在RASP事件页面查看事件列表
2. 使用筛选器筛选事件（严重级别、处理状态、时间范围）
3. 点击 "详情" 查看事件详细信息
4. 点击 "标记已处理" 处理安全事件

## 技术实现

### 后端架构

```
backend/
├── app/
│   ├── scanners/
│   │   └── rasp_scanner.py      # RASP扫描器
│   ├── models/
│   │   └── rasp_event.py         # RASP事件模型
│   └── api/
│       └── rasp.py               # RASP API接口
```

### 前端架构

```
frontend/src/
├── pages/
│   └── RASPEvents.js            # RASP事件页面
└── components/
    └── Layout/
        └── MainLayout.js         # 已更新菜单
```

## 数据库变更

新增数据表：

- `rasp_events` - 存储RASP运行时安全事件

运行数据库迁移：

```bash
# 在应用启动时会自动创建表
# 或手动执行
docker-compose exec backend python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
```

## 环境要求

### OpenRASP管理后台

- OpenRASP管理后台已安装并运行
- API接口地址可访问（默认: http://localhost:11111/api）
- 如有API密钥，需要配置OPENRASP_API_KEY

### 应用配置

需要在受保护的应用中安装和配置OpenRASP Agent：

- Java应用: 添加-javaagent参数
- PHP应用: 安装OpenRASP PHP扩展
- Python应用: 安装openrasp包

详细配置请参考 `docs/OpenRASP集成指南.md`

## 下一步建议

1. **测试连接**: 确认OpenRASP管理后台可访问
2. **配置应用**: 在关键应用上部署OpenRASP Agent
3. **监控事件**: 定期查看和处理RASP事件
4. **优化规则**: 根据实际情况调整OpenRASP检测规则
5. **自动化**: 配置自动同步和告警

## 相关文档

- [OpenRASP集成指南](docs/OpenRASP集成指南.md)
- [OpenRASP官方文档](https://rasp.baidu.com/doc/)
- [OpenRASP GitHub](https://github.com/baidu/openrasp)

## 注意事项

1. **网络连接**: 确保统一安全扫描平台可以访问OpenRASP管理后台
2. **API密钥**: 如果OpenRASP管理后台需要API密钥，请正确配置
3. **性能影响**: OpenRASP对应用性能影响很小，但需要监控
4. **误报处理**: 合理配置OpenRASP规则，减少误报
5. **事件存储**: 定期清理旧事件，避免数据库过大

## 技术支持

如有问题，请查看：

1. [OpenRASP集成指南 - 常见问题](docs/OpenRASP集成指南.md#常见问题)
2. OpenRASP官方文档
3. 提交GitHub Issue

---

**集成完成时间**: 2024-01-01  
**版本**: v1.1.0

