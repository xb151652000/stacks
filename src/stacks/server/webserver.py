"""
Stacks Web服务器模块
此模块负责创建和配置Flask应用，包括设置静态文件、模板、CORS、日志、
下载队列、工作线程和API路由注册等功能。
"""

from flask import Flask
from flask_cors import CORS
from stacks.config.config import Config
from stacks.constants import WWW_PATH, TIMESTAMP, CONFIG_FILE
from stacks.server.queue import DownloadQueue
from stacks.server.worker import DownloadWorker
from stacks.utils.logutils import setup_logging
from stacks.api import register_api
import logging
import os

def create_app(config_path: str = None, debug_mode: bool = False):
    """
    创建并配置Flask应用
    这是Stacks应用的工厂函数，负责初始化所有必需的组件：
    - 日志系统
    - Flask应用实例
    - CORS支持
    - 配置加载
    - 下载队列和工作线程
    - API路由注册
    
    Args:
        config_path (str, optional): 配置文件路径，如果为None则使用默认路径
        debug_mode (bool): 是否启用调试模式
        
    Returns:
        Flask: 配置完成的Flask应用实例
    """
    # ---- 使用默认配置路径（如果没有提供）----
    if config_path is None:
        # 检查main.py为gunicorn设置的环境变量
        config_path = os.environ.get("STACKS_CONFIG_PATH", str(CONFIG_FILE))

    # ---- 设置日志系统 ----
    setup_logging(None)  # 使用默认日志设置
    logger = logging.getLogger("stacks.server")
    logger.info("Stacks服务器正在初始化...")

    # ---- 创建Flask应用实例 ----
    app = Flask(
        __name__,
        template_folder=WWW_PATH,    # 模板文件夹路径
        static_folder=WWW_PATH,      # 静态文件文件夹路径
        static_url_path=""           # 静态文件URL路径（根路径）
    )
    # 启用CORS支持，允许跨域请求（用于API调用）
    CORS(app, supports_credentials=True)

    # ---- 调试模式下启用模板自动重载 ----
    if debug_mode:
        app.config['TEMPLATES_AUTO_RELOAD'] = True  # 开发时模板变更自动重载
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用静态文件缓存
        logger.info("调试模式: 模板自动重载已启用")

    # ---- 加载配置 ----
    config = Config(config_path)  # 创建配置对象并加载配置文件
    setup_logging(config)         # 根据配置设置日志系统

    # ---- 从配置设置会话密钥 ----
    app.secret_key = config.get("api", "session_secret")

    # ---- 初始化下载队列和工作线程 ----
    queue = DownloadQueue(config)  # 创建下载队列管理器
    worker = DownloadWorker(queue, config)  # 创建下载工作线程
    worker.start()  # 启动工作线程（开始处理下载任务）

    # ---- 将后端对象附加到Flask应用 ----
    # 这样可以在路由处理函数中访问这些对象
    app.stacks_config = config    # 配置对象
    app.stacks_queue = queue      # 下载队列
    app.stacks_worker = worker    # 工作线程

    # ---- 设置默认端口和主机 ----
    app.stacks_host = config.get("server", "host", default="0.0.0.0")
    app.stacks_port = config.get("server", "port", default=7788)

    # ---- 缓存破坏（确保用户获取最新版本的静态文件）----
    @app.context_processor
    def inject_constants():
        """
        模板上下文处理器
        将时间戳注入到所有模板中，用于静态文件的缓存破坏。
        这样当静态文件更新时，URL会变化，确保浏览器获取最新版本。
        """
        return dict(TIMESTAMP=TIMESTAMP)

    # ---- 注册所有API路由 ----
    register_api(app)  # 注册API蓝图和路由
    logger.info("Stacks初始化完成")    
    return app
