# API 契约: 修改密码

## 端点信息

- **路径**: `/api/password/change`
- **方法**: `POST`
- **描述**: 修改用户密码
- **认证要求**: 会话认证（仅 Web UI）
- **速率限制**: 5 次/分钟

---

## 请求

### 请求头

| 名称 | 类型 | 必需 | 描述 |
|------|------|------|------|
| Content-Type | string | 是 | 必须为 `application/json` |
| Cookie | string | 是 | 会话 Cookie |

### 请求体

| 参数 | 类型 | 必需 | 描述 | 约束 |
|------|------|------|------|------|
| current_password | string | 是 | 当前密码 | 最小长度 6 字符 |
| new_password | string | 是 | 新密码 | 最小长度 6 字符 |
| confirm_password | string | 是 | 确认新密码 | 必须与 new_password 相同 |

### 请求示例

```json
{
  "current_password": "stacks",
  "new_password": "new_password",
  "confirm_password": "new_password"
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
  "message": "密码已修改"
}
```

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

#### 2. 密码不一致 (400 Bad Request)

**状态码**: `400`

**响应体**:

```json
{
  "success": false,
  "error": {
    "code": "PASSWORD_MISMATCH",
    "message": "两次输入的密码不一致"
  }
}
```

#### 3. 密码长度不足 (400 Bad Request)

**状态码**: `400`

**响应体**:

```json
{
  "success": false,
  "error": {
    "code": "PASSWORD_TOO_SHORT",
    "message": "密码长度至少为 6 个字符"
  }
}
```

#### 4. 当前密码错误 (400 Bad Request)

**状态码**: `400`

**响应体**:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_CURRENT_PASSWORD",
    "message": "当前密码错误"
  }
}
```

#### 5. 请求格式错误 (400 Bad Request)

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

2. **验证会话**
   - 检查 `session.get('logged_in')`
   - 如果为 `False` 或不存在，返回 401 错误

3. **验证请求参数**
   - 检查请求体是否包含所有必需字段
   - 如果缺少字段，返回 400 错误

4. **验证新密码一致性**
   - 比较 `new_password` 和 `confirm_password`
   - 如果不一致，返回 400 错误

5. **验证新密码长度**
   - 检查 `new_password` 长度是否至少 6 个字符
   - 如果不足，返回 400 错误

6. **验证当前密码**
   - 读取配置 `login.password`（bcrypt 哈希）
   - 使用 `verify_password()` 验证当前密码
   - 如果验证失败，返回 400 错误

7. **更新密码**
   - 使用 `hash_password()` 哈希新密码
   - 更新配置 `login.password`
   - 保存配置

8. **返回成功响应**
   - 返回 200 状态码
   - 返回成功消息

---

## 安全考虑

### 密码安全

- 新密码使用 bcrypt 哈希存储
- 密码验证使用安全的比较方法
- 明文密码不在日志中记录

### 验证安全

- 验证当前密码确保只有用户本人可以修改密码
- 验证新密码一致性防止输入错误
- 验证密码长度确保密码强度

### 错误处理

- 不泄露当前密码是否正确的具体信息
- 使用通用错误消息

---

## 测试用例

### 测试用例 1: 修改密码成功

**输入**:
```json
{
  "current_password": "stacks",
  "new_password": "new_password",
  "confirm_password": "new_password"
}
```

**预期输出**:
```json
{
  "success": true,
  "message": "密码已修改"
}
```

**验证**:
- 状态码为 200
- 响应包含 `success: true`
- 配置文件中的密码已更新

### 测试用例 2: 密码不一致

**输入**:
```json
{
  "current_password": "stacks",
  "new_password": "new_password",
  "confirm_password": "different_password"
}
```

**预期输出**:
```json
{
  "success": false,
  "error": {
    "code": "PASSWORD_MISMATCH",
    "message": "两次输入的密码不一致"
  }
}
```

**验证**:
- 状态码为 400
- 响应包含错误信息

### 测试用例 3: 密码长度不足

**输入**:
```json
{
  "current_password": "stacks",
  "new_password": "123",
  "confirm_password": "123"
}
```

**预期输出**:
```json
{
  "success": false,
  "error": {
    "code": "PASSWORD_TOO_SHORT",
    "message": "密码长度至少为 6 个字符"
  }
}
```

**验证**:
- 状态码为 400
- 响应包含错误信息

### 测试用例 4: 当前密码错误

**输入**:
```json
{
  "current_password": "wrong_password",
  "new_password": "new_password",
  "confirm_password": "new_password"
}
```

**预期输出**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CURRENT_PASSWORD",
    "message": "当前密码错误"
  }
}
```

**验证**:
- 状态码为 400
- 响应包含错误信息

---

## 实现参考

### Python 实现

```python
from flask import request, session, jsonify, current_app
from stacks.security.auth import require_session_only, verify_password, hash_password

@api_bp.route('/api/password/change', methods=['POST'])
@require_session_only
def change_password():
    """修改密码"""
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
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    # 验证新密码一致性
    if new_password != confirm_password:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PASSWORD_MISMATCH',
                'message': '两次输入的密码不一致'
            }
        }), 400
    
    # 验证新密码长度
    if len(new_password) < 6:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PASSWORD_TOO_SHORT',
                'message': '密码长度至少为 6 个字符'
            }
        }), 400
    
    # 验证当前密码
    config = current_app.stacks_config
    stored_password = config.get('login', 'password')
    
    if not verify_password(current_password, stored_password):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_CURRENT_PASSWORD',
                'message': '当前密码错误'
            }
        }), 400
    
    # 更新密码
    hashed_password = hash_password(new_password)
    config.set('login', 'password', value=hashed_password)
    config.save()
    
    return jsonify({'success': True, 'message': '密码已修改'})
```

---

## 参考资料

- [bcrypt 文档](https://pypi.org/project/bcrypt/)
- [OWASP 密码存储备忘单](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
