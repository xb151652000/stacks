# API 契约: 用户登出

## 端点信息

- **路径**: `/api/logout`
- **方法**: `POST`
- **描述**: 用户登出系统，销毁会话
- **认证要求**: 会话认证（仅 Web UI）
- **速率限制**: 无限制

---

## 请求

### 请求头

| 名称 | 类型 | 必需 | 描述 |
|------|------|------|------|
| Content-Type | string | 是 | 必须为 `application/json` |
| Cookie | string | 是 | 会话 Cookie |

### 请求体

无请求体。

### 请求示例

```http
POST /api/logout HTTP/1.1
Host: localhost:7788
Content-Type: application/json
Cookie: session=...
```

---

## 响应

### 成功响应 (200 OK)

**状态码**: `200`

**响应体**:

```json
{
  "success": true,
  "message": "登出成功"
}
```

**响应头**:

| 名称 | 值 | 描述 |
|------|-----|------|
| Set-Cookie | `session=; HttpOnly; Secure; SameSite=Lax; Max-Age=0` | 清除会话 Cookie |

### 错误响应

#### 1. 未授权 (401 Unauthorized)

**状态码**: `401`

**响应体**:

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "未授权访问"
  }
}
```

#### 2. 登录已禁用 (403 Forbidden)

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

---

## 业务逻辑

### 验证流程

1. **检查登录是否禁用**
   - 读取配置 `login.disable`
   - 如果为 `true`，返回 403 错误

2. **验证会话**
   - 检查 `session.get('logged_in')`
   - 如果为 `False` 或不存在，返回 401 错误

3. **销毁会话**
   - 调用 `session.clear()`
   - 清除所有会话数据

4. **返回成功响应**
   - 返回 200 状态码
   - 设置 Cookie 的 Max-Age 为 0 以清除 Cookie

---

## 安全考虑

### 会话安全

- 销毁会话时清除所有会话数据
- 清除客户端 Cookie
- 防止会话固定攻击

### 错误处理

- 未授权访问返回 401 错误
- 不泄露敏感信息

---

## 测试用例

### 测试用例 1: 登出成功

**输入**:
```http
POST /api/logout HTTP/1.1
Host: localhost:7788
Content-Type: application/json
Cookie: session=valid_session_id
```

**预期输出**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

**验证**:
- 状态码为 200
- 响应包含 `success: true`
- 会话 Cookie 已清除

### 测试用例 2: 未授权访问

**输入**:
```http
POST /api/logout HTTP/1.1
Host: localhost:7788
Content-Type: application/json
Cookie: session=invalid_session_id
```

**预期输出**:
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "未授权访问"
  }
}
```

**验证**:
- 状态码为 401
- 响应包含错误信息

---

## 实现参考

### Python 实现

```python
from flask import session, jsonify, current_app
from stacks.security.auth import require_session_only

@api_bp.route('/api/logout', methods=['POST'])
@require_session_only
def logout():
    """用户登出"""
    # 销毁会话
    session.clear()
    return jsonify({'success': True, 'message': '登出成功'})
```

---

## 参考资料

- [Flask Session 文档](https://flask.palletsprojects.com/en/latest/api/#flask.session)
- [OWASP 会话管理备忘单](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
