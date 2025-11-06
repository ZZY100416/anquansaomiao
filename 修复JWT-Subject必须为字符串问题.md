# 修复JWT Subject必须为字符串问题

## 问题根源

从后端日志可以看到：
```
[JWT ERROR] JWT验证失败: Subject must be a string
```

**根本原因**：
- Flask-JWT-Extended要求token的`subject`（`sub`）字段必须是字符串
- 登录时创建token：`create_access_token(identity=user.id)` 传入的是整数
- 但`get_jwt_identity()`返回的是字符串，需要转换为整数用于数据库查询

## 已实施的修复

### 1. 登录时创建token（已修复）
```python
# 修复前
access_token = create_access_token(identity=user.id)

# 修复后
access_token = create_access_token(identity=str(user.id))
```

### 2. 所有使用get_jwt_identity()的地方（已修复）
所有API路由中，将字符串转换为整数：
```python
# 修复前
user_id = get_jwt_identity()

# 修复后
user_id = int(get_jwt_identity())  # 转换为整数
```

已修复的文件：
- `backend/app/api/auth.py` - `/me` 路由
- `backend/app/api/reports.py` - `/dashboard` 和 `/<scan_id>` 路由
- `backend/app/api/projects.py` - 所有路由
- `backend/app/api/scans.py` - 所有路由
- `backend/app/api/rasp.py` - `/events/<event_id>/handle` 路由

## 立即测试步骤

### 1. 在Ubuntu上重新构建并重启后端

```bash
cd ~/projects/anquansaomiao
docker-compose build backend
docker-compose restart backend
```

### 2. 在浏览器中测试

1. **清除浏览器缓存**（F12 -> Application -> Clear storage）
2. **重新登录**（admin/admin123）
3. **观察是否跳转到dashboard**
4. **查看后端日志**，应该看到：
   ```
   [Dashboard] 请求到达 - Authorization头: Bearer ...
   [Dashboard] User ID: 1
   ```
   而不是 `[JWT ERROR]` 错误

### 3. 验证修复

- ✅ 登录成功
- ✅ 跳转到dashboard，不再跳转回登录页
- ✅ Dashboard数据正常显示
- ✅ 后端日志中没有 `[JWT ERROR]`

## 如果还有问题

如果修复后仍然有问题，请提供：
1. 后端日志中的最新输出
2. 浏览器Console中的错误信息
3. Network标签中dashboard请求的状态码和响应

