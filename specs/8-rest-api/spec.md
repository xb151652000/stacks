# RESTful API 接口系统规格说明书

## 项目信息

- **项目名称**: Stacks - Download Manager for Anna's Archive
- **规范版本**: 1.0.0
- **创建日期**: 2025-12-25
- **最后更新**: 2025-12-25
- **负责人**: API Team

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

Stacks 需要一个全面的 RESTful API 接口系统，支持 Web 界面、浏览器扩展和外部工具的集成。API 系统提供系统状态查询、队列管理、下载控制、配置管理等功能，并支持多种认证方法。

### 目标

建立一个全面的 RESTful API 接口系统，确保：
1. API 设计符合 RESTful 原则
2. API 提供清晰一致的接口规范
3. API 支持多种认证方法
4. API 提供完善的错误处理和响应格式
5. API 支持速率限制和安全保护
6. API 提供完整的文档和示例

### 范围

本规格说明书涵盖以下 API 功能：
- API 认证和授权
- 系统状态查询
- 队列管理
- 下载控制
- 历史记录管理
- 配置管理
- API 密钥管理
- 子目录管理

### 预期成果

- 实现完整的 RESTful API 接口系统
- 提供清晰的 API 文档和示例
- 支持多种认证方法
- 确保 API 的安全性和可靠性
- 提供完善的错误处理和响应格式

---

## 功能需求

### 功能需求 1: API 认证和授权

**描述**: 实现多种 API 认证方法，支持不同权限级别的访问控制。

**用户故事**: 作为 API 用户，我想要使用不同的认证方法访问 API，以便满足不同的使用场景。

**验收标准**:
- [ ] 支持会话认证（Web UI）
- [ ] 支持 Admin API Key 认证（完全访问权限）
- [ ] 支持 Downloader API Key 认证（受限访问权限）
- [ ] API Key 通过 HTTP Header 传递（X-API-Key）
- [ ] 会话认证通过 Cookie 传递
- [ ] 认证失败返回 401 状态码
- [ ] 权限不足返回 403 状态码
- [ ] 支持认证失败重试机制

**优先级**: 高

**依赖项**: 用户认证系统、安全与隐私保护系统

---

### 功能需求 2: 系统状态查询

**描述**: 提供系统状态查询 API，返回系统健康状态、版本信息和日志。

**用户故事**: 作为系统管理员，我想要查询系统状态，以便监控系统运行情况。

**验收标准**:
- [ ] 提供 `/api/health` 端点（健康检查）
- [ ] 提供 `/api/version` 端点（版本信息）
- [ ] 提供 `/api/logs` 端点（系统日志）
- [ ] 提供 `/api/status` 端点（队列和下载状态）
- [ ] 健康检查返回 `{"status": "ok"}`
- [ ] 版本信息返回 Stacks 和 Tampermonkey 脚本版本
- [ ] 日志端点返回最后 1000 行日志
- [ ] 状态端点返回队列、下载、历史和快速下载信息

**优先级**: 高

**依赖项**: 日志与监控系统、下载队列管理系统

---

### 功能需求 3: 队列管理

**描述**: 提供队列管理 API，支持添加、删除、清空队列等操作。

**用户故事**: 作为 API 用户，我想要通过 API 管理下载队列，以便自动化下载流程。

**验收标准**:
- [ ] 提供 `/api/queue/add` 端点（添加到队列）
- [ ] 提供 `/api/queue/remove` 端点（从队列删除）
- [ ] 提供 `/api/queue/clear` 端点（清空队列）
- [ ] 提供 `/api/queue/pause` 端点（暂停/恢复下载）
- [ ] 提供 `/api/queue/current/cancel` 端点（取消当前下载并重新排队）
- [ ] 提供 `/api/queue/current/remove` 端点（取消当前下载并从队列删除）
- [ ] 添加到队列支持 MD5 和 source 参数
- [ ] 从队列删除支持 MD5 参数

**优先级**: 高

**依赖项**: 下载队列管理系统

---

### 功能需求 4: 历史记录管理

