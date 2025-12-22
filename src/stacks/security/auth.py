"""
Stacks安全认证模块
此模块提供用户认证、授权和安全防护功能，包括：
- 密码哈希和验证
- 登录速率限制
- 会话管理
- API密钥验证
- 权限控制装饰器
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
import bcrypt
from functools import wraps

from flask import session, request, jsonify, redirect, url_for, current_app

logger = logging.getLogger("auth")

# ================================
# 内存中的登录尝试和锁定跟踪
# ================================
# 注意：这些数据存储在内存中，服务器重启后会丢失
# 对于生产环境，可以考虑使用Redis等外部存储
login_attempts: dict[str, list[datetime]] = {}  # IP地址 -> 登录尝试时间列表
login_lockouts: dict[str, datetime] = {}        # IP地址 -> 锁定到期时间

def generate_secret_key():
    """
    生成192位（32字符）的密钥
    使用加密安全的随机数生成器创建密钥，用于API密钥和会话密钥。
    
    Returns:
        str: 32字符的随机密钥，包含字母、数字、下划线和连字符
    """
    alphabet = string.ascii_letters + string.digits + "-_"
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def hash_password(password):
    """
    使用bcrypt哈希密码
    bcrypt是一种自适应哈希函数，专门用于密码哈希，包含盐值以防止彩虹表攻击。
    
    Args:
        password (str): 明文密码
        
    Returns:
        str: bcrypt哈希值（60字符）
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """
    验证密码是否匹配bcrypt哈希
    安全地比较明文密码和存储的哈希值。
    
    Args:
        password (str): 要验证的明文密码
        hashed (str): 存储的bcrypt哈希值
        
    Returns:
        bool: 密码是否匹配
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        # 如果哈希格式无效或其他错误，返回False而不是抛出异常
        return False

def is_valid_bcrypt_hash(hash_string):
    """
    检查字符串是否看起来像有效的bcrypt哈希
    通过检查前缀和长度来快速验证哈希格式。
    
    Args:
        hash_string (str): 要检查的字符串
        
    Returns:
        bool: 是否是有效的bcrypt哈希格式
    """
    if not hash_string:
        return False
    # bcrypt哈希以$2a$、$2b$或$2y$开头，长度为60字符
    return (hash_string.startswith(('$2a$', '$2b$', '$2y$')) and len(hash_string) == 60)

def check_rate_limit(ip):
    """
    检查IP是否被速率限制
    实现登录尝试速率限制，防止暴力破解攻击。
    清理过期的尝试记录和锁定，然后检查当前IP的状态。
    
    Args:
        ip (str): 客户端IP地址
        
    Returns:
        tuple: (是否允许, 消息) - 如果不允许，消息包含原因
    """
    # 检查是否被锁定
    if ip in login_lockouts:
        lockout_until = login_lockouts[ip]
        if datetime.now() < lockout_until:
            # 仍在锁定期内
            remaining = int((lockout_until - datetime.now()).total_seconds() / 60)
            return False, f"尝试次数过多。请在{remaining}分钟后重试。"
        else:
            # 锁定已过期，清理记录
            del login_lockouts[ip]
            if ip in login_attempts:
                del login_attempts[ip]
    
    # 初始化当前IP的尝试记录
    if ip not in login_attempts:
        login_attempts[ip] = []
    
    # 清理所有IP的过期尝试记录（超过10分钟的）
    cutoff = datetime.now() - timedelta(minutes=10)
    expired_ips = []
    for tracked_ip, attempts in login_attempts.items():
        login_attempts[tracked_ip] = [t for t in attempts if t > cutoff]
        if not login_attempts[tracked_ip]:  # 没有最近的尝试
            expired_ips.append(tracked_ip)

    # 移除没有最近尝试的IP
    for tracked_ip in expired_ips:
        del login_attempts[tracked_ip]

    # 清理过期的锁定记录
    expired_lockouts = [tracked_ip for tracked_ip, until in login_lockouts.items() if datetime.now() >= until]
    for tracked_ip in expired_lockouts:
        del login_lockouts[tracked_ip]

    # 如果当前IP被清理了，重新初始化
    if ip not in login_attempts:
        login_attempts[ip] = []
    
    # 检查尝试次数是否超过限制
    if len(login_attempts[ip]) >= 5:
        # 锁定10分钟
        login_lockouts[ip] = datetime.now() + timedelta(minutes=10)
        return False, "尝试次数过多。请在10分钟后重试。"
    
    return True, None

def record_failed_attempt(ip):
    """
    记录失败的登录尝试
    在速率限制系统中记录一次失败的登录尝试。
    
    Args:
        ip (str): 客户端IP地址
    """
    if ip not in login_attempts:
        login_attempts[ip] = []
    login_attempts[ip].append(datetime.now())

def clear_attempts(ip):
    """
    成功登录后清除IP的登录尝试记录
    重置该IP的安全状态，允许正常的后续登录。
    
    Args:
        ip (str): 客户端IP地址
    """
    if ip in login_attempts:
        del login_attempts[ip]
    if ip in login_lockouts:
        del login_lockouts[ip]

def require_login(f):
    """Require a logged-in session for HTML pages (index, etc.)."""
    @wraps(f)    
    def wrapper(*args, **kwargs):
        cfg = current_app.stacks_config
        disable_auth = cfg.get("login", "disable")

        if disable_auth:
            return f(*args, **kwargs)
        
        if not session.get("logged_in"):
            # Note: blueprint name is "api", endpoint is "login"
            return redirect(url_for("api.login"))
        return f(*args, **kwargs)
    return wrapper

def validate_api_key(provided_key):
    """
    Validate an API key and return its type.
    Returns: (is_valid: bool, key_type: str | None)
    - "admin": Full access admin key
    - "downloader": Limited downloader key
    - None: Invalid key
    """
    if not provided_key:
        return False, None

    cfg = current_app.stacks_config
    admin_key = cfg.get("api", "key")
    downloader_key = cfg.get("api", "downloader_key", default=None)

    if provided_key == admin_key:
        return True, "admin"
    elif downloader_key and provided_key == downloader_key:
        return True, "downloader"
    else:
        return False, None

def require_auth(f):
    """
    Require EITHER:
    - A logged-in session (web UI), OR
    - A valid X-API-Key / ?api_key=... token (external tools).
    - The authentication to be disabled in the config

    Accepts both admin and downloader keys.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Allow for disabled auth altogether
        cfg = current_app.stacks_config
        disable_auth = cfg.get("login", "disable")

        if disable_auth:
            return f(*args, **kwargs)
        # Web session takes precedence
        if session.get("logged_in"):
            return f(*args, **kwargs)

        # API key path
        provided_key = (
            request.headers.get("X-API-Key")
            or request.args.get("api_key")
        )

        is_valid, key_type = validate_api_key(provided_key)
        if is_valid:
            # Store key type in request context for permission checking
            request.key_type = key_type
            return f(*args, **kwargs)

        return (
            jsonify({"success": False, "error": "Authentication required"}),
            401,
        )
    return wrapper

