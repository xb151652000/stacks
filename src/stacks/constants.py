#!/usr/bin/env python3
"""
🌟 Stacks项目常量定义文件 🌟

【这个文件的作用】
这个文件就像一个"配置中心"，存放了整个项目的所有重要设置：
- 📁 文件夹路径（下载目录、日志目录等）
- 🔗 API地址（Anna's Archive的下载接口）
- 🔐 安全设置（登录限制、密码规则等）
- 📋 文件类型（支持哪些文件格式）
- 📊 日志配置（日志格式、级别等）

【通俗理解】想象你在管理一个图书馆：
- 需要知道书架在哪里（目录路径）
- 需要知道从哪里进书（API地址）
- 需要知道哪些书可以借（文件类型）
- 需要知道怎么记录借阅（日志配置）

这个文件就是把这些"规则"都写在一个地方，方便统一管理。

【为什么需要常量文件？】
1. 🎯 集中管理：所有配置都在一个地方，修改方便
2. 🔄 避免重复：不用在多个地方写相同的值
3. 🛡️ 防止错误：用变量名代替魔法数字，减少拼写错误
4. 📖 易于理解：看到变量名就知道是什么意思
"""

from pathlib import Path  # 📂 路径处理模块，用于处理文件路径
import re               # 🔍 正则表达式模块，用于模式匹配
import time             # ⏰ 时间模块，用于获取当前时间
import os               # 💻 操作系统模块，用于环境变量
import logging          # 📝 日志模块，用于记录日志

# ================================
# 📁 目录路径配置
# ================================
# 就像给图书馆的各个房间起名字，方便找到东西

# PROJECT_ROOT - 项目根目录（整个项目的大本营）
# 允许通过环境变量覆盖项目根目录（PEX部署时需要）
PROJECT_ROOT = Path(os.environ.get('STACKS_PROJECT_ROOT', Path(__file__).resolve().parent.parent.parent))
"""
【解释】
- 这是整个项目的"家"，所有其他路径都是基于这个路径的
- 默认是当前文件的上级目录的上级目录的上级目录
- 可以通过环境变量 STACKS_PROJECT_ROOT 覆盖
- 就像说："我的家在 d:/workspace/stacks"

【实际路径示例】
如果项目在 d:/workspace/stacks，那么：
- PROJECT_ROOT = d:/workspace/stacks
"""

# 主要目录路径 - 就像图书馆的各个房间

# DOWNLOAD_PATH - 下载文件存储目录（存放用户下载的电子书）
DOWNLOAD_PATH = PROJECT_ROOT / "download"
"""
【解释】
- 用户下载的所有文件都存放在这里
- 路径示例：d:/workspace/stacks/download/
- 就像图书馆的"借阅区"，存放借出去的书
"""

# INCOMPLETE_PATH - 未完成下载的临时目录（正在下载的文件）
INCOMPLETE_PATH = PROJECT_ROOT / "download" / "incomplete"
"""
【解释】
- 正在下载的文件先存放在这里
- 下载完成后移动到 DOWNLOAD_PATH
- 路径示例：d:/workspace/stacks/download/incomplete/
- 就像图书馆的"新书整理区"，新书先在这里整理
"""

# LOG_PATH - 日志文件存储目录（存放程序运行记录）
LOG_PATH = PROJECT_ROOT / "logs"
"""
【解释】
- 所有日志文件都存放在这里
- 路径示例：d:/workspace/stacks/logs/
- 就像图书馆的"记录本"，记录每天借阅情况
"""

# CACHE_PATH - 缓存文件目录（如Cookie缓存）
CACHE_PATH = PROJECT_ROOT / "cache"
"""
【解释】
- 存放临时缓存文件，提高性能
- 路径示例：d:/workspace/stacks/cache/
- 就像图书馆的"临时书架"，放一些常用的书
"""

# CONFIG_PATH - 配置文件目录（存放config.yaml等配置文件）
CONFIG_PATH = PROJECT_ROOT / "config"
"""
【解释】
- 所有配置文件都存放在这里
- 路径示例：d:/workspace/stacks/config/
- 就像图书馆的"管理手册"，存放各种规则
"""

