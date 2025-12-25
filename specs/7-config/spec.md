# 配置管理系统规格说明书

## 项目信息

- **项目名称**: Stacks - Download Manager for Anna's Archive
- **规范版本**: 1.0.0
- **创建日期**: 2025-12-25
- **最后更新**: 2025-12-25
- **负责人**: Configuration Team

---

## 宪法合规性检查

本功能规范必须遵循以下宪法原则：

- [x] **代码质量标准**: 明确代码风格、类型注解、错误处理要求
- [x] **测试标准**: 定义测试类型、覆盖率要求、测试命名规范
- [x] **用户体验一致性**: 明确界面风格、响应式设计、交互反馈要求
- [x] **性能要求**: 定义响应时间、并发处理、资源使用标准
- [x] **安全与隐私**: 明确认证授权、数据保护、输入验证要求
- [x] **文档与可维护性**: 定义文档类型、版本控制、依赖管理要求

---

## 功能概述

### 背景

Stacks 是一个容器化的下载队列管理器，需要灵活的配置管理系统来支持各种运行环境和用户需求。配置管理系统负责管理所有系统配置，包括服务器设置、用户认证、下载参数、FlareSolverr 集成等。配置可以通过 Web 界面或直接编辑配置文件进行修改。

### 目标

建立一个全面的配置管理系统，确保：
1. 配置的集中管理和持久化
2. 配置的热重载（无需重启服务器）
3. 配置的验证和错误处理
4. 配置的默认值和自动生成
5. 配置的版本控制和备份
6. 配置的安全存储和访问控制

### 范围

本规格说明书涵盖以下配置管理功能：
- 配置文件管理（YAML 格式）
- 环境变量支持
- Web 界面配置编辑
- 配置验证和错误处理
- 配置热重载
- 配置默认值和自动生成
- 配置备份和恢复

### 预期成果

- 实现灵活的配置管理系统
- 提供用户友好的配置界面
- 支持配置的热重载
- 确保配置的安全性和可靠性
- 提供配置验证和错误提示

---

## 功能需求

### 功能需求 1: 配置文件管理

**描述**: 实现基于 YAML 格式的配置文件管理，支持配置的读取、写入和验证。

**用户故事**: 作为系统管理员，我想要通过配置文件管理系统配置，以便在部署时预设配置参数。

**验收标准**:
- [ ] 配置文件使用 YAML 格式
- [ ] 配置文件位于 `/opt/stacks/config/config.yaml`
- [ ] 支持配置文件的读取和解析
- [ ] 支持配置文件的写入和保存
- [ ] 支持配置文件的验证（类型、范围、格式）
- [ ] 配置文件不存在时自动创建默认配置
- [ ] 配置文件损坏时提供友好的错误提示
- [ ] 支持配置文件的备份和恢复

**优先级**: 高

**依赖项**: 无

---

### 功能需求 2: 环境变量支持

**描述**: 支持通过环境变量设置初始配置，特别是在首次运行时。

**用户故事**: 作为系统管理员，我想要通过环境变量设置初始配置，以便在 Docker 部署时快速配置系统。

**验收标准**:
- [ ] 支持 TZ 环境变量（时区设置）
- [ ] 支持 USERNAME 环境变量（初始用户名）
- [ ] 支持 PASSWORD 环境变量（初始密码）
- [ ] 支持 SOLVERR_URL 环境变量（FlareSolverr URL）
- [ ] 支持 RESET_ADMIN 环境变量（强制密码重置）
- [ ] 支持 FLASK_DEBUG 环境变量（Flask 调试模式）
- [ ] 环境变量仅在首次运行时生效（除非 RESET_ADMIN=true）
- [ ] 环境变量优先级低于配置文件

**优先级**: 高

**依赖项**: 配置文件管理

---

### 功能需求 3: Web 界面配置编辑

**描述**: 提供 Web 界面用于编辑系统配置，支持实时保存和验证。

**用户故事**: 作为系统用户，我想要通过 Web 界面编辑配置，以便无需重启服务器即可修改配置。

**验收标准**:
- [ ] 提供配置编辑界面
- [ ] 支持所有配置项的编辑
- [ ] 配置修改后立即生效（无需重启）
- [ ] 支持配置验证和错误提示
- [ ] 支持配置重置为默认值
- [ ] 支持配置导出和导入
- [ ] 配置修改需要管理员权限
- [ ] 配置修改记录到日志