def require_auth_with_permissions(allow_downloader=False):
    """
    Decorator that checks authentication and permissions.

    Args:
        allow_downloader: If True, downloader keys are allowed. If False, only admin keys/sessions.

    Usage:
        @require_auth_with_permissions(allow_downloader=True)
        def endpoint_that_downloader_can_access():
            ...

        @require_auth_with_permissions(allow_downloader=False)
        def admin_only_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Allow for disabled auth altogether
            cfg = current_app.stacks_config
            disable_auth = cfg.get("login", "disable")

            if disable_auth:
                return f(*args, **kwargs)

            # Web session takes precedence (always has admin rights)
            if session.get("logged_in"):
                return f(*args, **kwargs)

            # API key path
            provided_key = (
                request.headers.get("X-API-Key")
                or request.args.get("api_key")
            )

            is_valid, key_type = validate_api_key(provided_key)

            if not is_valid:
                return (
                    jsonify({"success": False, "error": "Authentication required"}),
                    401,
                )

            # Check permissions
            if key_type == "admin":
                # Admin always has access
                return f(*args, **kwargs)
            elif key_type == "downloader":
                if allow_downloader:
                    return f(*args, **kwargs)
                else:
                    return (
                        jsonify({"success": False, "error": "Insufficient permissions. Admin access required."}),
                        403,
                    )

            # Shouldn't reach here, but just in case
            return (
                jsonify({"success": False, "error": "Authentication required"}),
                401,
            )
        return wrapper
    return decorator

def require_session_only(f):
    """Require *only* a logged-in session (UI-only endpoints)."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Allow for disabled auth altogether
        cfg = current_app.stacks_config
        disable_auth = cfg.get("login", "disable")

        if disable_auth:
            return f(*args, **kwargs)
        
        if session.get("logged_in"):
            return f(*args, **kwargs)
        return (
            jsonify(
                {"success": False, "error": "Session authentication required"}
            ),
            401,
        )
    return wrapper