**描述**: 提供历史记录管理 API，支持清空历史和重试失败下载。

**用户故事**: 作为系统管理员，我想要通过 API 管理下载历史，以便清理和重试失败的下载。

**验收标准**:
- [ ] 提供 `/api/history/clear` 端点（清空历史）
- [ ] 提供 `/api/history/retry` 端点（重试失败下载）
- [ ] 清空历史需要 Admin 权限
- [ ] 重试失败下载需要 Admin 权限
- [ ] 重试下载支持 MD5 参数
- [ ] 重试下载将失败项重新加入队列

**优先级**: 高

**依赖项**: 下载历史与重试机制

---

### 功能需求 5: 配置管理

**描述**: 提供配置管理 API，支持获取和更新系统配置。

**用户故事**: 作为系统管理员，我想要通过 API 管理系统配置，以便自动化配置管理。

**验收标准**:
- [ ] 提供 `/api/config` GET 端点（获取配置）
- [ ] 提供 `/api/config` POST 端点（更新配置）
- [ ] 提供 `/api/config/test_key` 端点（测试快速下载密钥）
- [ ] 提供 `/api/config/test_flaresolverr` 端点（测试 FlareSolverr 连接）
- [ ] 配置管理需要 Admin 权限
- [ ] 配置更新支持热重载
- [ ] 配置更新返回成功或错误信息
- [ ] 配置测试返回测试结果

**优先级**: 高

**依赖项**: 配置管理系统

---

### 功能需求 6: API 密钥管理

**描述**: 提供 API 密钥管理 API，支持生成、禁用和测试 API 密钥。

**用户故事**: 作为系统管理员，我想要通过 API 管理 API 密钥，以便控制 API 访问权限。

**验收标准**:
- [ ] 提供 `/api/key` GET 端点（获取 API 密钥）
- [ ] 提供 `/api/key/regenerate` POST 端点（生成新的 Admin 密钥）
- [ ] 提供 `/api/key/disable` POST 端点（禁用 Admin 密钥）
- [ ] 提供 `/api/key/downloader/regenerate` POST 端点（生成新的 Downloader 密钥）
- [ ] 提供 `/api/key/downloader/disable` POST 端点（禁用 Downloader 密钥）
- [ ] 提供 `/api/key/test` POST 端点（测试 API 密钥）
- [ ] API 密钥管理需要会话认证
- [ ] 生成新密钥将使旧密钥失效

**优先级**: 高

**依赖项**: 用户认证系统、安全与隐私保护系统

---

### 功能需求 7: 子目录管理

**描述**: 提供子目录管理 API，支持获取可用的子目录列表。

**用户故事**: 作为 API 用户，我想要获取可用的子目录列表，以便选择下载目标目录。

**验收标准**:
- [ ] 提供 `/api/subdirs` GET 端点（获取子目录列表）
- [ ] 返回所有可用的子目录
- [ ] 支持所有认证方法
- [ ] 返回格式为 JSON 数组
- [ ] 子目录路径以 `/` 开头

**优先级**: 中

**依赖项**: 下载队列管理系统

---

### 功能需求 8: API 错误处理

**描述**: 实现统一的 API 错误处理机制，提供清晰的错误信息和状态码。

**用户故事**: 作为 API 用户，我想要收到清晰的错误信息，以便快速定位和解决问题。

**验收标准**:
- [ ] 使用标准 HTTP 状态码
- [ ] 错误响应包含错误代码和消息
- [ ] 错误响应格式统一
- [ ] 支持错误详情字段
- [ ] 认证失败返回 401 状态码
- [ ] 权限不足返回 403 状态码
- [ ] 资源不存在返回 404 状态码
- [ ] 请求错误返回 400 状态码

**优先级**: 高

**依赖项**: 无

---

### 功能需求 9: API 速率限制

**描述**: 实现 API 速率限制机制，防止滥用和 DDoS 攻击。

**用户故事**: 作为系统管理员，我想要限制 API 访问速率，以便保护系统免受滥用。