**优先级**: 高

**依赖项**: 用户认证系统、Web 界面系统

---

### 功能需求 4: 配置验证和错误处理

**描述**: 实现配置验证机制，确保配置的有效性和一致性。

**用户故事**: 作为系统用户，我想要系统验证配置的有效性，以便避免因配置错误导致系统故障。

**验收标准**:
- [ ] 验证配置项的数据类型
- [ ] 验证配置项的取值范围
- [ ] 验证配置项的格式（如 URL、IP 地址）
- [ ] 验证配置项之间的依赖关系
- [ ] 提供友好的错误提示
- [ ] 阻止无效配置的保存
- [ ] 支持配置项的默认值
- [ ] 支持配置项的必填验证

**优先级**: 高

**依赖项**: 配置文件管理、Web 界面配置编辑

---

### 功能需求 5: 配置热重载

**描述**: 实现配置的热重载机制，无需重启服务器即可应用配置更改。

**用户故事**: 作为系统用户，我想要配置更改立即生效，以便无需重启服务器。

**验收标准**:
- [ ] Web 界面配置修改立即生效
- [ ] 配置文件修改后支持热重载
- [ ] 热重载不影响正在运行的下载任务
- [ ] 热重载失败时提供错误提示
- [ ] 热重载支持部分配置项
- [ ] 热重载记录到日志
- [ ] 某些配置项需要重启服务器才能生效（如服务器端口）

**优先级**: 高

**依赖项**: 配置文件管理、Web 界面配置编辑

---

### 功能需求 6: 配置默认值和自动生成

**描述**: 为配置项提供默认值，并自动生成敏感配置（如密码、密钥）。

**用户故事**: 作为系统管理员，我想要系统自动生成默认配置，以便减少配置工作。

**验收标准**:
- [ ] 所有配置项都有默认值
- [ ] 自动生成用户名（admin）
- [ ] 自动生成密码（bcrypt 哈希）
- [ ] 自动生成 API 密钥
- [ ] 自动生成会话密钥
- [ ] 自动生成的密钥使用加密安全的随机数生成器
- [ ] 自动生成的密钥长度符合安全要求
- [ ] 自动生成失败时提供清晰的错误提示

**优先级**: 高

**依赖项**: 配置文件管理、安全与隐私保护系统

---

### 功能需求 7: 配置备份和恢复

**描述**: 实现配置的备份和恢复功能，防止配置丢失或损坏。

**用户故事**: 作为系统管理员，我想要备份和恢复配置，以便在配置错误时快速恢复。

**验收标准**:
- [ ] 支持配置的自动备份
- [ ] 支持配置的手动备份
- [ ] 支持配置的恢复
- [ ] 备份文件包含时间戳
- [ ] 支持多个备份版本
- [ ] 恢复前验证配置的有效性
- [ ] 恢复失败时提供错误提示
- [ ] 支持备份文件的导出和导入

**优先级**: 中

**依赖项**: 配置文件管理

---

## 非功能需求

### 性能需求

- [ ] **配置加载**: 配置加载必须在 100ms 以内完成
- [ ] **配置保存**: 配置保存必须在 200ms 以内完成
- [ ] **配置验证**: 配置验证必须在 50ms 以内完成
- [ ] **热重载**: 热重载必须在 500ms 以内完成

### 安全需求

- [ ] **配置访问**: 配置文件的访问需要管理员权限
- [ ] **敏感数据**: 敏感配置（密码、密钥）必须加密存储
- [ ] **配置验证**: 所有配置必须经过验证
- [ ] **日志记录**: 所有配置修改必须记录到日志
- [ ] **输入验证**: 所有用户输入必须进行验证和清理

### 可用性需求

- [ ] **错误提示**: 所有错误提示必须友好且清晰
- [ ] **默认值**: 所有配置项必须有合理的默认值
- [ ] **配置界面**: 配置界面必须直观易用
- [ ] **配置文档**: 所有配置项必须有详细的说明

### 可维护性需求

- [ ] **代码质量**: Python 代码必须遵循 PEP 8 规范
- [ ] **类型安全**: Python 代码必须使用类型注解
- [ ] **代码文档**: 所有配置相关函数必须包含 docstring
- [ ] **测试覆盖**: 配置相关代码的测试覆盖率必须达到 90% 以上

---