# FILES_PATH - 项目资源文件目录（存放项目需要的资源文件）
FILES_PATH = PROJECT_ROOT / "files"
"""
【解释】
- 存放项目运行需要的资源文件
- 路径示例：d:/workspace/stacks/files/
- 就像图书馆的"工具室"，存放各种工具
"""

# WWW_PATH - Web前端文件目录（存放HTML、CSS、JS等前端文件）
WWW_PATH = PROJECT_ROOT / "web"
"""
【解释】
- 存放Web界面的所有文件
- 路径示例：d:/workspace/stacks/web/
- 就像图书馆的"阅览室"，存放供读者阅读的资料
"""

# ================================
# 📄 文件路径配置
# ================================
# 就像图书馆的"档案室"，存放各种重要文件

# QUEUE_FILE - 下载队列数据文件（记录待下载的任务）
QUEUE_FILE = CONFIG_PATH / "queue.json"
"""
【解释】
- 存放所有待下载任务的信息
- 路径示例：d:/workspace/stacks/config/queue.json
- 就像图书馆的"借阅登记表"，记录谁要借什么书
"""

# CONFIG_FILE - 主配置文件（存放用户设置）
CONFIG_FILE = CONFIG_PATH / "config.yaml"
"""
【解释】
- 存放用户的所有设置（登录信息、下载路径等）
- 路径示例：d:/workspace/stacks/config/config.yaml
- 就像图书馆的"规则手册"，规定怎么运营
"""

# CONFIG_SCHEMA_FILE - 配置文件模式定义（配置文件的格式说明）
CONFIG_SCHEMA_FILE = FILES_PATH / "config_schema.yaml"
"""
【解释】
- 定义配置文件应该包含哪些字段、什么类型
- 路径示例：d:/workspace/stacks/files/config_schema.yaml
- 就像图书馆的"表格模板"，说明表格该怎么填
"""

# COOKIE_CACHE_DIR - Cookie缓存目录（存放登录凭证等）
COOKIE_CACHE_DIR = CACHE_PATH
"""
【解释】
- 存放网站登录凭证，避免重复登录
- 路径示例：d:/workspace/stacks/cache/
- 就像图书馆的"会员卡"，记录会员信息
"""

# GUNICORN_CONFIG_FILE - Gunicorn配置文件（Web服务器设置）
GUNICORN_CONFIG_FILE = PROJECT_ROOT / "src" / "stacks" / "gunicorn_config.py"
"""
【解释】
- 存放Web服务器的运行配置
- 路径示例：d:/workspace/stacks/src/stacks/gunicorn_config.py
- 就像图书馆的"开门时间表"，规定什么时候开门
"""

# ================================
# 🚫 保留路径配置
# ================================
# 这些路径被系统保留，不能用于下载子目录
RESERVED_PATHS = ['/logs', '/config', '/files', '/cache', '/web']
"""
【解释】
- 这些文件夹是系统专用的，用户不能用来存放下载文件
- 就像图书馆的"员工区"，读者不能进入
- 防止用户误删或覆盖系统文件
"""

# ================================
# 🔗 API URL配置
# ================================
# Anna's Archive快速下载API端点
FAST_DOWNLOAD_API_URL = "https://annas-archive.org/dyn/api/fast_download.json"
"""
【解释】
- Anna's Archive网站的下载接口地址
- 程序通过这个地址获取下载链接
- 就像图书馆的"采购部"，从这里订购新书
"""

# ================================
# 📊 日志配置
# ================================
# 就像图书馆的"记录规则"，规定怎么记录日志

# LOG_FORMAT - 日志格式字符串（每条日志的格式）
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
"""
【解释】
- 定义每条日志的显示格式
- %(asctime)s = 时间（如 2025-12-23 10:30:45）
- %(levelname)s = 日志级别（如 INFO、ERROR）
- %(name)s = 模块名称（如 stacks.main）
- %(message)s = 日志内容
- 示例：[2025-12-23 10:30:45] [INFO] [stacks.main] 程序启动成功
"""

