# 用户认证与授权系统 - 研究文档

## 项目信息

- **项目名称**: Stacks - Anna's Archive 下载管理器
- **功能模块**: 用户认证与授权系统
- **文档版本**: 1.0.0
- **创建日期**: 2025-12-26
- **规范文档**: `specs/2-user-auth/spec.md`

---

## 研究目标

本研究文档旨在分析用户认证与授权系统的技术实现方案，包括：
1. 现有代码库的认证功能现状
2. 技术选型与架构设计
3. 实现方案与最佳实践
4. 潜在风险与缓解措施

---

## 现有代码库分析

### 已实现的认证功能

通过分析现有代码，项目已经实现了部分认证功能：

#### 1. 密码哈希与验证 (`src/stacks/security/auth.py`)

**已实现功能**:
- `hash_password()`: 使用 bcrypt 算法哈希密码
- `verify_password()`: 验证密码是否匹配哈希值
- `is_valid_bcrypt_hash()`: 检查字符串是否为有效的 bcrypt 哈希

**技术细节**:
```python
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

**符合规范**: ✅ 符合规范要求（bcrypt 哈希，至少 12 轮）

#### 2. API 密钥管理 (`src/stacks/api/keys.py`)

**已实现功能**:
- `api_key_regenerate()`: 重新生成 Admin API Key
- `api_key_disable()`: 禁用 Admin API Key
- `api_key_downloader_regenerate()`: 重新生成 Downloader API Key
- `api_key_downloader_disable()`: 禁用 Downloader API Key
- `api_key_info()`: 获取 API 密钥信息
- `api_key_test()`: 测试 API 密钥有效性

**技术细节**:
- 使用 `generate_secret_key()` 生成 32 字符的随机密钥
- 密钥存储在 YAML 配置文件中
- API 密钥通过 HTTP 请求头 `X-API-Key` 或查询参数 `api_key` 传递

**符合规范**: ✅ 符合规范要求

#### 3. 认证装饰器 (`src/stacks/security/auth.py`)

**已实现功能**:
- `require_login()`: 要求 Web 会话认证（用于 HTML 页面）
- `require_auth()`: 要求会话或 API Key 认证
- `require_auth_with_permissions()`: 要求认证并检查权限（支持 allow_downloader 参数）
- `require_session_only()`: 仅要求会话认证（用于 UI 端点）

**技术细节**:
- 支持禁用认证功能（通过 `login.disable` 配置）
- Web 会话优先于 API Key 认证
- 支持 Admin 和 Downloader 两种 API Key 类型

**符合规范**: ✅ 符合规范要求

#### 4. 登录速率限制 (`src/stacks/security/auth.py`)

**已实现功能**:
- `check_rate_limit()`: 检查 IP 是否被速率限制
- `record_failed_attempt()`: 记录失败的登录尝试
- `clear_attempts()`: 清除登录尝试记录

**技术细节**:
- 5 次失败尝试后锁定 10 分钟
- 使用内存存储（`login_attempts` 和 `login_lockouts` 字典）
- 自动清理过期的尝试记录和锁定

**符合规范**: ✅ 符合规范要求（5 次失败锁定 10 分钟）

#### 5. 密码重置机制 (`src/stacks/main.py`)

**已实现功能**:
- 通过环境变量 `RESET_ADMIN=true` 启用密码重置
- 通过环境变量 `PASSWORD` 指定新密码
- 密码重置在容器启动时生效

**符合规范**: ✅ 符合规范要求

---

### 缺失的功能

#### 1. 用户登录 API 端点

**状态**: ❌ 未实现

**规范要求**:
- POST `/api/login`
- 接收用户名和密码
- 使用 bcrypt 验证密码哈希
- 验证成功后创建会话
- 使用 HTTPOnly 和 Secure Cookie
- 支持禁用登录功能

**实现建议**:
```python
@api_bp.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # 检查速率限制
    ip = request.remote_addr
    allowed, message = check_rate_limit(ip)
    if not allowed:
        return jsonify({'success': False, 'error': message}), 429
    
    # 验证凭据
    config = current_app.stacks_config
    stored_username = config.get('login', 'username')
    stored_password = config.get('login', 'password')
    
    if username == stored_username and verify_password(password, stored_password):
        # 创建会话
        session['logged_in'] = True
        session['username'] = username
        clear_attempts(ip)
        return jsonify({'success': True, 'message': '登录成功'})
    else:
        record_failed_attempt(ip)
        return jsonify({'success': False, 'error': '用户名或密码错误'}), 401