## 技术规范

### 后端技术

**技术栈**:
- Python 3.11+
- Flask 3.1.2
- PyYAML 6.0+
- python-dotenv 1.0.0+

**配置架构**:
- 分层配置设计（默认值、环境变量、配置文件）
- 配置验证和错误处理
- 配置热重载机制
- 配置备份和恢复

**数据模型**:
```python
class ServerConfig:
    host: str
    port: int

class LoginConfig:
    username: Optional[str]
    password: Optional[str]  # bcrypt 哈希
    disable: bool

class APIConfig:
    key: Optional[str]  # bcrypt 哈希
    session_secret: Optional[str]

class DownloadsConfig:
    delay: int
    retry_count: int
    resume_attempts: int

class FastDownloadConfig:
    enabled: bool
    key: Optional[str]

class FlareSolverrConfig:
    enabled: bool
    url: Optional[str]
    timeout: int

class QueueConfig:
    max_history: int

class LoggingConfig:
    level: str

class Config:
    server: ServerConfig
    login: LoginConfig
    api: APIConfig
    downloads: DownloadsConfig
    fast_download: FastDownloadConfig
    flaresolverr: FlareSolverrConfig
    queue: QueueConfig
    logging: LoggingConfig
```

**业务逻辑**:
- 配置文件的读取和解析
- 配置文件的写入和保存
- 配置验证和错误处理
- 配置热重载
- 配置备份和恢复
- 环境变量处理

---

### 前端技术

**技术栈**:
- HTML5
- SCSS（使用 Dracula 主题）
- JavaScript (ES6+)
- Remix Icon

**配置组件**:
- 配置编辑表单
- 配置验证提示
- 配置保存按钮
- 配置重置按钮
- 配置导出/导入按钮

**交互设计**:
- 实时配置验证
- 配置修改提示
- 配置保存确认
- 错误提示显示

---

### 配置文件设计

**配置文件结构**:
```yaml
server:
  host: "0.0.0.0"
  port: 7788

login:
  username: null
  password: null
  disable: false

api:
  key: null
  session_secret: null

downloads:
  delay: 2
  retry_count: 3
  resume_attempts: 3

fast_download:
  enabled: false
  key: null

flaresolverr:
  enabled: false
  url: null
  timeout: 60

queue:
  max_history: 100

logging:
  level: "INFO"
```

**配置验证规则**:
- server.host: 必须是有效的 IP 地址或主机名
- server.port: 必须在 1-65535 范围内
- login.username: 必须是有效的用户名（字母、数字、下划线）
- login.password: 必须是有效的 bcrypt 哈希
- downloads.delay: 必须在 0-300 范围内
- downloads.retry_count: 必须在 0-10 范围内
- downloads.resume_attempts: 必须在 0-10 范围内
- flaresolverr.timeout: 必须在 10-300 范围内
- queue.max_history: 必须在 10-1000 范围内
- logging.level: 必须是 DEBUG、INFO、WARN、ERROR 之一

---

## 接口规范

### API 端点 1: 获取配置

**方法**: GET

**路径**: `/api/v1/config`

**描述**: 获取当前系统配置。

**请求参数**: 无

**响应格式**:
```json
{
  "success": true,
  "data": {
    "server": {
      "host": "0.0.0.0",
      "port": 7788
    },
    "login": {
      "username": "admin",
      "password": null,
      "disable": false
    },
    "api": {
      "key": null,
      "session_secret": null
    },
    "downloads": {
      "delay": 2,
      "retry_count": 3,
      "resume_attempts": 3
    },
    "fast_download": {
      "enabled": false,
      "key": null
    },
    "flaresolverr": {
      "enabled": false,
      "url": null,
      "timeout": 60
    },
    "queue": {
      "max_history": 100
    },
    "logging": {
      "level": "INFO"
    }
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "NOT_AUTHENTICATED",
    "message": "未登录"
  }
}
```

**认证要求**: 需要会话认证

**速率限制**: 60 次/分钟/用户

---

### API 端点 2: 更新配置

**方法**: PUT

**路径**: `/api/v1/config`

**描述**: 更新系统配置。