# LOG_DATE_FORMAT - 日志日期格式（时间的显示方式）
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
"""
【解释】
- %Y = 4位年份（2025）
- %m = 2位月份（12）
- %d = 2位日期（23）
- %H = 24小时制小时（10）
- %M = 分钟（30）
- %S = 秒（45）
- 示例：2025-12-23 10:30:45
"""

# LOG_LEVELS - 支持的日志级别列表
LOG_LEVELS = ["INFO", "ERROR", "WARN", "DEBUG"]
"""
【解释】
- DEBUG = 调试信息（最详细）
- INFO = 一般信息（正常运行）
- WARN = 警告信息（需要注意）
- ERROR = 错误信息（出错了）
- 就像图书馆的"记录等级"，重要程度不同
"""

# LOG_VIEW_LENGTH - Web界面显示的日志行数限制
LOG_VIEW_LENGTH = 1000
"""
【解释】
- Web界面最多显示1000行日志
- 防止日志太多导致浏览器卡顿
- 就像图书馆的"展示柜"，只展示最近1000条记录
"""

# ================================
# 🔐 文件名哈希包含选项
# ================================
# 定义如何在文件名中包含MD5哈希值
INCLUDE_HASH_OPTIONS = ["none", "prefix", "suffix"]
"""
【解释】
- none = 不包含哈希值（文件名：book.pdf）
- prefix = 哈希值在前缀（文件名：abc123_book.pdf）
- suffix = 哈希值在后缀（文件名：book_abc123.pdf）
- MD5哈希用于确保文件唯一性
- 就像给每本书贴个"唯一编号"，防止重名
"""

# ================================
# 🔑 默认凭据配置
# ================================
# 登录系统的默认账号密码

# DEFAULT_USERNAME - 默认管理员用户名
DEFAULT_USERNAME = "admin"
"""
【解释】
- 首次安装时的默认用户名
- 建议首次使用后立即修改
- 就像图书馆的"管理员账号"，初始密码是admin
"""

# DEFAULT_PASSWORD - 默认管理员密码
DEFAULT_PASSWORD = "stacks"
"""
【解释】
- 首次安装时的默认密码
- ⚠️ 安全警告：强烈建议首次使用后立即修改！
- 就像图书馆的"初始密码"，应该尽快更换
"""

# ================================
# 🛡️ 速率限制设置
# ================================
# 防止暴力破解密码的安全措施

# LOGIN_MAX_ATTEMPTS - 最大登录尝试次数
LOGIN_MAX_ATTEMPTS = 5
"""
【解释】
- 连续输错5次密码后锁定账户
- 防止暴力破解密码
- 就像图书馆的"门禁卡"，输错5次就锁住
"""

# LOGIN_LOCKOUT_MINUTES - 登录锁定时长（分钟）
LOGIN_LOCKOUT_MINUTES = 10
"""
【解释】
- 账户锁定10分钟后才能再次尝试登录
- 给用户一些时间冷静，也给系统时间恢复
- 就像图书馆的"禁闭室"，关10分钟再放出来
"""

# LOGIN_ATTEMPT_WINDOW_MINUTES - 登录尝试时间窗口（分钟）
LOGIN_ATTEMPT_WINDOW_MINUTES = 10
"""
【解释】
- 在10分钟内输错5次才会锁定
- 如果超过10分钟，计数器会重置
- 就像图书馆的"记忆时间"，10分钟后就忘了你之前输错几次
"""

# ================================
# 🔍 预编译正则表达式模式
# ================================
# 就像图书馆的"检查规则"，用于验证输入是否正确

# RE_IPV4 - IPv4地址验证模式（支持可选端口号）
RE_IPV4 = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::(?:6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]\d{4}|[1-9]\d{0,3}))?$")
"""
【解释】
- 验证IPv4地址格式是否正确
- 支持可选的端口号
- 正确示例：192.168.1.1、127.0.0.1:8080
- 错误示例：256.1.1.1、192.168.1
- 就像验证"借书证号码"格式是否正确
"""