```

#### 2. 用户登出 API 端点

**状态**: ❌ 未实现

**规范要求**:
- POST `/api/logout`
- 销毁用户会话

**实现建议**:
```python
@api_bp.route('/api/logout', methods=['POST'])
@require_session_only
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'success': True, 'message': '登出成功'})
```

#### 3. 密码修改功能

**状态**: ❌ 未实现

**规范要求**:
- POST `/api/password/change`
- 接收当前密码、新密码、确认密码
- 验证当前密码
- 更新密码哈希

**实现建议**:
```python
@api_bp.route('/api/password/change', methods=['POST'])
@require_session_only
def change_password():
    """修改密码"""
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    # 验证新密码
    if new_password != confirm_password:
        return jsonify({'success': False, 'error': '两次输入的密码不一致'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'error': '密码长度至少为 6 个字符'}), 400
    
    # 验证当前密码
    config = current_app.stacks_config
    stored_password = config.get('login', 'password')
    
    if not verify_password(current_password, stored_password):
        return jsonify({'success': False, 'error': '当前密码错误'}), 400
    
    # 更新密码
    hashed_password = hash_password(new_password)
    config.set('login', 'password', value=hashed_password)
    config.save()
    
    return jsonify({'success': True, 'message': '密码已修改'})
```

#### 4. 前端登录界面

**状态**: ❌ 未实现

**规范要求**:
- 登录页面（居中登录表单）
- Logo 和标题
- 用户名和密码输入框
- 登录按钮
- 错误提示区域
- 使用 Dracula 主题配色

**实现建议**:
- 创建 `templates/login.html` 模板
- 使用 Remix Icon 图标库
- 实现响应式设计（桌面、平板、移动）
- 添加加载指示器和错误提示

---

## 技术选型分析

### 后端技术栈

| 技术 | 版本 | 用途 | 评估 |
|------|------|------|------|
| Python | 3.11+ | 主要编程语言 | ✅ 符合规范 |
| Flask | 3.1.2 | Web 框架 | ✅ 符合规范 |
| bcrypt | - | 密码哈希 | ✅ 符合规范 |
| Flask-Session | - | 会话管理 | ⚠️ 需要集成 |
| PyYAML | - | 配置管理 | ✅ 已使用 |

**评估结果**: 技术栈符合规范要求，需要集成 Flask-Session 进行会话管理。

### 前端技术栈

| 技术 | 用途 | 评估 |
|------|------|------|
| HTML5 | 页面结构 | ✅ 符合规范 |
| SCSS | 样式表（Dracula 主题） | ✅ 符合规范 |
| JavaScript (ES6+) | 交互逻辑 | ✅ 符合规范 |
| Remix Icon | 图标库 | ✅ 符合规范 |

**评估结果**: 技术栈符合规范要求。

---

## 架构设计

### 认证流程

#### Web 界面登录流程

```
用户输入凭据
    ↓
提交到 /api/login
    ↓
检查速率限制
    ↓
验证用户名和密码
    ↓
创建会话 (HTTPOnly Cookie)
    ↓
跳转到主界面
```

#### API Key 认证流程

```
API 请求
    ↓
检查 X-API-Key 请求头
    ↓
验证 API Key 有效性
    ↓
确定 API Key 类型 (Admin/Downloader)
    ↓
检查权限
    ↓