**请求参数**:
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 7788
  },
  "login": {
    "disable": false
  },
  "downloads": {
    "delay": 2,
    "retry_count": 3,
    "resume_attempts": 3
  },
  "fast_download": {
    "enabled": false,
    "key": "your_fast_download_key"
  },
  "flaresolverr": {
    "enabled": true,
    "url": "http://flaresolverr:8191",
    "timeout": 60
  },
  "queue": {
    "max_history": 100
  },
  "logging": {
    "level": "INFO"
  }
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "配置更新成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "配置验证失败",
    "details": {
      "server.port": "端口号必须在 1-65535 范围内"
    }
  }
}
```

**认证要求**: 需要会话认证

**速率限制**: 10 次/分钟/用户

---

### API 端点 3: 重置配置

**方法**: POST

**路径**: `/api/v1/config/reset`

**描述**: 重置配置为默认值。

**请求参数**: 无

**响应格式**:
```json
{
  "success": true,
  "message": "配置重置成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "NOT_AUTHENTICATED",
    "message": "未登录"
  }
}
```

**认证要求**: 需要会话认证

**速率限制**: 1 次/小时/用户

---

### API 端点 4: 导出配置

**方法**: GET

**路径**: `/api/v1/config/export`

**描述**: 导出当前配置为 YAML 文件。

**请求参数**: 无

**响应格式**: YAML 文件

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "NOT_AUTHENTICATED",
    "message": "未登录"
  }
}
```

**认证要求**: 需要会话认证

**速率限制**: 10 次/分钟/用户

---

### API 端点 5: 导入配置

**方法**: POST

**路径**: `/api/v1/config/import`

**描述**: 从 YAML 文件导入配置。

**请求参数**: YAML 文件

**响应格式**:
```json
{
  "success": true,
  "message": "配置导入成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "配置验证失败"
  }
}
```

**认证要求**: 需要会话认证

**速率限制**: 5 次/分钟/用户

---

### API 端点 6: 备份配置

**方法**: POST

**路径**: `/api/v1/config/backup`

**描述**: 备份当前配置。

**请求参数**: 无

**响应格式**:
```json
{
  "success": true,
  "data": {
    "backup_file": "config_backup_20251225_120000.yaml"
  },
  "message": "配置备份成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "BACKUP_FAILED",
    "message": "配置备份失败"
  }
}
```

**认证要求**: 需要会话认证

**速率限制**: 10 次/分钟/用户

---

### API 端点 7: 恢复配置

**方法**: POST

**路径**: `/api/v1/config/restore`

**描述**: 从备份文件恢复配置。

**请求参数**:
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| backup_file | string | 是 | 备份文件名 |

**响应格式**:
```json
{
  "success": true,
  "message": "配置恢复成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "BACKUP_NOT_FOUND",
    "message": "备份文件不存在"
  }
}
```

**认证要求**: 需要会话认证

**速率限制**: 5 次/分钟/用户

---

## 用户界面设计

### 页面 1: 设置页面 - 配置管理

**描述**: 系统配置管理页面，提供所有配置项的编辑界面。

**布局**:
- 服务器设置
- 登录设置
- 下载设置
- 快速下载设置
- FlareSolverr 设置
- 队列设置
- 日志设置

**组件**:
- 配置表单: 包含所有配置项的输入框
- 配置验证提示: 显示配置验证错误
- 保存按钮: 保存配置更改
- 重置按钮: 重置配置为默认值
- 导出按钮: 导出配置文件
- 导入按钮: 导入配置文件
- 备份按钮: 备份当前配置
- 恢复按钮: 从备份恢复配置

**交互流程**:
1. 用户浏览配置项
2. 用户修改配置项
3. 系统实时验证配置
4. 用户点击保存按钮
5. 系统保存配置并应用更改
6. 显示保存成功提示

**响应式断点**:
- 桌面: > 1024px
- 平板: 768px - 1024px
- 移动: < 768px

---

## 测试规范

### 单元测试

**测试框架**: pytest

**覆盖率要求**:
- 配置相关代码: ≥ 90%
- 整体代码库: ≥ 80%

**测试命名**:
- 使用 `test_<function_name>` 格式
- 使用 Given-When-Then 模式

**示例**:
```python
def test_load_config_success():
    # Given: 一个有效的配置文件
    config_file = create_test_config_file()
    
    # When: 加载配置
    config = load_config(config_file)
    
    # Then: 配置应该成功加载
    assert config is not None
    assert config.server.port == 7788

def test_validate_config_success():
    # Given: 一个有效的配置
    config = create_valid_config()
    
    # When: 验证配置
    errors = validate_config(config)
    
    # Then: 验证应该通过
    assert len(errors) == 0

def test_validate_config_failure():
    # Given: 一个无效的配置
    config = create_invalid_config()
    
    # When: 验证配置
    errors = validate_config(config)
    
    # Then: 验证应该失败
    assert len(errors) > 0
```