# RE_IPV6 - IPv6地址验证模式（支持可选端口号）
RE_IPV6 = re.compile(r"^((\[((?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,7}:|:([0-9A-Fa-f]{1,4}:){1,7}|([0-9A-Fa-f]{1,4}:){1,6}[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2}|([0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3}|([0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4}|([0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5}|[0-9A-Fa-f]{1,4}:((:[0-9A-Fa-f]{1,4}){1,6})|:((:[0-9A-Fa-f]{1,4}){1,7}))\])(?::(?:6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]\d{4}|[1-9]\d{0,3}))?$|(?:[0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,7}:|:([0-9A-Fa-f]{1,4}:){1,7}|([0-9A-Fa-f]{1,4}:){1,6}[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2}|([0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3}|([0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4}|([0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5}|[0-9A-Fa-f]{1,4}:((:[0-9A-Fa-f]{1,4}){1,6})|:((:[0-9A-Fa-f]{1,4}){1,7}))$")
"""
【解释】
- 验证IPv6地址格式是否正确
- 支持可选的端口号
- 正确示例：2001:db8::1、[::1]:8080
- 错误示例：2001:db8::1::1
- IPv6是新一代网络地址格式，比IPv4更长
"""

# RE_URL - URL验证模式（支持可选协议和端口号）
RE_URL = re.compile(r"^(?:https?:\/\/)?(?=[a-zA-Z0-9])[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)*(?::(?:6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]\d{4}|[1-9]\d{0,3}))?$")
"""
【解释】
- 验证URL格式是否正确
- 支持可选的http://或https://前缀
- 支持可选的端口号
- 正确示例：example.com、https://example.com、example.com:8080
- 错误示例：-example.com、http://example
- 就像验证"网站地址"格式是否正确
"""

# RE_SECRET_KEY - 密钥验证模式（32位字母数字、下划线和连字符）
RE_SECRET_KEY = re.compile(r"^[A-Za-z0-9_-]{32}$")
"""
【解释】
- 验证密钥格式是否正确
- 必须是32位字符
- 只能包含字母、数字、下划线和连字符
- 正确示例：abc123def456ghi789jkl012mno345pqr
- 错误示例：abc123（太短）、abc@123（包含非法字符）
- 密钥用于加密和安全验证
"""

# ================================
# 🧪 测试配置
# ================================
# 用于开发和测试的特殊配置

# KNOWN_MD5 - 已知的测试用MD5哈希值
KNOWN_MD5 = "d6e1dc51a50726f00ec438af21952a45"
"""
【解释】
- 这是一个已知的测试用MD5哈希值
- 用于测试下载功能是否正常
- MD5是文件内容的"指纹"，用于验证文件完整性
- 就像图书馆的"测试书籍"，用来测试系统是否正常
"""

# ================================
# 🔄 缓存破坏
# ================================
# 确保用户获取最新版本的静态文件

# TIMESTAMP - 当前时间戳
TIMESTAMP = time.time()
"""
【解释】
- 获取程序启动时的当前时间戳
- 用于静态文件的缓存破坏
- 在URL中添加时间戳参数，强制浏览器重新加载文件
- 示例：style.css?v=1734923445
- 就像给每本书贴个"出版日期"，确保拿到最新版
"""

# ================================
# 📚 合法文件扩展名
# ================================
# Stacks支持的文件类型列表（电子书、文档、压缩包等）
LEGAL_FILES = ['.7z', '.ai', '.azw', '.azw3', '.cb7', '.cbr', '.cbz', '.chm', '.djvu', 
               '.doc', '.docx', '.epub', '.exe', '.fb2', '.gz', '.htm', '.html', 
               '.htmlz', '.jpg', '.json', '.lit', '.lrf', '.mht', '.mobi', '.odt', 
               '.pdb', '.pdf', '.ppt', '.pptx', '.prc', '.rar', '.rtf', '.snb', 
               '.tar', '.tif', '.txt', '.updb', '.xls', '.xlsx', '.zip']