**验收标准**:
- [ ] 支持基于 IP 的速率限制
- [ ] 支持基于 API Key 的速率限制
- [ ] 支持基于会话的速率限制
- [ ] 超出限制返回 429 状态码
- [ ] 返回剩余请求次数和重置时间
- [ ] 支持不同端点的不同限制
- [ ] 支持白名单机制
- [ ] 支持自定义限制规则

**优先级**: 高

**依赖项**: 安全与隐私保护系统

---

## 非功能需求

### 性能需求

- [ ] **API 响应时间**: 大部分 API 响应时间必须在 200ms 以内
- [ ] **API 吞吐量**: 支持 1000 请求/秒的并发访问
- [ ] **API 可用性**: API 可用性必须达到 99.9%
- [ ] **API 延迟**: API 延迟必须在 100ms 以内（P95）

### 安全需求

- [ ] **API 认证**: 所有 API 必须经过认证（除健康检查和版本信息）
- [ ] **API 授权**: API 访问必须经过授权检查
- [ ] **API 加密**: API 通信必须使用 HTTPS（生产环境）
- [ ] **API 日志**: 所有 API 请求必须记录到日志
- [ ] **API 输入验证**: 所有 API 输入必须进行验证和清理

### 可用性需求

- [ ] **API 文档**: 所有 API 必须有完整的文档
- [ ] **API 示例**: 所有 API 必须有使用示例
- [ ] **API 错误信息**: 错误信息必须友好且清晰
- [ ] **API 版本控制**: API 必须支持版本控制

### 可维护性需求

- [ ] **代码质量**: Python 代码必须遵循 PEP 8 规范
- [ ] **类型安全**: Python 代码必须使用类型注解
- [ ] **代码文档**: 所有 API 端点必须包含 docstring
- [ ] **测试覆盖**: API 相关代码的测试覆盖率必须达到 90% 以上

---

## 技术规范

### 后端技术

**技术栈**:
- Python 3.11+
- Flask 3.1.2
- Flask-RESTful 0.3.10+
- Flask-Limiter 3.5.0+

**API 架构**:
- RESTful API 设计
- 统一的响应格式
- 统一的错误处理
- 速率限制和安全保护

**数据模型**:
```python
class APIResponse:
    success: bool
    data: Optional[Dict[str, Any]]
    message: Optional[str]
    error: Optional[APIError]

class APIError:
    code: str
    message: str
    details: Optional[Dict[str, Any]]

class HealthResponse:
    status: str

class VersionResponse:
    stacks_version: str
    tampermonkey_version: str

class StatusResponse:
    queue: List[QueueItem]
    current_download: Optional[DownloadItem]
    history: List[HistoryItem]
    fast_download: FastDownloadInfo

class QueueItem:
    md5: str
    added_at: datetime
    status: str

class DownloadItem:
    md5: str
    progress: float
    speed: float
    status: str

class HistoryItem:
    md5: str
    title: str
    status: str
    timestamp: datetime

class FastDownloadInfo:
    enabled: bool
    quota_remaining: Optional[int]
```

**业务逻辑**:
- API 认证和授权
- API 请求处理
- API 响应格式化
- API 错误处理
- API 速率限制

---

### 前端技术

**技术栈**:
- JavaScript (ES6+)
- Fetch API 或 Axios

**API 客户端**:
- 统一的 API 请求封装
- 自动处理认证
- 自动处理错误
- 自动处理速率限制

---

### API 设计原则

**RESTful 设计**:
- 使用合适的 HTTP 方法（GET、POST、PUT、DELETE）
- 使用资源导向的 URL 设计
- 使用标准 HTTP 状态码
- 使用 JSON 作为数据格式

