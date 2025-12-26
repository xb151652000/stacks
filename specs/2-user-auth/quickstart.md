# 用户认证系统快速开始指南

## 目录

- [系统概述](#系统概述)
- [前置要求](#前置要求)
- [安装和配置](#安装和配置)
- [API使用示例](#api使用示例)
- [常见问题](#常见问题)
- [故障排除](#故障排除)

---

## 系统概述

Stacks 用户认证系统提供了一套完整的身份验证和授权解决方案，支持以下功能：

- **用户登录**: 通过用户名和密码进行身份验证
- **用户登出**: 安全地终止用户会话
- **密码修改**: 允许用户更改自己的密码
- **API密钥认证**: 支持管理员和下载者角色的API访问
- **会话管理**: 基于HTTPOnly Cookie的安全会话
- **速率限制**: 防止暴力破解攻击

### 技术特性

- **密码安全**: 使用 bcrypt 进行密码哈希存储
- **会话安全**: HTTPOnly、Secure、SameSite Cookie
- **速率限制**: 5次失败尝试后锁定10分钟
- **配置灵活**: 通过YAML配置文件管理所有设置

---

## 前置要求

### 环境要求

- **Python**: 3.11 或更高版本
- **操作系统**: Windows、Linux 或 macOS
- **Docker**: 可选，用于容器化部署

### 依赖包

```txt
Flask==3.1.2
bcrypt==4.2.1
PyYAML==6.0.2
```

---

## 安装和配置

### 1. 安装依赖

```bash
pip install Flask bcrypt PyYAML
```

### 2. 配置文件

创建或编辑配置文件 `config.yaml`：

```yaml
login:
  username: 'admin'
  password: $2b$12$cfJlGm4XRCi3lOfhLZ2cmuNbHsICxQfthA2wpuWdVanUdCWEiYMnW
  disable: false

api:
  key: INMuBeoc23a-gZvIYs-Xx6H9K7c8rOly
  downloader_key: Xx6H9K7c8rOlyINMuBeoc23a-gZvIYs
  session_secret: abc123def456ghi789jkl012mno345pq
```

### 3. 生成密码哈希

使用以下Python脚本生成密码哈希：

```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# 生成密码哈希
hashed_password = hash_password('your_password_here')
print(hashed_password)
```

### 4. 启动服务

```bash
python src/stacks/main.py
```

服务将在 `http://localhost:7788` 启动。

---

## API使用示例

### 1. 用户登录

#### 请求

```bash
curl -X POST http://localhost:7788/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "stacks"
  }' \
  -c cookies.txt
```

#### 响应

```json
{
  "success": true,
  "message": "登录成功"
}
```

#### JavaScript (Fetch)

```javascript
const response = await fetch('http://localhost:7788/api/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',
  body: JSON.stringify({
    username: 'admin',
    password: 'stacks'
  })
});

const data = await response.json();
console.log(data);
```

### 2. 用户登出

#### 请求

```bash
curl -X POST http://localhost:7788/api/logout \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

#### 响应

```json
{
  "success": true,
  "message": "登出成功"
}
```

#### JavaScript (Fetch)

```javascript
const response = await fetch('http://localhost:7788/api/logout', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include'
});

const data = await response.json();
console.log(data);
```

### 3. 修改密码

#### 请求

```bash
curl -X POST http://localhost:7788/api/password/change \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "current_password": "stacks",
    "new_password": "new_secure_password",
    "confirm_password": "new_secure_password"
  }'
```

#### 响应

```json
{
  "success": true,
  "message": "密码已修改"
}
```

#### JavaScript (Fetch)

```javascript
const response = await fetch('http://localhost:7788/api/password/change', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',
  body: JSON.stringify({
    current_password: 'stacks',
    new_password: 'new_secure_password',
    confirm_password: 'new_secure_password'
  })
});

const data = await response.json();
console.log(data);
```

### 4. 使用API密钥访问

#### 管理员API密钥

```bash
curl -X GET http://localhost:7788/api/config \
  -H "X-API-Key: INMuBeoc23a-gZvIYs-Xx6H9K7c8rOly"
```

#### 下载者API密钥

```bash
curl -X GET http://localhost:7788/api/download \
  -H "X-API-Key: Xx6H9K7c8rOlyINMuBeoc23a-gZvIYs"
```

---

## 常见问题

### Q1: 如何重置管理员密码？

**A**: 使用以下步骤重置密码：

1. 生成新的密码哈希：

```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

hashed_password = hash_password('new_password')
print(hashed_password)
```

2. 编辑 `config.yaml` 文件，将 `login.password` 更新为新生成的哈希值：

```yaml
login:
  password: $2b$12$新的哈希值
```

3. 重启服务。

### Q2: 如何禁用登录功能？

**A**: 在 `config.yaml` 中设置 `login.disable` 为 `true`：

```yaml
login:
  disable: true
```

### Q3: 如何更改API密钥？

**A**: 在 `config.yaml` 中更新 `api.key` 和 `api.downloader_key`：

```yaml
api:
  key: 新的管理员密钥
  downloader_key: 新的下载者密钥
```

### Q4: 会话多久过期？

**A**: 会话默认在24小时后过期。过期后需要重新登录。

### Q5: 如何配置速率限制？

**A**: 速率限制在代码中硬编码为：
- 失败尝试次数：5次
- 锁定时间：10分钟

如需修改，请编辑 `src/stacks/security/auth.py` 文件中的相关参数。

---

## 故障排除

### 问题1: 登录时返回 "登录功能已被禁用"

**原因**: `login.disable` 配置为 `true`

**解决方案**:
```yaml
login:
  disable: false
```

### 问题2: 登录时返回 "尝试次数过多"

**原因**: 触发了速率限制

**解决方案**: 等待10分钟后重试，或重启服务清除锁定记录

### 问题3: 修改密码时返回 "当前密码错误"

**原因**: 输入的当前密码不正确

**解决方案**: 确认当前密码正确，或使用密码重置流程

### 问题4: API密钥认证失败

**原因**: API密钥不正确或未提供

**解决方案**:
- 检查 `config.yaml` 中的API密钥配置
- 确保请求头中包含正确的 `X-API-Key`
- 确认使用的是正确的API密钥（管理员或下载者）

### 问题5: 会话丢失

**原因**: 会话Cookie未正确设置或已过期

**解决方案**:
- 确保浏览器允许Cookie
- 检查Cookie的 `SameSite` 和 `Secure` 属性
- 重新登录获取新的会话

### 问题6: 密码哈希验证失败

**原因**: 密码哈希格式不正确或损坏

**解决方案**:
- 使用正确的bcrypt哈希格式
- 重新生成密码哈希
- 确保配置文件中的哈希值完整

---

## 安全建议

### 1. 使用强密码

- 密码长度至少12个字符
- 包含大小写字母、数字和特殊字符
- 避免使用常见密码

### 2. 定期更换密码

- 建议每90天更换一次密码
- 使用密码管理器生成和存储密码

### 3. 保护API密钥

- 不要在代码中硬编码API密钥
- 使用环境变量或配置文件管理密钥
- 定期轮换API密钥

### 4. 启用HTTPS

- 在生产环境中使用HTTPS
- 配置SSL/TLS证书
- 确保所有通信都经过加密

### 5. 监控登录活动

- 记录所有登录尝试
- 监控异常登录行为
- 设置告警机制

---

## 更多资源

- [API契约文档](./contracts/)
- [数据模型文档](./data-model.md)
- [研究文档](./research.md)
- [项目规范](./spec.md)
- [Flask文档](https://flask.palletsprojects.com/)
- [bcrypt文档](https://pypi.org/project/bcrypt/)

---

## 支持

如需帮助或报告问题，请联系开发团队或提交Issue。