"""
【解释】
- 列出了所有允许下载的文件类型
- 包括电子书格式（.epub、.mobi、.pdf等）
- 包括文档格式（.doc、.docx、.txt等）
- 包括压缩包格式（.zip、.rar、.7z等）
- 如果文件扩展名不在这个列表中，将不允许下载
- 就像图书馆的"藏书清单"，只收藏这些类型的书

【常见文件类型说明】
- .pdf - Adobe PDF文档
- .epub - 电子书格式
- .mobi - Kindle电子书
- .doc/.docx - Word文档
- .zip/.rar - 压缩包
"""

# ================================
# 📋 版本信息（启动时加载一次）
# ================================
# 用于显示程序版本号

def _load_version():
    """
    📖 从版本文件加载应用版本号
    
    【作用】
    从项目的VERSION文件中读取版本号，用于显示当前程序版本。
    如果读取失败，返回"unknown"。
    
    【通俗理解】
    就像查看产品的"出厂日期"或"版本号"，
    告诉用户现在用的是哪个版本。
    
    Returns:
        str: 应用版本号（如 "1.0.0"）或 "unknown"
    
    【学习提示】
    这个函数展示了：
    1. 如何使用Path对象处理文件路径
    2. 如何安全地读取文件（try-except）
    3. 如何使用logging记录警告信息
    4. 如何处理文件不存在的情况
    """
    try:
        # 构建版本文件路径
        version_file = PROJECT_ROOT / "VERSION"
        
        # 读取版本号并去除首尾空白
        with open(version_file) as f:
            return f.read().strip()
    except Exception as e:
        # 如果读取失败，记录警告并返回"unknown"
        logging.getLogger(__name__).warning(f"加载版本失败: {e}")
        return "unknown"


def _load_tamper_version():
    """
    🌐 从Tampermonkey脚本元数据加载版本号
    
    【作用】
    从浏览器扩展脚本中提取版本号，用于显示扩展版本信息。
    Tampermonkey是一个浏览器扩展管理工具。
    
    【通俗理解】
    就像查看"浏览器插件"的版本号，
    确保Web界面和浏览器插件版本一致。
    
    Returns:
        str | None: Tampermonkey脚本版本号（如 "1.2.3"），如果解析失败则返回None
    
    【学习提示】
    这个函数展示了：
    1. 如何使用正则表达式提取特定内容
    2. 如何处理文件编码（encoding='utf-8'）
    3. 如何只读取文件的一部分（f.read(2000)）
    4. 如何处理元数据格式的文件
    
    【Tampermonkey元数据格式示例】
    // ==UserScript==
    // @name         Stacks Extension
    // @version      1.2.3
    // @match        https://annas-archive.org/*
    // ==/UserScript==
    """
    try:
        # 构建Tampermonkey脚本路径
        tamper_script = PROJECT_ROOT / "web" / "tamper" / "stacks_extension.user.js"
        
        # 检查文件是否存在
        if tamper_script.exists():
            # 读取文件前2000字符（元数据块通常在文件开头）
            with open(tamper_script, 'r', encoding='utf-8') as f:
                content = f.read(2000)
                
                # 使用正则表达式提取@version字段的值
                # 匹配格式：// @version 1.2.3
                match = re.search(r'//\s*@version\s+(\S+)', content)
                if match:
                    return match.group(1)  # 返回版本号
    except Exception as e:
        # 如果读取失败，记录警告
        logging.getLogger(__name__).warning(f"加载Tampermonkey版本失败: {e}")
    
    # 如果没有找到版本号，返回None
    return None


# 在模块加载时获取版本信息
# 这些变量在程序启动时就会被赋值，之后不再改变
VERSION = _load_version()          # 主应用版本
TAMPER_VERSION = _load_tamper_version()  # Tampermonkey扩展版本

"""
【版本号使用示例】
- 在Web界面显示：Stacks v1.0.0
- 在日志中记录：[INFO] [stacks] 版本 1.0.0 启动
- 在API响应中返回：{"version": "1.0.0"}
"""