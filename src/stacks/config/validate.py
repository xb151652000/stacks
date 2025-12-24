import os
import logging
from pathlib import Path
from stacks.constants import (
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    LOG_LEVELS,
    INCLUDE_HASH_OPTIONS,
    RE_SECRET_KEY,
    RE_IPV4,
    RE_IPV6,
    RE_URL,
    PROJECT_ROOT,
    RESERVED_PATHS,
)

from stacks.security.auth import (
    generate_secret_key,
    hash_password,
    is_valid_bcrypt_hash,
)

logger = logging.getLogger('config')

def _validate_path(value, path_type="incomplete_folder", incomplete_folder_path=None):
    """
    验证并规范化路径字符串
    
    这个函数用于验证用户配置的路径是否合法，主要功能包括：
    1. 检查路径是否为字符串
    2. 去除路径两端的空白字符
    3. 检查路径是否为空或只有斜杠
    4. 规范化路径分隔符（统一使用正斜杠）
    5. 处理路径中的 ".."（上级目录）和 "."（当前目录）
    6. 检查路径是否使用了保留路径
    7. 验证父目录是否可创建
    
    Args:
        value: 需要验证的路径字符串
        path_type: 路径类型，可以是 "incomplete_folder"（未完成文件夹）或 "subdirectory"（子目录）
        incomplete_folder_path: 未完成文件夹的路径，用于验证子目录时检查冲突
    
    Returns:
        str: 规范化后的路径字符串，格式为 "/path/to/folder"（无尾部斜杠）
    
    Raises:
        ValueError: 当路径验证失败时抛出异常，包含具体的错误信息
    """
    if not isinstance(value, str):
        raise ValueError("Path must be a string")

    value = value.strip()

    if not value or value == '/':
        raise ValueError("Path cannot be empty or just '/'")

    normalized = Path(value.replace('\\', '/'))
    parts = []

    for part in normalized.parts:
        if part == '..':
            if parts:
                parts.pop()
        elif part != '.' and part != '/' and part != '\\':
            parts.append(part)

    if not parts:
        raise ValueError("Path cannot be empty after normalization")

    normalized_path = '/' + '/'.join(parts)

    if path_type == "incomplete_folder":
        for reserved in RESERVED_PATHS:
            if normalized_path == reserved:
                raise ValueError(f"Path cannot be {reserved} (reserved)")
            if normalized_path.startswith(reserved + '/'):
                raise ValueError(f"Path cannot be a subdirectory of {reserved} (reserved)")
    elif path_type == "subdirectory":
        if incomplete_folder_path and normalized_path == incomplete_folder_path:
            raise ValueError(f"Path cannot be the same as incomplete folder: {incomplete_folder_path}")

    try:
        test_path = PROJECT_ROOT / normalized_path.lstrip('/')
        test_path.parent.mkdir(parents=True, exist_ok=True)
        if not test_path.parent.is_dir():
            raise ValueError(f"Parent directory does not exist and cannot be created")
    except Exception as e:
        raise ValueError(f"Invalid path: {str(e)}")

    return normalized_path

def _validate(config: dict, schema: dict) -> dict:
    """
    主验证函数，根据配置模式验证用户配置
    
    这个函数是配置验证的核心入口，它会遍历配置模式（schema）中的每个部分和键，
    对用户提供的配置进行验证和规范化处理
    
    Args:
        config: 用户提供的配置字典，格式如 {"section": {"key": value}}
        schema: 配置模式字典，定义了每个配置项的验证规则
    
    Returns:
        dict: 经过验证和规范化后的配置字典
    
    工作流程：
        1. 遍历 schema 中的每个配置部分（section）
        2. 获取用户配置中对应的部分，如果不存在则使用空字典
        3. 遍历该部分中的每个配置键
        4. 调用 _validate_value 函数验证每个配置值
        5. 将验证后的值存入 normalized 字典并返回
    """
    logger.debug("Validating config.")
    normalized = {}

    for section, section_schema in schema.items():
        user_section = config.get(section, {})
        if isinstance(section_schema, dict):
            normalized[section] = {}

            for key, rules in section_schema.items():
                value = user_section.get(key, None)
                normalized[section][key] = _validate_value(value, rules, key, section, normalized)
        else:
            logging.debug(f"Error '{key}', no such key in schema.")
    logger.debug("Config validated.")
    return normalized