**统一响应格式**:
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "error": null
}
```

**错误响应格式**:
```json
{
  "success": false,
  "data": null,
  "message": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

---

## 接口规范

### API 端点 1: 健康检查

**方法**: GET

**路径**: `/api/health`

**描述**: 检查系统健康状态。

**请求参数**: 无

**认证要求**: 无

**响应格式**:
```json
{
  "status": "ok"
}
```

**状态码**:
- 200: 成功

---

### API 端点 2: 版本信息

**方法**: GET

**路径**: `/api/version`

**描述**: 获取系统版本信息。

**请求参数**: 无

**认证要求**: 无

**响应格式**:
```json
{
  "stacks_version": "1.0.0",
  "tampermonkey_version": "1.0.0"
}
```

**状态码**:
- 200: 成功

---

### API 端点 3: 系统日志

**方法**: GET

**路径**: `/api/logs`

**描述**: 获取系统日志。

**请求参数**: 无

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "data": {
    "logs": "log line 1\nlog line 2\n..."
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

**状态码**:
- 200: 成功
- 401: 未认证
- 403: 权限不足

**速率限制**: 60 次/分钟/用户

---

### API 端点 4: 系统状态

**方法**: GET

**路径**: `/api/status`

**描述**: 获取系统状态信息。

**请求参数**: 无

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "data": {
    "queue": [
      {
        "md5": "1d6fd221af5b9c9bffbd398041013de8",
        "added_at": "2025-12-25T12:00:00Z",
        "status": "pending"
      }
    ],
    "current_download": {
      "md5": "1d6fd221af5b9c9bffbd398041013de8",
      "progress": 50.0,
      "speed": 1024000,
      "status": "downloading"
    },
    "history": [
      {
        "md5": "1d6fd221af5b9c9bffbd398041013de8",
        "title": "Book Title",
        "status": "completed",
        "timestamp": "2025-12-25T12:00:00Z"
      }
    ],
    "fast_download": {
      "enabled": true,
      "quota_remaining": 100
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

**状态码**:
- 200: 成功
- 401: 未认证
- 403: 权限不足

**速率限制**: 60 次/分钟/用户

---

### API 端点 5: 添加到队列

**方法**: POST

**路径**: `/api/queue/add`

**描述**: 添加下载项到队列。

**请求参数**:
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| md5 | string | 是 | 文件的 MD5 哈希值 |
| source | string | 否 | 下载来源（默认: "manual"） |

**认证要求**: 会话认证、Admin API Key 或 Downloader API Key

**响应格式**:
```json
{
  "success": true,
  "message": "Added to queue",
  "data": {
    "md5": "1d6fd221af5b9c9bffbd398041013de8"
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "MD5 哈希值无效"
  }
}
```

**状态码**:
- 200: 成功
- 400: 请求错误
- 401: 未认证

**速率限制**: 60 次/分钟/用户

---

### API 端点 6: 从队列删除

**方法**: POST

**路径**: `/api/queue/remove`

**描述**: 从队列删除下载项。

**请求参数**:
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| md5 | string | 是 | 文件的 MD5 哈希值 |

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "message": "Removed from queue"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "队列项不存在"
  }
}
```

**状态码**:
- 200: 成功
- 400: 请求错误
- 401: 未认证
- 403: 权限不足
- 404: 资源不存在

**速率限制**: 30 次/分钟/用户

---

### API 端点 7: 清空队列

**方法**: POST

**路径**: `/api/queue/clear`

**描述**: 清空下载队列。

**请求参数**: 无

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "message": "Queue cleared"
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

**状态码**:
- 200: 成功
- 401: 未认证
- 403: 权限不足

**速率限制**: 5 次/分钟/用户

---

### API 端点 8: 暂停/恢复下载

**方法**: POST

**路径**: `/api/queue/pause`

**描述**: 暂停或恢复下载工作线程。

**请求参数**: 无

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "message": "Download paused"
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

**状态码**:
- 200: 成功
- 401: 未认证
- 403: 权限不足

**速率限制**: 30 次/分钟/用户

---

### API 端点 9: 取消当前下载并重新排队

**方法**: POST

**路径**: `/api/queue/current/cancel`

**描述**: 取消当前下载并将下载项重新加入队列。

**请求参数**: 无

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "message": "Download cancelled and requeued"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "NO_DOWNLOAD",
    "message": "没有正在进行的下载"
  }
}
```

**状态码**:
- 200: 成功
- 400: 请求错误
- 401: 未认证
- 403: 权限不足

**速率限制**: 30 次/分钟/用户

---

### API 端点 10: 取消当前下载并从队列删除

**方法**: POST

**路径**: `/api/queue/current/remove`

**描述**: 取消当前下载并将下载项从队列删除。

**请求参数**: 无

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "message": "Download cancelled and removed"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "NO_DOWNLOAD",
    "message": "没有正在进行的下载"
  }
}
```

**状态码**:
- 200: 成功
- 400: 请求错误
- 401: 未认证
- 403: 权限不足

**速率限制**: 30 次/分钟/用户

---

### API 端点 11: 获取子目录列表

**方法**: GET

**路径**: `/api/subdirs`

**描述**: 获取可用的子目录列表。

**请求参数**: 无

**认证要求**: 会话认证、Admin API Key 或 Downloader API Key

**响应格式**:
```json
{
  "success": true,
  "data": {
    "subdirectories": ["/Library 1", "/Library 2", "/Users/Alice"]
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

**状态码**:
- 200: 成功
- 401: 未认证

**速率限制**: 60 次/分钟/用户

---

### API 端点 12: 清空历史记录

**方法**: POST

**路径**: `/api/history/clear`

**描述**: 清空下载历史记录。

**请求参数**: 无

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "message": "History cleared"
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

**状态码**:
- 200: 成功
- 401: 未认证
- 403: 权限不足

**速率限制**: 5 次/分钟/用户

---

### API 端点 13: 重试失败下载

**方法**: POST

**路径**: `/api/history/retry`

**描述**: 重试失败的下载。

**请求参数**:
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| md5 | string | 是 | 文件的 MD5 哈希值 |

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "message": "Download added to queue"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "历史记录不存在"
  }
}
```

**状态码**:
- 200: 成功
- 400: 请求错误
- 401: 未认证
- 403: 权限不足
- 404: 资源不存在

**速率限制**: 30 次/分钟/用户

---

### API 端点 14: 获取配置

**方法**: GET

**路径**: `/api/config`

**描述**: 获取系统配置。

**请求参数**: 无

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "data": {
    "server": {
      "host": "0.0.0.0",
      "port": 7788
    },
    "downloads": {
      "delay": 2,
      "retry_count": 3,
      "resume_attempts": 3
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

**状态码**:
- 200: 成功
- 401: 未认证
- 403: 权限不足

**速率限制**: 60 次/分钟/用户

---

### API 端点 15: 更新配置

**方法**: POST

**路径**: `/api/config`

**描述**: 更新系统配置。

**请求参数**: 配置对象（JSON 格式）

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "message": "Configuration updated"
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

**状态码**:
- 200: 成功
- 400: 请求错误
- 401: 未认证
- 403: 权限不足

**速率限制**: 10 次/分钟/用户

---

### API 端点 16: 测试快速下载密钥

**方法**: POST

**路径**: `/api/config/test_key`

**描述**: 测试 Anna's Archive 快速下载密钥的有效性。

**请求参数**:
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| key | string | 是 | 快速下载密钥 |

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "quota_remaining": 100
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_KEY",
    "message": "密钥无效"
  }
}
```

