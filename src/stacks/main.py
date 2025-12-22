#!/usr/bin/env python3
"""
Stacks下载管理器 - 主入口文件
这是Stacks应用程序的主入口点，负责初始化和启动服务器。
Stacks是一个专门为Anna's Archive设计的下载队列管理器，提供Web界面来管理下载任务。
"""

import os
import sys
import signal
import argparse
from stacks.server.webserver import create_app
from pathlib import Path
from stacks.constants import CONFIG_FILE, PROJECT_ROOT, LOG_PATH, DOWNLOAD_PATH, GUNICORN_CONFIG_FILE

# ANSI颜色代码（德古拉主题）- 用于美化控制台输出
INFO = "\033[38;2;139;233;253m"       # 青色 - 信息提示
WARN = "\033[38;2;255;184;108m"       # 橙色 - 警告信息
GOOD = "\033[38;2;80;250;123m"        # 绿色 - 成功信息
PINK = "\033[38;2;255;102;217m"       # 粉色 - 强调信息
PURPLE = "\033[38;2;178;102;255m"     # 紫色 - 边框颜色
BG = "\033[48;2;40;42;54m"            # 黑色背景
PINKBG = "\033[48;2;255;102;217m"     # 粉色背景
RESET = "\033[0m"                     # 重置颜色

def print_logo(version: str):
    """
    显示超酷的STACKS徽标和版本信息
    这个函数在程序启动时显示一个ASCII艺术徽标，用于提升用户体验。
    
    Args:
        version (str): 应用程序版本号
    """
    # 根据版本号长度动态调整分隔符长度
    dashes = '─' * (52 - len(version))
    
    # 打印ASCII艺术徽标，使用多种颜色创建德古拉主题效果
    print(f"{BG}{PURPLE} ┌───────────────────────────────────────────────────────────┐ {RESET}")
    print(f"{BG}{PURPLE} │                                                           {PURPLE}│ {RESET}")
    print(f"{BG}{PURPLE} │{PINK}     ▄████▄ ████████  ▄█▄     ▄████▄  ██    ▄██ ▄████▄     {PURPLE}│ {RESET}")
    print(f"{BG}{PURPLE} │{PINK}    ██▀  ▀██   ██    ▄{PINKBG}{PURPLE}▄{BG}▀{PINKBG}▄{BG}{PINK}▄   ██▀  ▀██ ██  ▄██▀ ██▀  ▀██    {PURPLE}│ {RESET}")
    print(f"{BG}{PURPLE} │{PINK}    ██▄        ██    █{PURPLE}█ █{PINK}█  ██        ██▄██▀   ██▄         {PURPLE}│ {RESET}")
    print(f"{BG}{PURPLE} │{PINK}     ▀████▄    ██   █{PURPLE}█   █{PINK}█ ██        ████      ▀████▄     {PURPLE}│ {RESET}")
    print(f"{BG}{PURPLE} │{PINK}         ▀██   ██   █{PURPLE}█   █{PINK}█ ██        ██▀██▄        ▀██    {PURPLE}│ {RESET}")
    print(f"{BG}{PURPLE} │{PINK}    ██▄  ▄██   ██  █{PURPLE}█     █{PINK}█ ██▄  ▄██ ██  ▀██▄ ██▄  ▄██    {PURPLE}│ {RESET}")
    print(f"{BG}{PURPLE} │{PINK}     ▀████▀    ██  █{PURPLE}▀     ▀{PINK}█  ▀████▀  ██    ▀██ ▀████▀     {PURPLE}│ {RESET}")
    print(f"{BG}{PURPLE} │                                                           {PURPLE}│ {RESET}")
    # 显示版本信息
    print(f"{BG}{PURPLE} └{dashes}╢v{version}╟────┘ {RESET}")
    # 强制刷新输出缓冲区，确保徽标立即显示
    sys.stdout.flush()  # 在执行前强制刷新
    sys.stdout.flush()

def ensure_directories():
    """
    确保必要的目录存在
    这个函数检查并创建Stacks运行所需的所有目录，包括配置目录、日志目录和下载目录。
    使用parents=True确保父目录也被创建，exist_ok=True避免目录已存在时出错。
    """
    # 定义需要创建的目录列表
    dirs = [
        Path(CONFIG_FILE).parent,  # 配置文件目录
        Path(LOG_PATH),            # 日志文件目录
        Path(DOWNLOAD_PATH),       # 下载文件目录
    ]
    # 循环创建每个目录
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)


def setup_config(config_path):
    """
    确保配置文件存在
    检查配置文件是否存在，如果不存在则创建一个新的空配置文件。
    新创建的配置文件权限设置为600（只有所有者可读写），确保安全性。
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        str: 配置文件的完整路径
    """
    # 使用提供的配置路径或默认配置路径
    cfg_path = Path(config_path) if config_path else Path(CONFIG_FILE)

    print("◼ 检查配置文件...")
    sys.stdout.flush()

    if not cfg_path.exists():
        # 配置文件不存在，创建新的空配置文件
        print("  未找到config.yaml — 正在创建新文件。")
        cfg_path.write_text("{}\n")  # 写入空的YAML结构
        cfg_path.chmod(0o600)       # 设置安全权限
    else:
        # 配置文件已存在
        print(f"  使用配置文件: {cfg_path}")

    return str(cfg_path)