def _apply_default(default, key, old_value):
    """
    应用默认值处理函数
    
    当用户提供的配置值验证失败时，这个函数会根据默认值的类型
    生成相应的默认值或从环境变量中获取值
    
    Args:
        default: 默认值的类型标识，可以是：
            - "GENERATE_SECRET_KEY": 生成新的密钥
            - "HASH_PASSWORD": 使用默认密码并哈希
            - "USERNAME": 使用默认用户名
            - "FLARESOLVERR": 使用环境变量中的 Solr URL
        key: 配置项的键名，用于日志记录
        old_value: 用户提供的原始值
    
    Returns:
        根据默认值类型生成的默认值
    
    处理逻辑：
        - GENERATE_SECRET_KEY: 调用 generate_secret_key() 生成 32 位密钥
        - HASH_PASSWORD: 从环境变量获取密码，如果没有则使用 DEFAULT_PASSWORD，然后进行哈希
        - USERNAME: 从环境变量获取用户名，如果没有则使用 DEFAULT_USERNAME
        - FLARESOLVERR: 从环境变量获取 SOLVERR_URL
    """
    match default:
        case "GENERATE_SECRET_KEY":
            logger.info(f"Generated new 32-bit key for {key}")
            return generate_secret_key()
        case "HASH_PASSWORD":
            logger.warning("Valid password missing, resetting to default.")
            default = os.environ.get('PASSWORD', DEFAULT_PASSWORD)
            return hash_password(default)
        case "USERNAME":
            logger.warning(f"Username '{old_value}' is invalid. Resetting back to '{DEFAULT_USERNAME}'.")
            default = os.environ.get('USERNAME', DEFAULT_USERNAME)
        case "FLARESOLVERR":
            default = os.environ.get("SOLVERR_URL", None)
            logger.warning(f"FlareSolverr URL is invalid Resetting back to '{default}'.")
    return default

def _validate_value(value, rules, key, section=None, normalized=None):
    """
    验证单个配置值
    
    这个函数根据配置规则验证单个配置值是否合法，支持多种数据类型和验证规则
    
    Args:
        value: 需要验证的配置值
        rules: 验证规则字典，包含以下可能的键：
            - types: 允许的类型列表
            - default: 默认值（当验证失败时使用）
            - min: 最小值（适用于整数）
            - max: 最大值（适用于整数）
            - max_length: 最大长度（适用于字符串）
        key: 配置项的键名，用于日志记录
        section: 配置项所属的配置部分，用于获取相关配置
        normalized: 已验证的配置字典，用于获取相关配置
    
    Returns:
        验证通过后的值，或应用默认值后的值
    
    支持的类型验证：
        - STRING: 字符串类型，检查最大长度
        - INTEGER: 整数类型，检查最小值和最大值
        - BOOL: 布尔类型
        - NULL: 空值
        - PORT_RANGE: 端口号范围（0-65535）
        - SECRET_KEY: 密钥，使用正则表达式验证格式
        - IP: IP 地址，支持 IPv4 和 IPv6
        - URL: URL 地址，使用正则表达式验证格式
        - LOGGING: 日志级别，必须是预定义的日志级别之一
        - INCLUDE_HASH: 包含哈希选项，必须是预定义的选项之一
        - BCRYPTHASH: bcrypt 哈希密码，验证格式并检查是否需要重置
        - PATH: 路径，调用 _validate_path 验证
        - PATH_LIST: 路径列表，验证列表中的每个路径
    
    验证流程：
        1. 遍历允许的类型列表
        2. 根据类型进行相应的验证
        3. 如果验证通过，返回该值
        4. 如果所有类型都不匹配，调用 _apply_default 应用默认值
    """
    allowed_types = rules.get("types", [])
    default = rules.get("default")
    min_value = rules.get("min")
    max_value = rules.get("max")
    max_length = rules.get("max_length")
    
    for t in allowed_types:
        match t:
            case "STRING":
                if isinstance(value, str):
                    if max_length is None or len(value) <= max_length:
                         return value
            case "INTEGER":
                if isinstance(value, int):
                    if (min_value is None or value >= min_value) and (max_value is None or value <= max_value):
                        return value
            case "BOOL":
                if isinstance(value, bool):
                    return value
            case "NULL":
                if value is None:
                    return value
            case "PORT_RANGE":
                if isinstance(value, int) and 0 <= value <= 65535:
                    return value
            case "SECRET_KEY":
                if isinstance(value, str):
                    if RE_SECRET_KEY.fullmatch(value):
                        return value
            case "IP":
                if isinstance(value, str):
                    if RE_IPV4.fullmatch(value) or RE_IPV6.fullmatch(value):
                        return value
            case "URL":
                if isinstance(value, str):
                    if RE_URL.fullmatch(value):
                        return value
            case "LOGGING":
                if isinstance(value, str):
                    if value.upper() in LOG_LEVELS:
                        return value
            case "INCLUDE_HASH":
                if isinstance(value, str):
                    if value.lower() in INCLUDE_HASH_OPTIONS:
                        return value.lower()
            case "BCRYPTHASH":
                if is_valid_bcrypt_hash(value) and not os.environ.get('RESET_ADMIN','').lower() == 'true':
                    return value
            case "PATH":
                if isinstance(value, str):
                    try:
                        return _validate_path(value, path_type="incomplete_folder")
                    except ValueError as e:
                        logger.error(f"Path validation failed for {key}: {e}")
            case "PATH_LIST":
                if isinstance(value, list):
                    incomplete_folder_path = None
                    if normalized and section in normalized:
                        incomplete_folder_path = normalized[section].get("incomplete_folder_path")

                    validated_subdirs = []
                    for subdir in value:
                        if not isinstance(subdir, str):
                            logger.warning(f"Skipping non-string subdirectory: {subdir}")
                            continue

                        try:
                            validated_path = _validate_path(subdir, path_type="subdirectory", incomplete_folder_path=incomplete_folder_path)
                            validated_subdirs.append(validated_path)
                        except ValueError as e:
                            logger.warning(f"Skipping invalid subdirectory '{subdir}': {e}")
                            continue

                    return validated_subdirs
                elif value is None:
                    return None

    return _apply_default(default, key, value)