**状态码**:
- 200: 成功
- 400: 请求错误
- 401: 未认证
- 403: 权限不足

**速率限制**: 10 次/分钟/用户

---

### API 端点 17: 测试 FlareSolverr 连接

**方法**: POST

**路径**: `/api/config/test_flaresolverr`

**描述**: 测试 FlareSolverr 连接。

**请求参数**: 无

**认证要求**: 会话认证或 Admin API Key

**响应格式**:
```json
{
  "success": true,
  "data": {
    "connected": true,
    "version": "1.0.0"
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "CONNECTION_FAILED",
    "message": "连接失败"
  }
}
```

**状态码**:
- 200: 成功
- 401: 未认证
- 403: 权限不足

**速率限制**: 10 次/分钟/用户

---

### API 端点 18: 获取 API 密钥

**方法**: GET

**路径**: `/api/key`

**描述**: 获取 API 密钥（仅返回密钥类型，不返回实际密钥）。

**请求参数**: 无

**认证要求**: 会话认证

**响应格式**:
```json
{
  "success": true,
  "data": {
    "admin_key": "enabled",
    "downloader_key": "enabled"
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

**状态码**:
- 200: 成功
- 401: 未认证

**速率限制**: 60 次/分钟/用户

---

### API 端点 19: 生成新的 Admin 密钥

**方法**: POST

**路径**: `/api/key/regenerate`

**描述**: 生成新的 Admin API 密钥（使旧密钥失效）。

**请求参数**: 无

**认证要求**: 会话认证

**响应格式**:
```json
{
  "success": true,
  "message": "Admin key regenerated",
  "data": {
    "key": "new_admin_api_key"
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

**状态码**:
- 200: 成功
- 401: 未认证

**速率限制**: 5 次/小时/用户

---

### API 端点 20: 禁用 Admin 密钥

**方法**: POST

**路径**: `/api/key/disable`

**描述**: 禁用 Admin API 密钥。

**请求参数**: 无

**认证要求**: 会话认证

**响应格式**:
```json
{
  "success": true,
  "message": "Admin key disabled"
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

**状态码**:
- 200: 成功
- 401: 未认证

**速率限制**: 5 次/小时/用户

---

### API 端点 21: 生成新的 Downloader 密钥

**方法**: POST

**路径**: `/api/key/downloader/regenerate`

**描述**: 生成新的 Downloader API 密钥（使旧密钥失效）。

**请求参数**: 无

**认证要求**: 会话认证

**响应格式**:
```json
{
  "success": true,
  "message": "Downloader key regenerated",
  "data": {
    "key": "new_downloader_api_key"
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

**状态码**:
- 200: 成功
- 401: 未认证

**速率限制**: 5 次/小时/用户

---

### API 端点 22: 禁用 Downloader 密钥

**方法**: POST

**路径**: `/api/key/downloader/disable`

**描述**: 禁用 Downloader API 密钥。

**请求参数**: 无

**认证要求**: 会话认证

**响应格式**:
```json
{
  "success": true,
  "message": "Downloader key disabled"
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

**状态码**:
- 200: 成功
- 401: 未认证

**速率限制**: 5 次/小时/用户

---

### API 端点 23: 测试 API 密钥

**方法**: POST

**路径**: `/api/key/test`

**描述**: 测试 API 密钥的有效性并返回密钥类型。

**请求参数**:
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| key | string | 是 | API 密钥 |

**认证要求**: 会话认证、Admin API Key 或 Downloader API Key

**响应格式**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "type": "admin"
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_KEY",
    "message": "密钥无效"
  }
}
```

**状态码**:
- 200: 成功
- 400: 请求错误

**速率限制**: 60 次/分钟/用户

---

## 测试规范

### 单元测试

**测试框架**: pytest

**覆盖率要求**:
- API 相关代码: ≥ 90%
- 整体代码库: ≥ 80%

**测试命名**:
- 使用 `test_<function_name>` 格式
- 使用 Given-When-Then 模式

**示例**:
```python
def test_health_check():
    # Given: 一个运行中的服务器
    client = create_test_client()
    
    # When: 请求健康检查端点
    response = client.get('/api/health')
    
    # Then: 应该返回 200 状态码
    assert response.status_code == 200
    assert response.json == {"status": "ok"}

def test_add_to_queue_success():
    # Given: 一个认证的客户端
    client = create_authenticated_client()
    
    # When: 添加下载项到队列
    response = client.post('/api/queue/add', json={
        "md5": "1d6fd221af5b9c9bffbd398041013de8",
        "source": "manual"
    })
    
    # Then: 应该返回成功
    assert response.status_code == 200
    assert response.json["success"] is True

def test_add_to_queue_unauthorized():
    # Given: 一个未认证的客户端
    client = create_test_client()
    
    # When: 尝试添加下载项到队列
    response = client.post('/api/queue/add', json={
        "md5": "1d6fd221af5b9c9bffbd398041013de8"
    })
    
    # Then: 应该返回 401 状态码
    assert response.status_code == 401
```

---

### 集成测试

**测试范围**:
- API 认证集成
- API 请求处理集成
- API 响应格式化集成
- API 错误处理集成
- API 速率限制集成

**测试要求**:
- 使用测试数据库
- 测试所有 API 端点
- 验证错误处理

---

### 端到端测试

**测试场景**:
- 完整的 API 认证流程
- 完整的队列管理流程
- 完整的下载控制流程
- 完整的配置管理流程

**测试要求**:
- 测试完整的 API 工作流
- 验证响应格式
- 验证数据一致性

---

## 部署规范

### 环境配置

**开发环境**:
- 使用测试数据库
- 使用调试模式
- 使用测试密钥

**测试环境**:
- 使用测试数据库
- 使用生产模式
- 使用测试密钥

**生产环境**:
- 使用生产数据库
- 使用生产模式
- 使用生产密钥
- 启用 HTTPS

---

### API 文档

**文档工具**:
- Swagger/OpenAPI 3.0
- ReDoc

**文档要求**:
- 所有 API 端点必须包含文档
- 所有参数必须包含说明
- 所有响应必须包含示例
- 所有错误必须包含说明

---

### CI/CD 流程

**持续集成**:
- 代码提交后自动运行测试
- API 测试
- 代码质量检查（black, flake8, mypy）

**持续部署**:
- 测试通过后自动部署
- API 测试通过后自动部署
- 部署后必须验证 API 健康状态

---

## 文档要求

### 代码文档

- 所有 API 端点必须包含 docstring（遵循 Google 风格）
- 复杂 API 逻辑必须包含内联注释
- 所有 API 参数必须包含说明注释

### API 文档

- 包含所有 API 端点的详细说明
- 包含所有参数的说明
- 包含所有响应的示例
- 包含所有错误的说明

### 用户文档

- API 使用指南
- API 认证指南
- API 错误处理指南
- API 最佳实践

### 开发文档

- API 架构设计文档
- API 开发指南
- API 测试指南

---

## 风险与依赖

### 技术风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| API 滥用 | 中 | 高 | 实现速率限制和 IP 封禁 |
| API 认证绕过 | 低 | 高 | 使用强认证机制和定期审计 |
| API 性能问题 | 中 | 中 | 实现缓存和负载均衡 |
| API 版本兼容性 | 低 | 中 | 实现版本控制和向后兼容 |

---

### 外部依赖

- Flask 3.1.2: Web 框架
- Flask-RESTful 0.3.10+: RESTful API 支持
- Flask-Limiter 3.5.0+: 速率限制

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

### API 验收

- [ ] 所有 API 端点正常工作
- [ ] API 响应格式正确
- [ ] API 错误处理正常
- [ ] API 速率限制正常

### 文档验收

- [ ] 代码文档完整
- [ ] API 文档完整
- [ ] 部署文档完整
- [ ] 用户文档完整

---

## 附录

### 参考资料

- RESTful API 设计最佳实践
- Flask-RESTful 文档
- Flask-Limiter 文档
- OpenAPI 3.0 规范

### 相关文档

- [项目宪法](../memory/constitution.md)
- [用户认证与授权系统规格说明书](../2-user-auth/spec.md)
- [安全与隐私保护系统规格说明书](../6-security/spec.md)

### 术语表

| 术语 | 定义 |
|------|------|
| RESTful API | 符合 REST 架构风格的 API |
| API Key | 用于 API 认证的密钥 |
| 速率限制 | 限制 API 访问频率的机制 |
| HTTP 状态码 | 表示 HTTP 请求结果的三位数字代码 |
| JSON | 轻量级的数据交换格式 |

---

**本规范必须与项目宪法保持一致，任何偏离必须经过审查和批准。**