---

### 集成测试

**测试范围**:
- 配置加载和保存集成
- 配置验证集成
- 配置热重载集成
- 环境变量处理集成

**测试要求**:
- 使用测试配置文件
- 测试所有配置流程
- 验证错误处理

---

### 端到端测试

**测试场景**:
- 配置编辑和保存流程
- 配置重置流程
- 配置导出和导入流程
- 配置备份和恢复流程

**测试要求**:
- 测试完整的配置工作流
- 验证 UI 交互
- 验证数据一致性

---

## 部署规范

### 环境配置

**开发环境**:
- 使用测试配置文件
- 使用调试模式
- 使用测试密钥

**测试环境**:
- 使用测试配置文件
- 使用生产模式
- 使用测试密钥

**生产环境**:
- 使用生产配置文件
- 使用生产模式
- 使用生产密钥

---

### Docker 配置

**环境变量**:
```yaml
environment:
  - TZ=UTC
  - USERNAME=admin
  - PASSWORD=stacks
  - SOLVERR_URL=flaresolverr:8191
  - RESET_ADMIN=false
  - FLASK_DEBUG=false
```

**卷挂载**:
```yaml
volumes:
  - /path/to/config:/opt/stacks/config
```

---

### CI/CD 流程

**持续集成**:
- 代码提交后自动运行测试
- 配置验证测试
- 代码质量检查（black, flake8, mypy）

**持续部署**:
- 测试通过后自动部署
- 配置验证通过后自动部署
- 部署后必须验证服务健康

---

## 文档要求

### 代码文档

- 所有配置相关函数必须包含 docstring（遵循 Google 风格）
- 复杂配置逻辑必须包含内联注释
- 所有配置项必须包含说明注释

### 配置文档

- 包含所有配置项的详细说明
- 包含配置项的默认值
- 包含配置项的验证规则
- 包含配置示例

### 用户文档

- 配置管理指南
- 配置项说明
- 配置最佳实践
- 故障排除指南

### 开发文档

- 配置架构设计文档
- 配置开发指南
- 配置测试指南

---

## 风险与依赖

### 技术风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 配置文件损坏 | 低 | 高 | 实现配置备份和恢复 |
| 配置验证失败 | 中 | 中 | 提供友好的错误提示和默认值 |
| 热重载失败 | 低 | 中 | 实现回滚机制 |
| 环境变量冲突 | 低 | 低 | 明确环境变量优先级 |

---

### 外部依赖

- PyYAML 6.0+: YAML 解析
- python-dotenv 1.0.0+: 环境变量处理

---

## 验收标准

### 功能验收

- [ ] 所有功能需求已实现
- [ ] 所有功能测试通过
- [ ] 所有用户场景验证通过

### 非功能验收

- [ ] 性能指标达标
- [ ] 安全测试通过
- [ ] 可用性测试通过
- [ ] 兼容性测试通过

### 配置验收

- [ ] 配置文件格式正确
- [ ] 配置验证规则完整
- [ ] 配置热重载正常工作
- [ ] 配置备份和恢复正常工作

### 文档验收

- [ ] 代码文档完整
- [ ] 配置文档完整
- [ ] 部署文档完整
- [ ] 用户文档完整

---

## 附录

### 参考资料

- YAML 规范
- Flask 配置最佳实践
- Docker 环境变量最佳实践

### 相关文档

- [项目宪法](../memory/constitution.md)
- [安全与隐私保护系统规格说明书](../6-security/spec.md)
- [用户认证与授权系统规格说明书](../2-user-auth/spec.md)

### 术语表

| 术语 | 定义 |
|------|------|
| YAML | 一种人类可读的数据序列化格式 |
| 热重载 | 在不重启服务的情况下重新加载配置 |
| 环境变量 | 操作系统级别的配置变量 |
| 配置验证 | 验证配置的有效性和一致性 |
| 配置备份 | 保存配置的副本以防止数据丢失 |

---

**本规范必须与项目宪法保持一致，任何偏离必须经过审查和批准。**