允许或拒绝访问
```

### 权限模型

| 认证方式 | 权限范围 | 适用场景 |
|----------|----------|----------|
| Web 会话 | 完全访问权限 | Web UI 操作 |
| Admin API Key | 完全访问权限 | 自动化脚本 |
| Downloader API Key | 受限访问权限 | 浏览器扩展 |

### 安全措施

1. **密码安全**
   - bcrypt 哈希（至少 12 轮）
   - 每个密码使用唯一盐值
   - 密码长度至少 6 个字符

2. **会话安全**
   - HTTPOnly Cookie（防止 XSS）
   - Secure Cookie（仅 HTTPS）
   - SameSite 属性（防止 CSRF）
   - 会话过期时间（默认 24 小时）

3. **API 密钥安全**
   - 32 字符强随机密钥
   - 支持禁用和重新生成
   - 通过请求头传递（避免日志记录）

4. **速率限制**
   - 5 次失败尝试后锁定 10 分钟
   - 基于 IP 地址的跟踪
   - 自动清理过期记录

---

## 实现方案

### Phase 1: 数据模型

**目标**: 定义认证相关的数据模型和配置结构。

**输出**: `data-model.md`

**内容**:
- 用户配置模型
- API 配置模型
- 会话配置模型
- 配置文件结构

### Phase 2: API 契约

**目标**: 定义所有认证相关的 API 端点。

**输出**: `contracts/` 目录

**内容**:
- `/api/login` - 用户登录
- `/api/logout` - 用户登出
- `/api/password/change` - 修改密码
- `/api/key` - 获取 API 密钥
- `/api/key/regenerate` - 重新生成 Admin API Key
- `/api/key/disable` - 禁用 Admin API Key
- `/api/key/downloader/regenerate` - 重新生成 Downloader API Key
- `/api/key/downloader/disable` - 禁用 Downloader API Key
- `/api/key/test` - 测试 API 密钥

### Phase 3: 前端实现

**目标**: 实现登录界面和设置页面的认证部分。

**输出**: `quickstart.md`

**内容**:
- 登录页面实现
- 设置页面认证部分实现
- 交互流程说明
- 响应式设计说明

---

## 潜在风险与缓解措施

### 风险 1: bcrypt 性能问题

**可能性**: 低  
**影响**: 中

**缓解措施**:
- 使用合理的哈希轮数（12 轮）
- 监控登录响应时间
- 考虑使用异步验证

### 风险 2: 会话劫持

**可能性**: 低  
**影响**: 高

**缓解措施**:
- 使用 HTTPOnly 和 Secure Cookie
- 使用 SameSite 属性
- 定期轮换会话密钥
- 实现会话固定保护

### 风险 3: API 密钥泄露

**可能性**: 中  
**影响**: 高

**缓解措施**:
- 提供密钥禁用和重新生成功能
- 不在日志中记录 API 密钥
- 使用 HTTPS 传输
- 实施速率限制

### 风险 4: 密码暴力破解

**可能性**: 中  
**影响**: 中

**缓解措施**:
- 实施速率限制（5 次失败锁定 10 分钟）
- 使用强哈希算法（bcrypt）
- 强制密码复杂度要求

### 风险 5: 内存存储的速率限制数据丢失

**可能性**: 中  
**影响**: 低

**缓解措施**:
- 服务器重启后速率限制重置（可接受）
- 未来可考虑使用 Redis 等外部存储

---

## 测试策略

### 单元测试

**覆盖率要求**:
- 认证授权逻辑: ≥ 95%
- 整体代码库: ≥ 80%

**测试框架**: pytest

**测试示例**:
```python
def test_login_success():
    """测试登录成功"""
    # Given: 一个有效的用户凭据
    username = "admin"
    password = "correct_password"
    
    # When: 执行登录
    result = auth.login(username, password)
    
    # Then: 登录应该成功
    assert result.success is True
    assert result.session_id is not None

def test_login_rate_limit():
    """测试登录速率限制"""
    # Given: 5 次失败的登录尝试
    for _ in range(5):
        auth.login("admin", "wrong_password")
    
    # When: 尝试第 6 次登录
    result = auth.login("admin", "correct_password")
    
    # Then: 应该被速率限制
    assert result.success is False
    assert "尝试次数过多" in result.error
```

### 集成测试

**测试范围**:
- 认证模块与配置模块的交互
- API 端点集成
- 会话管理集成

### 端到端测试

**测试场景**:
- 用户登录成功流程
- 用户登录失败流程
- API Key 生成和使用流程
- 密码修改流程
- API Key 禁用流程

### 性能测试

**测试指标**:
- 登录验证响应时间 < 500ms（P95）
- API Key 验证响应时间 < 200ms（P95）
- 支持 50+ 并发认证请求

**测试工具**: Locust, pytest-benchmark

---

## 部署考虑

### 环境变量

```yaml
environment:
  - USERNAME=admin
  - PASSWORD=stacks
  - RESET_ADMIN=false
```

### Docker 配置

**Dockerfile**: 使用项目现有的 Dockerfile

**docker-compose.yml**:
```yaml
services:
  stacks:
    image: stacks:latest
    environment:
      - USERNAME=admin
      - PASSWORD=stacks
      - RESET_ADMIN=false
    ports:
      - "8080:8080"
```

### CI/CD 流程

**持续集成**:
- 代码提交后自动运行测试
- 代码质量检查（black, flake8, mypy）
- 构建和部署到测试环境

**持续部署**:
- 测试通过后自动部署到生产环境
- 部署前必须通过所有检查
- 部署后必须验证服务健康

---

## 参考资料

- [Flask 文档](https://flask.palletsprojects.com/)
- [bcrypt 文档](https://pypi.org/project/bcrypt/)
- [OWASP 认证备忘单](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Flask-Session 文档](https://flask-session.readthedocs.io/)
- [PEP 8 - Style Guide for Python Code](https://peps8.org/)

---

## 结论

通过分析现有代码库，项目已经实现了大部分认证功能，包括密码哈希、API 密钥管理、认证装饰器和登录速率限制。需要补充的主要功能包括：

1. 用户登录 API 端点
2. 用户登出 API 端点
3. 密码修改功能
4. 前端登录界面

技术选型符合规范要求，架构设计合理，安全措施完善。下一步将进行详细的设计和实现规划。