def ensure_login_credentials(self):
    """
    确保登录凭证有效
    
    这个函数用于检查和重置管理员登录凭证。它会检查当前的用户名和密码哈希是否有效，
    如果无效或需要重置，则会使用环境变量或默认值进行重置
    
    Args:
        self: 配置对象，需要实现 get()、set() 和 save() 方法
    
    触发重置的条件：
        1. 环境变量 RESET_ADMIN 设置为 "true"
        2. 用户名为空
        3. 密码哈希为空
        4. 密码哈希格式无效
    
    重置逻辑：
        - 用户名：优先从环境变量 USERNAME 获取，否则使用 DEFAULT_USERNAME
        - 密码：优先从环境变量 PASSWORD 获取，否则使用 DEFAULT_PASSWORD
        - 密码哈希：对密码进行 bcrypt 哈希处理
    
    日志记录：
        - RESET_ADMIN=true: 记录警告信息，表示通过环境变量重置
        - 用户名或密码为空: 记录信息，表示初始化登录凭证
        - 密码哈希无效: 记录警告，表示使用环境变量或默认值重置
    """
    logger = logging.getLogger('config')

    username = self.get("login", "username")
    password_hash = self.get("login", "password")

    reset_admin = os.environ.get("RESET_ADMIN", "").lower() == "true"
    
    needs_reset = (
        reset_admin or
        not username or
        not password_hash or
        not is_valid_bcrypt_hash(password_hash)
    )

    if not needs_reset:
        return
    
    new_username = os.environ.get("USERNAME", DEFAULT_USERNAME)
    new_password = os.environ.get("PASSWORD", DEFAULT_PASSWORD)
    new_password_hash = hash_password(new_password)

    self.set("login", "username", value=new_username)
    self.set("login", "password", value=new_password_hash)
    self.save()

    if reset_admin:
        logger.warning("RESET_ADMIN=true detected - Admin credentials reset via environment/defaults")
    elif not username or not password_hash:
        logger.info(f"Login credentials initialized (username: '{new_username}')")
    else:
        logger.warning(
            f"Password hash was invalid - credentials reset using environment/defaults (username: '{new_username}')"
        )
