# 统一安全扫描平台 - API接口文档

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON

## 认证

### 注册

**POST** `/auth/register`

创建新用户账户。

**请求体**:
```json
{
  "username": "user123",
  "password": "password123",
  "email": "user@example.com",
  "role": "user"
}
```

**响应**:
```json
{
  "message": "注册成功",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "role": "user",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 登录

**POST** `/auth/login`

用户登录获取访问令牌。

**请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

### 获取当前用户

**GET** `/auth/me`

获取当前登录用户信息（需要认证）。

**Headers**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "created_at": "2024-01-01T00:00:00"
}
```

## 项目管理

### 获取项目列表

**GET** `/projects`

获取当前用户的所有项目（需要认证）。

**响应**:
```json
[
  {
    "id": 1,
    "name": "My Project",
    "description": "项目描述",
    "repository_url": "https://github.com/user/repo",
    "project_type": "python",
    "user_id": 1,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "scan_count": 5
  }
]
```

### 创建项目

**POST** `/projects`

创建新项目（需要认证）。

**请求体**:
```json
{
  "name": "My Project",
  "description": "项目描述",
  "repository_url": "https://github.com/user/repo",
  "project_type": "python"
}
```

**响应**: 201 Created
```json
{
  "id": 1,
  "name": "My Project",
  ...
}
```

### 获取项目详情

**GET** `/projects/{project_id}`

获取指定项目的详细信息（需要认证）。

**响应**:
```json
{
  "id": 1,
  "name": "My Project",
  ...
}
```

### 更新项目

**PUT** `/projects/{project_id}`

更新项目信息（需要认证）。

**请求体**:
```json
{
  "name": "Updated Project Name",
  "description": "更新后的描述"
}
```

### 删除项目

**DELETE** `/projects/{project_id}`

删除项目（需要认证）。**注意**: 会同时删除项目下的所有扫描任务和结果。

**响应**: 200 OK
```json
{
  "message": "项目删除成功"
}
```

## 扫描任务

### 获取扫描任务列表

**GET** `/scans`

获取扫描任务列表（需要认证）。

**查询参数**:
- `project_id` (可选): 筛选指定项目的扫描任务

**示例**: `/scans?project_id=1`

**响应**:
```json
[
  {
    "id": 1,
    "project_id": 1,
    "scan_type": "sast",
    "status": "completed",
    "started_at": "2024-01-01T00:00:00",
    "completed_at": "2024-01-01T00:05:00",
    "created_at": "2024-01-01T00:00:00",
    "config": {},
    "result_count": 10
  }
]
```

### 创建扫描任务

**POST** `/scans`

创建新的扫描任务（需要认证）。

**请求体**:
```json
{
  "project_id": 1,
  "scan_type": "sast",
  "config": {
    "rules": "auto",
    "exclude": ["node_modules"]
  }
}
```

**scan_type 可选值**:
- `sast`: 静态代码扫描
- `sca`: 依赖漏洞扫描
- `container`: 容器镜像扫描

**响应**: 201 Created
```json
{
  "id": 1,
  "project_id": 1,
  "scan_type": "sast",
  "status": "pending",
  ...
}
```

### 获取扫描任务详情

**GET** `/scans/{scan_id}`

获取指定扫描任务的详细信息（需要认证）。

**响应**:
```json
{
  "id": 1,
  "project_id": 1,
  "scan_type": "sast",
  "status": "completed",
  ...
}
```

### 获取扫描结果

**GET** `/scans/{scan_id}/results`

获取指定扫描任务的结果列表（需要认证）。

**响应**:
```json
[
  {
    "id": 1,
    "scan_id": 1,
    "severity": "high",
    "vulnerability_type": "SQL Injection",
    "title": "潜在的SQL注入漏洞",
    "description": "检测到未参数化的SQL查询",
    "file_path": "app/models/user.py",
    "line_number": 45,
    "cve_id": null,
    "package_name": null,
    "package_version": null,
    "fixed_version": null,
    "raw_data": {},
    "created_at": "2024-01-01T00:05:00"
  }
]
```

## 报告

### 生成报告

**GET** `/reports/{scan_id}`

生成扫描任务的报告（需要认证）。

**查询参数**:
- `type` (可选): 报告类型，`html` (默认) 或 `pdf`

**示例**: `/reports/1?type=pdf`

**响应**:
- HTML类型: JSON格式的报告数据
- PDF类型: PDF文件流

### 获取仪表盘数据

**GET** `/reports/dashboard`

获取仪表盘统计数据（需要认证）。

**响应**:
```json
{
  "total_projects": 10,
  "total_scans": 50,
  "completed_scans": 45,
  "severity_stats": {
    "critical": 5,
    "high": 15,
    "medium": 30,
    "low": 10,
    "info": 5
  }
}
```

## 健康检查

### 健康状态

**GET** `/health`

检查API服务健康状态。

**响应**:
```json
{
  "status": "healthy",
  "service": "Unified Security Scanner API"
}
```

## 错误响应

### 错误格式

所有错误响应使用统一格式：

```json
{
  "error": "错误描述信息"
}
```

### HTTP状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或token无效
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

### 错误示例

**401 Unauthorized**:
```json
{
  "error": "用户名或密码错误"
}
```

**400 Bad Request**:
```json
{
  "error": "项目名称不能为空"
}
```

**404 Not Found**:
```json
{
  "error": "项目不存在"
}
```

## 使用示例

### Python示例

```python
import requests

# 登录
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['access_token']

# 创建项目
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'http://localhost:5000/api/projects',
    json={
        'name': 'My Project',
        'project_type': 'python'
    },
    headers=headers
)
project_id = response.json()['id']

# 创建扫描任务
response = requests.post(
    'http://localhost:5000/api/scans',
    json={
        'project_id': project_id,
        'scan_type': 'sast'
    },
    headers=headers
)
scan_id = response.json()['id']

# 获取扫描结果
response = requests.get(
    f'http://localhost:5000/api/scans/{scan_id}/results',
    headers=headers
)
results = response.json()
```

### cURL示例

```bash
# 登录
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 获取项目列表
curl -X GET http://localhost:5000/api/projects \
  -H "Authorization: Bearer <token>"

# 创建扫描任务
curl -X POST http://localhost:5000/api/scans \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"scan_type":"sast"}'
```

## 限流

当前版本未实现API限流，未来版本将添加：

- 每分钟最多100个请求
- 每个用户最多10个并发扫描任务

## 版本信息

- **API版本**: v1
- **最后更新**: 2024-01-01

