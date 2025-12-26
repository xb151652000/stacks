# 用户认证与授权系统 - 数据模型

## 项目信息

- **项目名称**: Stacks - Anna's Archive 下载管理器
- **功能模块**: 用户认证与授权系统
- **文档版本**: 1.0.0
- **创建日期**: 2025-12-26
- **规范文档**: `specs/2-user-auth/spec.md`

---

## 概述

本数据模型文档定义了用户认证与授权系统的数据结构，包括用户配置、API 配置和会话配置。系统使用 YAML 格式的配置文件存储认证信息，不使用传统数据库。

---

## 配置文件结构

### 主配置文件路径

```
config/config.yaml
```

### 配置模式文件路径

```
files/config_schema.yaml
```

---

## 数据模型定义

### 1. 用户配置模型 (login)

**描述**: 定义用户登录凭据和认证设置。

**配置路径**: `login`

**字段说明**:

| 字段名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| username | string | 是 | USERNAME (环境变量) 或 "admin" | 用户名，最大长度 64 字符 |
| password | string | 是 | HASH_PASSWORD (环境变量) 或 bcrypt 哈希 | 密码的 bcrypt 哈希值（60 字符） |
| disable | boolean | 是 | false | 是否禁用登录功能 |

**YAML 示例**:

```yaml
login:
  username: "admin"
  password: "$2b$12$cfJlGm4XRCi3lOfhLZ2cmuNbHsICxQfthA2wpuWdVanUdCWEiYMnW"
  disable: false
```

**配置模式**:

```yaml
login:
  username:
    types: [STRING]
    default: USERNAME
    max_length: 64
  password:
    types: [BCRYPTHASH]
    default: HASH_PASSWORD
  disable:
    types: [BOOL]
    default: false
```

**验证规则**:

- `username`: 必须是字符串，最大长度 64 字符
- `password`: 必须是有效的 bcrypt 哈希（以 `$2a$`、`$2b$` 或 `$2y$` 开头，长度 60 字符）
- `disable`: 必须是布尔值

**特殊处理**:

- 如果 `RESET_ADMIN=true` 环境变量设置，密码将被重置
- 如果用户名或密码为空或无效，将使用环境变量或默认值重置
- 默认用户名: `admin`
- 默认密码: `stacks`

---

### 2. API 配置模型 (api)

**描述**: 定义 API 密钥和会话密钥配置。

**配置路径**: `api`

**字段说明**:

| 字段名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| key | string | 否 | null | Admin API Key（32 字符），null 表示禁用 |
| downloader_key | string | 否 | null | Downloader API Key（32 字符），null 表示禁用 |
| session_secret | string | 是 | GENERATED | 会话密钥（32 字符） |

**YAML 示例**:

```yaml
api:
  key: "INMuBeoc23a-gZvIYs-Xx6H9K7c8rOly"
  downloader_key: "Xx6H9K7c8rOlyINMuBeoc23a-gZvIYs"
  session_secret: "abc123def456ghi789jkl012mno345pq"
```

**配置模式**:

```yaml
api:
  key:
    types: [SECRET_KEY, NULL]
    default: null
  downloader_key:
    types: [SECRET_KEY, NULL]
    default: null
  session_secret:
    types: [SECRET_KEY]
    default: GENERATE_SECRET_KEY
```

**验证规则**:

- `key`: 必须是有效的密钥（32 字符，包含字母、数字、下划线和连字符）或 null
- `downloader_key`: 必须是有效的密钥（32 字符）或 null
- `session_secret`: 必须是有效的密钥（32 字符）

**密钥格式**:

```
SECRET_KEY: 32 字符，包含字母（a-z, A-Z）、数字（0-9）、下划线（_）和连字符（-）
正则表达式: ^[a-zA-Z0-9_-]{32}$
```

**特殊处理**:

- `session_secret` 如果不存在，将自动生成新的 32 字符密钥
- `key` 和 `downloader_key` 设置为 null 表示禁用相应的 API Key

---

### 3. 会话模型 (Session)

**描述**: 定义用户会话的数据结构（存储在客户端 Cookie 中）。

**存储位置**: HTTPOnly Cookie

**字段说明**:

| 字段名 | 类型 | 描述 |
|--------|------|------|
| logged_in | boolean | 用户是否已登录 |
| username | string | 用户名 |
| session_id | string | 会话唯一标识符 |
| created_at | datetime | 会话创建时间 |
| expires_at | datetime | 会话过期时间 |

**Cookie 属性**:

| 属性 | 值 | 描述 |
|------|-----|------|
| HTTPOnly | true | 防止客户端脚本访问 Cookie |
| Secure | true | 仅通过 HTTPS 传输 |
| SameSite | Lax | 防止 CSRF 攻击 |
| Max-Age | 86400 | 会话过期时间（24 小时，单位：秒） |

**Python 示例**:

```python
from flask import session

# 创建会话
session['logged_in'] = True
session['username'] = 'admin'
session['session_id'] = 'abc123...'
session['created_at'] = datetime.now()
session['expires_at'] = datetime.now() + timedelta(hours=24)

# 验证会话
if session.get('logged_in'):
    username = session.get('username')
    # 用户已登录
```

---

### 4. 登录尝试跟踪模型 (Login Attempts)

**描述**: 跟踪登录尝试和锁定状态（存储在内存中）。

**存储位置**: 内存字典（`src/stacks/security/auth.py`）

**数据结构**:

```python
# 登录尝试记录
login_attempts: dict[str, list[datetime]] = {
    "192.168.1.100": [
        datetime(2025, 12, 26, 10, 0, 0),
        datetime(2025, 12, 26, 10, 0, 5),
        datetime(2025, 12, 26, 10, 0, 10),
    ]
}

# 登录锁定记录
login_lockouts: dict[str, datetime] = {
    "192.168.1.100": datetime(2025, 12, 26, 10, 10, 0),
}
```

