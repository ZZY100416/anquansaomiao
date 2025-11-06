# 查看Dashboard 422错误详情

## 问题

从Network标签看到 `/api/reports/dashboard` 请求返回422错误。

## 需要查看的信息

### 在浏览器中：

1. **打开Network标签**
2. **找到 `/api/reports/dashboard` 请求（红色，422错误）**
3. **点击该请求**
4. **查看Response标签**：
   - 复制完整的响应内容
   - 应该包含错误信息，例如：`{"error": "无效的Token: ..."}`

### 在Ubuntu上：

```bash
# 查看后端日志，看422错误的具体原因
docker-compose logs --tail=50 backend | grep -i "422\|dashboard\|jwt\|token"
```

## 可能的原因

1. **Token格式错误**：后端无法解析token
2. **JWT配置问题**：后端JWT配置有误
3. **Token未发送**：前端没有正确添加Authorization头

## 快速测试

在浏览器Console中执行：

```javascript
// 检查token
const token = localStorage.getItem('token');
console.log('Token:', token);
console.log('Token长度:', token?.length);

// 检查API请求头
// 在Network标签中，点击dashboard请求，查看Headers标签
// 应该看到：Authorization: Bearer <token>
```

## 临时解决方案

如果想快速验证，可以临时禁用422的token清除：

但这不是根本解决方案，需要找到422错误的根本原因。

请提供：
1. Network标签中dashboard请求的Response内容
2. 后端日志中的422错误信息

