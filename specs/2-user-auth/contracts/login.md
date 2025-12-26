# API 契约: 用户登录

## 端点信息

- **路径**: `/api/login`
- **方法**: `POST`
- **描述**: 用户通过用户名和密码登录系统
- **认证要求**: 无
- **速率限制**: 5 次/分钟

---

## 请求

### 请求头

| 名称 | 类型 | 必需 | 描述 |
|------|------|------|------|
| Content-Type | string | 是 | 必须为 `application/json` |

### 请求体

| 参数 | 类型 | 必需 | 描述 | 约束 |
|------|------|------|------|------|
| username | string | 是 | 用户名 | 最大长度 64 字符 |
| password | string | 是 | 密码 | 最小长度 6 字符 |

### 请求示例

```json
{
  "username": "admin",
  "password": "stacks"
}
```

---

## 响应

### 成功响应 (200 OK)

**状态码**: `200`

**响应体**:

```json
{
  "success": true,
  "message": "登录成功"
}
```

**响应头**:

| 名称 | 值 | 描述 |
|------|-----|------|
| Set-Cookie | `session=...; HttpOnly; Secure; SameSite=Lax; Max-Age=86400` | 会话 Cookie |

### 错误响应

#### 1. 凭据无效 (401 Unauthorized)

**状态码**: `401`

**响应体**:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "用户名或密码错误"
  }
}
```

#### 2. 速率限制 (429 Too Many Requests)

**状态码**: `429`

**响应体**:

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "尝试次数过多。请在10分钟后重试。"
  }
}
```

#### 3. 登录已禁用 (403 Forbidden)

**状态码**: `403`

**响应体**:

```json
{
  "success": false,
  "error": {
    "code": "LOGIN_DISABLED",
    "message": "登录功能已被禁用"
  }
}
```

#### 4. 请求格式错误 (400 Bad Request)

**状态码**: `400`

**响应体**:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求格式错误"
  }
}
```

---

## 业务逻辑

### 验证流程

1. **检查登录是否禁用**
   - 读取配置 `login.disable`
   - 如果为 `true`，返回 403 错误

2. **检查速率限制**
   - 获取客户端 IP 地址
   - 检查是否被锁定
   - 如果被锁定，返回 429 错误

3. **验证用户名**
   - 读取配置 `login.username`
   - 比较输入的用户名

4. **验证密码**
   - 读取配置 `login.password`（bcrypt 哈希）
   - 使用 `verify_password()` 验证密码

5. **创建会话**
   - 设置 `session['logged_in'] = True`
   - 设置 `session['username'] = username`
   - 生成会话 ID
   - 设置会话过期时间（24 小时）

6. **清除登录尝试记录**
   - 清除该 IP 的登录尝试记录
   - 清除该 IP 的锁定记录

### 失败处理

- **用户名或密码错误**: 记录失败的登录尝试，返回 401 错误
- **速率限制**: 如果达到 5 次失败，锁定 IP 10 分钟，返回 429 错误

---

## 安全考虑

### 密码安全

- 密码使用 bcrypt 哈希存储
- 密码验证使用安全的比较方法
- 明文密码不在日志中记录

### 会话安全

- 使用 HTTPOnly Cookie 防止 XSS 攻击
- 使用 Secure Cookie 仅通过 HTTPS 传输
- 使用 SameSite=Lax 防止 CSRF 攻击
- 会话过期时间 24 小时

### 速率限制

- 5 次失败尝试后锁定 10 分钟
- 基于 IP 地址的跟踪
- 自动清理过期的尝试记录

---

## 测试用例

### 测试用例 1: 登录成功

**输入**:
```json
{
  "username": "admin",
  "password": "stacks"
}
```

**预期输出**:
```json
{
  "success": true,
  "message": "登录成功"
}
```

**验证**:
- 状态码为 200
- 响应包含 `success: true`
- 会话 Cookie 已设置

### 测试用例 2: 用户名错误

**输入**:
```json
{
  "username": "wrong",
  "password": "stacks"
}
```

**预期输出**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "用户名或密码错误"
  }
}
```

**验证**:
- 状态码为 401
- 响应包含错误信息

### 测试用例 3: 密码错误

**输入**:
```json
{
  "username": "admin",
  "password": "wrong"
}
```

**预期输出**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "用户名或密码错误"
  }
}
```

**验证**:
- 状态码为 401
- 响应包含错误信息

### 测试用例 4: 速率限制

**输入**: 连续 6 次错误登录

**预期输出**:
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "尝试次数过多。请在10分钟后重试。"
  }
}
```

**验证**:
- 状态码为 429
- 响应包含速率限制信息

---

## 实现参考

### Python 实现

```python
from flask import request, session, jsonify, current_app
from stacks.security.auth import check_rate_limit, verify_password, record_failed_attempt, clear_attempts

@api_bp.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    # 检查登录是否禁用
    cfg = current_app.stacks_config
    if cfg.get("login", "disable"):
        return jsonify({
            'success': False,
            'error': {
                'code': 'LOGIN_DISABLED',
                'message': '登录功能已被禁用'
            }
        }), 403
    
    # 获取请求参数
    data = request.json
    if not data:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_REQUEST',
                'message': '请求格式错误'
            }
        }), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # 检查速率限制
    ip = request.remote_addr
    allowed, message = check_rate_limit(ip)
    if not allowed:
        return jsonify({
            'success': False,
            'error': {
                'code': 'RATE_LIMIT_EXCEEDED',
                'message': message
            }
        }), 429
    
    # 验证凭据
    stored_username = cfg.get('login', 'username')
    stored_password = cfg.get('login', 'password')
    
    if username == stored_username and verify_password(password, stored_password):
        # 创建会话
        session['logged_in'] = True
        session['username'] = username
        clear_attempts(ip)
        return jsonify({'success': True, 'message': '登录成功'})
    else:
        record_failed_attempt(ip)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_CREDENTIALS',
                'message': '用户名或密码错误'
            }
        }), 401
```

---

## 参考资料

- [Flask Session 文档](https://flask.palletsprojects.com/en/latest/api/#flask.session)
- [OWASP 认证备忘单](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [HTTP 状态码](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