def setup_signal_handlers(app):
    """
    设置优雅关闭的信号处理器
    为SIGTERM和SIGINT信号设置处理函数，确保程序在关闭时能够：
    1. 停止下载工作线程
    2. 清理下载器资源
    3. 保存队列状态
    
    Args:
        app: Flask应用实例，包含工作线程和队列对象
    """
    def shutdown_handler(signum, frame):
        """
        信号处理函数 - 执行优雅关闭操作
        
        Args:
            signum: 接收到的信号编号
            frame: 当前的堆栈帧
        """
        # 确定信号类型用于显示
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        print(f"\n{WARN}◼ 收到{signal_name}信号，正在优雅关闭...{RESET}")
        sys.stdout.flush()

        # 停止下载工作线程
        if hasattr(app, 'stacks_worker') and app.stacks_worker:
            print(f"{INFO}  正在停止下载工作线程...{RESET}")
            sys.stdout.flush()
            app.stacks_worker.stop()

        # 清理下载器资源（关闭HTTP会话等）
        if hasattr(app, 'stacks_worker') and app.stacks_worker and hasattr(app.stacks_worker, 'downloader'):
            print(f"{INFO}  正在清理下载器资源...{RESET}")
            sys.stdout.flush()
            app.stacks_worker.downloader.cleanup()

        # 保存队列状态到磁盘
        if hasattr(app, 'stacks_queue') and app.stacks_queue:
            print(f"{INFO}  正在保存队列状态...{RESET}")
            sys.stdout.flush()
            app.stacks_queue.save()

        print(f"{GOOD}◼ 关闭完成{RESET}")
        sys.stdout.flush()
        sys.exit(0)

    # 注册信号处理器
    signal.signal(signal.SIGTERM, shutdown_handler)  # Docker容器停止信号
    signal.signal(signal.SIGINT, shutdown_handler)   # Ctrl+C信号


def main():
    """
    主函数 - 程序入口点
    处理命令行参数，初始化应用，并根据调试模式选择使用Flask开发服务器或Gunicorn生产服务器。
    """
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="启动Stacks服务器。")
    parser.add_argument(
        "-c", "--config",
        help="指定替代的config.yaml文件路径"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用Flask调试模式用于开发（文件变更时自动重载）"
    )
    args = parser.parse_args()

    # 设置UTF-8编码环境变量
    os.environ.setdefault("LANG", "C.UTF-8")

    # 读取版本信息
    version_file = PROJECT_ROOT / "VERSION"
    version = version_file.read_text().strip() if version_file.exists() else "unknown"
    print_logo(version)  # 显示启动徽标

    # 确保必要的目录存在
    ensure_directories()

    # 加载或创建配置文件
    config_path = setup_config(args.config)

    # 检测是否需要重置管理员密码
    if os.environ.get("RESET_ADMIN", "false").lower() == "true":
        print("! 检测到RESET_ADMIN=true - 管理员密码将被重置！\n")
        sys.stdout.flush()

    # 切换工作目录到项目根目录
    os.chdir(PROJECT_ROOT)

    # 确定调试模式（从命令行参数或环境变量）
    debug_mode = args.debug or os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true")

    if debug_mode:
        # 调试模式：使用Flask开发服务器
        print(f"{WARN}◼ 调试模式已启用 - 使用Flask开发服务器{RESET}")
        sys.stdout.flush()

        print("◼ 正在启动Stacks...")
        sys.stdout.flush()

        # 创建Flask应用
        app = create_app(config_path, debug_mode=debug_mode)

        # 设置优雅关闭的信号处理器
        setup_signal_handlers(app)

        # 获取服务器配置
        host = app.stacks_host
        port = app.stacks_port

        # 启动Flask开发服务器
        app.run(host, port, debug=debug_mode, use_reloader=True)
    else:
        # 生产模式：使用Gunicorn WSGI服务器
        print(f"{INFO}◼ 正在使用Gunicorn启动Stacks...{RESET}")
        sys.stdout.flush()

        # 将配置路径设置为环境变量，供Gunicorn工作进程使用
        os.environ["STACKS_CONFIG_PATH"] = config_path

        # 检查是从源代码运行还是从PEX文件运行
        if GUNICORN_CONFIG_FILE.exists():
            # 从源代码运行 - 使用文件路径并设置PYTHONPATH
            current_pythonpath = os.environ.get("PYTHONPATH", "")
            src_path = str(PROJECT_ROOT / "src")
            if current_pythonpath:
                os.environ["PYTHONPATH"] = f"{src_path}:{current_pythonpath}"
            else:
                os.environ["PYTHONPATH"] = src_path

            # 构建Gunicorn命令
            gunicorn_cmd = [
                "gunicorn",
                "--config", str(GUNICORN_CONFIG_FILE),
                "stacks.server.webserver:create_app()"
            ]
            # 执行Gunicorn，替换当前进程
            os.execvp("gunicorn", gunicorn_cmd)
        else:
            # 从PEX文件运行 - 直接导入并运行Gunicorn
            from gunicorn.app.wsgiapp import run
            sys.argv = [
                "gunicorn",
                "--config", "python:stacks.gunicorn_config",
                "stacks.server.webserver:create_app()"
            ]
            run()

# 程序入口点 - 当直接运行此脚本时执行main函数
if __name__ == "__main__":
    try:
        main()  # 调用主函数启动应用
    except Exception as e:
        # 捕获启动过程中的异常并输出到标准错误流
        print(f"\n启动过程中发生错误: {e}", file=sys.stderr)
        sys.exit(1)  # 以错误代码退出