**字段说明**:

| 字段名 | 类型 | 描述 |
|--------|------|------|
| login_attempts | dict | IP 地址到登录尝试时间列表的映射 |
| login_lockouts | dict | IP 地址到锁定到期时间的映射 |

**速率限制规则**:

- 最大尝试次数: 5 次
- 锁定时间: 10 分钟
- 记录保留时间: 10 分钟

**Python 示例**:

```python
from stacks.security.auth import check_rate_limit, record_failed_attempt, clear_attempts

# 检查速率限制
ip = request.remote_addr
allowed, message = check_rate_limit(ip)
if not allowed:
    return jsonify({'error': message}), 429

# 记录失败的登录尝试
record_failed_attempt(ip)

# 清除登录尝试记录（成功登录后）
clear_attempts(ip)
```

---

## 完整配置文件示例

```yaml
# config/config.yaml

server:
  host: 0.0.0.0
  port: 7788

login:
  username: 'admin'
  password: $2b$12$cfJlGm4XRCi3lOfhLZ2cmuNbHsICxQfthA2wpuWdVanUdCWEiYMnW
  disable: false

api:
  key: INMuBeoc23a-gZvIYs-Xx6H9K7c8rOly
  downloader_key: Xx6H9K7c8rOlyINMuBeoc23a-gZvIYs
  session_secret: abc123def456ghi789jkl012mno345pq

downloads:
  delay: 2
  retry_count: 3
  resume_attempts: 3
  prefer_title_naming: false
  include_hash: none
  incomplete_folder_path: /download/incomplete
  subdirectories: []

fast_download:
  enabled: false
  key: null

flaresolverr:
  enabled: true
  url: http://localhost:8191
  timeout: 60

queue:
  max_history: 100

logging:
  level: INFO
```

---

## 数据流图

### 登录流程数据流

```
用户输入凭据
    ↓
POST /api/login
    ↓
验证用户名和密码
    ↓
创建会话 (session['logged_in'] = True)
    ↓
设置 HTTPOnly Cookie
    ↓
返回成功响应
```

### API Key 认证流程数据流

```
API 请求
    ↓
检查 X-API-Key 请求头
    ↓
从配置文件读取 api.key 和 api.downloader_key
    ↓
验证 API Key 有效性
    ↓
确定 API Key 类型 (admin/downloader)
    ↓
检查权限
    ↓
允许或拒绝访问
```

### 密码重置流程数据流

```
设置环境变量 RESET_ADMIN=true
    ↓
设置环境变量 PASSWORD=new_password
    ↓
重启容器
    ↓
检测到 RESET_ADMIN=true
    ↓
生成新的密码哈希
    ↓
更新配置文件 (login.password)
    ↓
保存配置
```

---

## 数据验证

### 配置验证

所有配置值在加载时都会根据配置模式（`config_schema.yaml`）进行验证：

```python
from stacks.config import Config

# 加载并验证配置
config = Config()

# 获取配置值
username = config.get('login', 'username')
password_hash = config.get('login', 'password')
api_key = config.get('api', 'key')
```

### 密码验证

```python
from stacks.security.auth import hash_password, verify_password

# 哈希密码
hashed_password = hash_password("my_password")

# 验证密码
is_valid = verify_password("my_password", hashed_password)
```

### API Key 验证

```python
from stacks.security.auth import validate_api_key

# 验证 API Key
is_valid, key_type = validate_api_key("INMuBeoc23a-gZvIYs-Xx6H9K7c8rOly")

# key_type 可能是:
# - "admin": Admin API Key
# - "downloader": Downloader API Key
# - None: 无效的 API Key
```

---

## 安全考虑

### 密码安全

- 使用 bcrypt 算法哈希密码（至少 12 轮）
- 每个密码使用唯一的盐值
- 密码长度至少 6 个字符
- 明文密码不在日志中记录

### 会话安全

- 使用 HTTPOnly Cookie 防止 XSS 攻击
- 使用 Secure Cookie 仅通过 HTTPS 传输
- 使用 SameSite 属性防止 CSRF 攻击
- 会话过期时间默认 24 小时
- 会话密钥使用强随机数生成

### API 密钥安全

- API 密钥使用强随机字符串生成（32 字符）
- API 密钥通过 HTTP 请求头传递（避免日志记录）
- 支持禁用 API 密钥（设置为 null）
- 支持重新生成 API 密钥（旧密钥立即失效）

### 速率限制

- 5 次失败尝试后锁定 10 分钟
- 基于 IP 地址的跟踪
- 自动清理过期的尝试记录和锁定

---

## 扩展性考虑

### 未来可能的扩展

1. **多用户支持**: 扩展 `login` 配置支持多个用户
2. **基于角色的访问控制 (RBAC)**: 添加角色和权限配置
3. **外部认证集成**: 支持 OAuth、LDAP 等外部认证
4. **会话持久化**: 使用 Redis 存储会话数据
5. **双因素认证 (2FA)**: 添加 TOTP 或短信验证

### 数据库迁移

如果未来需要从配置文件迁移到数据库：

1. 创建数据库表结构
2. 编写迁移脚本将配置文件数据导入数据库
3. 更新配置加载逻辑从数据库读取
4. 保持向后兼容性

---

## 参考资料

- [bcrypt 文档](https://pypi.org/project/bcrypt/)
- [Flask Session 文档](https://flask.palletsprojects.com/en/latest/api/#flask.session)
- [OWASP 认证备忘单](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [PEP 8 - Style Guide for Python Code](https://peps8.org/)
