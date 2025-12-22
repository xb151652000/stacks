"""
Stacks项目常量定义文件
此文件包含了Stacks下载管理器使用的所有常量、路径配置、正则表达式模式等。
常量集中管理有助于维护和配置的统一性。
"""

from pathlib import Path
import re
import time
import os
import logging

# ================================
# 目录路径配置
# ================================
# 允许通过环境变量覆盖项目根目录（PEX部署时需要）
PROJECT_ROOT = Path(os.environ.get('STACKS_PROJECT_ROOT', Path(__file__).resolve().parent.parent.parent))

# 主要目录路径
DOWNLOAD_PATH = PROJECT_ROOT / "download"      # 下载文件存储目录
INCOMPLETE_PATH = PROJECT_ROOT / "download" / "incomplete"  # 未完成下载的临时目录
LOG_PATH = PROJECT_ROOT / "logs"               # 日志文件存储目录
CACHE_PATH = PROJECT_ROOT / "cache"            # 缓存文件目录（如Cookie缓存）
CONFIG_PATH = PROJECT_ROOT / "config"          # 配置文件目录
FILES_PATH = PROJECT_ROOT / "files"            # 项目资源文件目录
WWW_PATH = PROJECT_ROOT / "web"                # Web前端文件目录

# ================================
# 文件路径配置
# ================================
QUEUE_FILE = CONFIG_PATH / "queue.json"        # 下载队列数据文件
CONFIG_FILE = CONFIG_PATH / "config.yaml"      # 主配置文件
CONFIG_SCHEMA_FILE = FILES_PATH / "config_schema.yaml"  # 配置文件模式定义
COOKIE_CACHE_DIR = CACHE_PATH                  # Cookie缓存目录
GUNICORN_CONFIG_FILE = PROJECT_ROOT / "src" / "stacks" / "gunicorn_config.py"  # Gunicorn配置文件

# ================================
# 保留路径配置
# ================================
# 这些路径被系统保留，不能用于下载子目录
RESERVED_PATHS = ['/logs', '/config', '/files', '/cache', '/web']

# ================================
# API URL配置
# ================================
# Anna's Archive快速下载API端点
FAST_DOWNLOAD_API_URL = "https://annas-archive.org/dyn/api/fast_download.json"

# ================================
# 日志配置
# ================================
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"  # 日志格式字符串
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"                                 # 日志日期格式
LOG_LEVELS = ["INFO", "ERROR", "WARN", "DEBUG"]                      # 支持的日志级别列表
LOG_VIEW_LENGTH = 1000                                               # Web界面显示的日志行数限制

# ================================
# 文件名哈希包含选项
# ================================
# 定义如何在文件名中包含MD5哈希值
INCLUDE_HASH_OPTIONS = ["none", "prefix", "suffix"]  # 不包含、前缀、后缀

# ================================
# 默认凭据配置
# ================================
DEFAULT_USERNAME = "admin"    # 默认管理员用户名
DEFAULT_PASSWORD = "stacks"   # 默认管理员密码（应在首次使用时修改）

# ================================
# 速率限制设置
# ================================
LOGIN_MAX_ATTEMPTS = 5              # 最大登录尝试次数
LOGIN_LOCKOUT_MINUTES = 10          # 登录锁定时长（分钟）
LOGIN_ATTEMPT_WINDOW_MINUTES = 10   # 登录尝试时间窗口（分钟）

# ================================
# 预编译正则表达式模式
# ================================
# IPv4地址验证模式（支持可选端口号）
RE_IPV4 = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::(?:6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]\d{4}|[1-9]\d{0,3}))?$")

# IPv6地址验证模式（支持可选端口号）
RE_IPV6 = re.compile(r"^((\[((?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,7}:|:([0-9A-Fa-f]{1,4}:){1,7}|([0-9A-Fa-f]{1,4}:){1,6}[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2}|([0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3}|([0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4}|([0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5}|[0-9A-Fa-f]{1,4}:((:[0-9A-Fa-f]{1,4}){1,6})|:((:[0-9A-Fa-f]{1,4}){1,7}))\])(?::(?:6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]\d{4}|[1-9]\d{0,3}))?$|(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,7}:|:([0-9A-Fa-f]{1,4}:){1,7}|([0-9A-Fa-f]{1,4}:){1,6}[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2}|([0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3}|([0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4}|([0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5}|[0-9A-Fa-f]{1,4}:((:[0-9A-Fa-f]{1,4}){1,6})|:((:[0-9A-Fa-f]{1,4}){1,7}))$")

# URL验证模式（支持可选协议和端口号）
RE_URL = re.compile(r"^(?:https?:\/\/)?(?=[a-zA-Z0-9])[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)*(?::(?:6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]\d{4}|[1-9]\d{0,3}))?$")

# 密钥验证模式（32位字母数字、下划线和连字符）
RE_SECRET_KEY = re.compile(r"^[A-Za-z0-9_-]{32}$")

# ================================
# 测试配置
# ================================
# 已知的测试用MD5哈希值
KNOWN_MD5 = "d6e1dc51a50726f00ec438af21952a45"

# ================================
# 缓存破坏
# ================================
# 当前时间戳，用于静态文件的缓存破坏（确保用户获取最新版本）
TIMESTAMP = time.time()

# ================================
# 合法文件扩展名
# ================================
# Stack支持的文件类型列表（电子书、文档、压缩包等）
LEGAL_FILES = ['.7z', '.ai', '.azw', '.azw3', '.cb7', '.cbr', '.cbz', '.chm', '.djvu', 
               '.doc', '.docx', '.epub', '.exe', '.fb2', '.gz', '.htm', '.html', 
               '.htmlz', '.jpg', '.json', '.lit', '.lrf', '.mht', '.mobi', '.odt', 
               '.pdb', '.pdf', '.ppt', '.pptx', '.prc', '.rar', '.rtf', '.snb', 
               '.tar', '.tif', '.txt', '.updb', '.xls', '.xlsx', '.zip']

# ================================
# 版本信息（启动时加载一次）
# ================================

def _load_version():
    """
    从版本文件加载应用版本号
    尝试从VERSION文件中读取版本信息，如果失败则返回"unknown"。
    
    Returns:
        str: 应用版本号或"unknown"
    """
    try:
        version_file = PROJECT_ROOT / "VERSION"
        with open(version_file) as f:
            return f.read().strip()
    except Exception as e:
        logging.getLogger(__name__).warning(f"加载版本失败: {e}")
        return "unknown"

def _load_tamper_version():
    """
    从Tampermonkey脚本元数据加载版本号
    解析Tampermonkey用户脚本的元数据块，提取@version字段的值。
    这用于显示浏览器扩展的版本信息。
    
    Returns:
        str | None: Tampermonkey脚本版本号，如果解析失败则返回None
    """
    try:
        tamper_script = PROJECT_ROOT / "web" / "tamper" / "stacks_extension.user.js"
        if tamper_script.exists():
            with open(tamper_script, 'r', encoding='utf-8') as f:
                content = f.read(2000)  # 读取前2000字符（元数据块通常在文件开头）
                match = re.search(r'//\s*@version\s+(\S+)', content)
                if match:
                    return match.group(1)
    except Exception as e:
        logging.getLogger(__name__).warning(f"加载Tampermonkey版本失败: {e}")
    return None

# 在模块加载时获取版本信息
VERSION = _load_version()          # 主应用版本
TAMPER_VERSION = _load_tamper_version()  # Tampermonkey扩展版本