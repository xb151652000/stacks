#!/usr/bin/env python3
"""
🌟 Stacks下载管理器 - 主入口文件 🌟

这个文件是整个Stacks程序的"总指挥"，就像电脑的"开机键"一样。
当你运行这个程序时，它会：

1. 📁 检查并创建必要的文件夹（配置文件、日志、下载文件夹）
2. 🔧 读取或创建配置文件
3. 🖥️ 启动Web服务器，让你可以用浏览器访问
4. 🛡️ 设置安全关闭功能，确保程序不会突然死掉

【小知识】这个程序是专门为Anna's Archive（一个电子书下载网站）设计的下载管理器。
简单说就是：它帮你管理下载队列，让你下载书籍更方便！

【初学者提示】不需要理解所有细节，知道这是程序的"启动文件"就够了。
"""

# ========== 导入必需的模块 ==========
import os           # 用于操作系统功能，如文件操作、环境变量
import sys          # 用于Python系统相关功能
import signal       # 用于处理系统信号（如Ctrl+C关闭程序）
import argparse     # 用于解析命令行参数（如 --debug 参数）
from stacks.server.webserver import create_app  # 导入创建Web应用的函数
from pathlib import Path  # 用于处理文件路径
# 导入常量值（这些值定义了重要文件的位置）
from stacks.constants import CONFIG_FILE, PROJECT_ROOT, LOG_PATH, DOWNLOAD_PATH, GUNICORN_CONFIG_FILE

# ========== 美化输出 - 颜色定义 ==========
# 这些是给命令行输出添加颜色的代码，让界面更美观
# 就像给文字涂上不同颜色一样
INFO = "\033[38;2;139;233;253m"       # 青色 - 用于一般信息提示
WARN = "\033[38;2;255;184;108m"       # 橙色 - 用于警告信息
GOOD = "\033[38;2;80;250;123m"        # 绿色 - 用于成功信息
PINK = "\033[38;2;255;102;217m"       # 粉色 - 用于强调信息
PURPLE = "\033[38;2;178;102;255m"     # 紫色 - 用于边框
BG = "\033[48;2;40;42;54m"            # 黑色背景
PINKBG = "\033[48;2;255;102;217m"     # 粉色背景
RESET = "\033[0m"                     # 重置颜色（让文字恢复正常）

def print_logo(version: str):
    """
    🎨 显示程序启动徽标
    
    【作用】就像电脑开机时的"Windows标志"一样，这个函数会在程序启动时
    显示一个漂亮的ASCII艺术徽标和版本信息，让用户知道程序正在启动。
    
    【通俗理解】想象你在启动一个游戏，这个函数就是显示游戏LOGO的部分。
    让整个启动过程看起来更专业、更有趣！
    
    Args:
        version (str): 版本号，比如 "1.0.0"
    
    Returns:
        None: 这个函数只负责显示，不返回任何值
    
    【学习提示】这个函数展示了如何：
    1. 动态计算字符串长度（dashes的计算）
    2. 使用颜色美化命令行输出
    3. 强制刷新输出缓冲区（sys.stdout.flush()）
    """
    
    # 🔧 根据版本号长度动态调整装饰线的长度
    # 如果版本号很长，装饰线就短一些；如果版本号很短，装饰线就长一些
    # 这样看起来更美观，就像量体裁衣一样
    dashes = '─' * (52 - len(version))
    
    # 🎨 打印ASCII艺术徽标 - 这就像在命令行里画画！
    # 使用了多种颜色创建"德古拉主题"效果（暗色调配色方案）
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
    
    # 🏷️ 显示版本信息 - 在徽标底部显示当前版本号
    print(f"{BG}{PURPLE} └{dashes}╢v{version}╟────┘ {RESET}")
    
    # ⚡ 强制刷新输出缓冲区
    # 想象一下，你往瓶子里倒水，但如果瓶子口太小，水可能不会立即流出来
    # sys.stdout.flush() 就是"敲一下瓶子"，确保所有内容都立即显示出来
    # 为什么调用两次？可能是个小bug，但不会影响功能
    sys.stdout.flush()
    sys.stdout.flush()

def ensure_directories():
    """
    📁 确保程序运行必需的文件夹存在
    
    【作用】就像你新买了一个手机，需要先创建"相册"、"下载"、"文档"等文件夹一样，
    这个程序也需要先创建自己的"文件夹结构"才能正常工作。
    
    【通俗理解】想象你要搬新家，家具进场前需要先把房间整理好。
    这个函数就是"整理房间"的工作，确保程序运行时有地方放文件。
    
    【创建哪些文件夹？】
    1. 📄 配置文件目录 - 存放config.yaml等配置文件
    2. 📋 日志文件目录 - 存放程序运行记录
    3. 📦 下载文件目录 - 存放用户下载的文件
    
    【学习提示】这个函数展示了：
    1. 如何批量创建多个目录
    2. pathlib.Path 的基本用法
    3. mkdir() 参数的作用：
       - parents=True: 如果父目录不存在，自动创建
       - exist_ok=True: 如果目录已存在，不会报错
    """
    
    # 📝 定义需要创建的目录列表
    # 就像写一个购物清单一样，我们先列出所有需要创建的"文件夹"
    dirs = [
        Path(CONFIG_FILE).parent,  # 🗂️ 配置文件目录（config.yaml所在目录）
        Path(LOG_PATH),            # 📋 日志文件目录（程序运行记录存放处）
        Path(DOWNLOAD_PATH),       # 📦 下载文件目录（用户下载的电子书存放处）
    ]
    
    # 🔄 循环创建每个目录
    # 就像按清单逐个购买商品一样，逐个创建目录
    for directory in dirs:
        # 创建目录，如果不存在就创建，如果已存在就跳过
        # 这就像说："给我一个房间，如果已经有了就不用再建了"
        directory.mkdir(parents=True, exist_ok=True)


def setup_config(config_path):
    """
    ⚙️ 设置并确保配置文件存在
    
    【作用】配置文件就像程序的"使用说明书"，告诉程序该怎么运行。
    这个函数负责：
    1. 找到配置文件（如果用户指定了路径，就用指定的；如果没有，用默认的）
    2. 如果配置文件不存在，就创建一个新的空配置文件
    3. 设置安全权限，防止别人随意修改
    
    【通俗理解】想象你买了一个智能家居设备，第一次使用时需要：
    - 找到说明书（配置文件）
    - 如果没带说明书，就创建一份新的空白说明书
    - 确保说明书只有你能修改（设置权限）
    
    【配置文件是什么？】
    config.yaml - 一个文本文件，存放程序的各种设置，比如：
    - 服务器端口号
    - 用户名和密码
    - 下载文件夹位置
    等各种配置信息
    
    Args:
        config_path (str): 配置文件路径，如果为None则使用默认路径
                          就像告诉程序："我的说明书在桌面上"
        
    Returns:
        str: 配置文件的完整路径（告诉调用者配置文件在哪里）
    
    【学习提示】这个函数展示了：
    1. 如何处理可选参数（config_path可能为None）
    2. 文件存在性检查（.exists()方法）
    3. 如何创建文件并写入内容（.write_text()方法）
    4. 如何设置文件权限（.chmod()方法）
    5. 路径类型转换（Path对象转字符串）
    """
    
    # 🎯 确定配置文件的路径
    # 就像找文件时：如果用户指定了位置就用指定的，否则用默认位置
    cfg_path = Path(config_path) if config_path else Path(CONFIG_FILE)

    # 📢 告诉用户正在检查配置文件
    print("◼ 检查配置文件...")
    sys.stdout.flush()  # 立即显示消息

    # 🔍 检查配置文件是否存在
    if not cfg_path.exists():
        # ❌ 配置文件不存在，需要创建一个新的
        
        # 📝 通知用户正在创建配置文件
        print("  未找到config.yaml — 正在创建新文件。")
        
        # ✏️ 创建空的YAML配置文件
        # "{}" 是一个空的YAML格式，就像一个空白的表格
        cfg_path.write_text("{}\n")  
        
        # 🔒 设置安全权限：只有文件所有者可以读写，其他人无法访问
        # 0o600 是一种权限设置，类似于Windows的"只读"属性
        cfg_path.chmod(0o600)       
    else:
        # ✅ 配置文件存在，直接使用
        
        # 📢 告诉用户正在使用现有配置文件
        print(f"  使用配置文件: {cfg_path}")

    # 📤 返回配置文件的完整路径字符串
    # 就像说："配置文件在 d:/stacks/config/config.yaml"
    return str(cfg_path)


def setup_signal_handlers(app):
    """
    🛡️ 设置程序安全关闭的"守护神"
    
    【作用】这个函数就像给程序安装了一个"保险丝"，
    确保当程序需要关闭时（比如用户按Ctrl+C，或者Docker容器停止），
    能够安全、优雅地关闭，不会造成数据丢失或文件损坏。
    
    【通俗理解】想象你正在写一份重要的Word文档：
    - 如果突然断电，文档可能丢失（程序突然关闭）
    - 如果你先保存再关机，文档就安全了（优雅关闭）
    
    这个函数就是让程序学会"先保存再关机"的本领。
    
    【关闭时需要做什么？】
    1. 🛑 停止下载任务（就像暂停播放视频一样）
    2. 🧹 清理临时文件（关闭网络连接等）
    3. 💾 保存用户数据（保存下载队列等）
    
    【什么情况会触发关闭？】
    - 用户按 Ctrl+C（在命令行中停止程序）
    - Docker容器收到停止信号
    - 系统关机
    
    Args:
        app: Flask应用实例，包含工作线程和队列对象
             就像程序的"大脑"，包含所有重要的组件
    
    【学习提示】这个函数展示了：
    1. 如何处理系统信号
    2. 如何进行条件检查（hasattr()的使用）
    3. 如何进行资源清理
    4. 嵌套函数的定义和使用
    """
    
    # 🔧 定义关闭处理函数 - 就像制定"关机流程表"
    def shutdown_handler(signum, frame):
        """
        📋 执行安全关闭的"操作手册"
        
        【作用】这个内部函数定义了在收到关闭信号时应该执行的具体步骤。
        就像医院的急救流程一样，有条不紊地执行每个步骤。
        
        Args:
            signum (int): 收到的信号类型编号
                          就像接到电话："您好，这里是120急救中心"
            frame: 当前的程序执行状态（堆栈帧）
                   就像拍照记录当前的状态
        """
        
        # 🏷️ 确定信号类型 - 告诉用户是哪种关闭方式
        # 就像医生问："您是因为什么不舒服？"
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        print(f"\n{WARN}◼ 收到{signal_name}信号，正在优雅关闭...{RESET}")
        sys.stdout.flush()  # 立即显示消息

        # 🛑 第一步：停止下载工作线程
        # 就像告诉正在下载文件的工作人员："请停止工作"
        if hasattr(app, 'stacks_worker') and app.stacks_worker:
            print(f"{INFO}  正在停止下载工作线程...{RESET}")
            sys.stdout.flush()
            app.stacks_worker.stop()

        # 🧹 第二步：清理下载器资源
        # 就像关闭打开的文件、断开网络连接等
        if hasattr(app, 'stacks_worker') and app.stacks_worker and hasattr(app.stacks_worker, 'downloader'):
            print(f"{INFO}  正在清理下载器资源...{RESET}")
            sys.stdout.flush()
            app.stacks_worker.downloader.cleanup()

        # 💾 第三步：保存队列状态到磁盘
        # 就像保存游戏进度一样，把用户的下载队列保存起来
        if hasattr(app, 'stacks_queue') and app.stacks_queue:
            print(f"{INFO}  正在保存队列状态...{RESET}")
            sys.stdout.flush()
            app.stacks_queue.save()

        # ✅ 完成关闭
        print(f"{GOOD}◼ 关闭完成{RESET}")
        sys.stdout.flush()
        sys.exit(0)  # 正常退出程序

    # 📞 注册信号处理器 - 把"操作手册"注册给系统
    # 就像告诉系统："如果收到SIGTERM或SIGINT信号，就按照这个手册执行"
    signal.signal(signal.SIGTERM, shutdown_handler)  # Docker容器停止信号
    signal.signal(signal.SIGINT, shutdown_handler)   # Ctrl+C信号


def main():
    """
    🚀 程序启动的"总导演"
    
    【作用】这个函数就像电影的总导演，负责协调整个程序的启动过程。
    它的主要任务是：
    1. 📋 理解用户的命令（解析命令行参数）
    2. 🏠 准备运行环境（设置目录、配置文件等）
    3. 🎭 决定使用哪种"舞台"（调试模式用Flask，生产模式用Gunicorn）
    4. 🎬 正式启动程序（创建应用并运行服务器）
    
    【通俗理解】想象你要开一家餐厅：
    1. 先了解顾客需求（解析参数）
    2. 准备厨房和餐厅（初始化环境）
    3. 决定是试营业还是正式营业（调试vs生产模式）
    4. 开门迎客（启动服务器）
    
    【启动流程图】
    命令行输入 → 参数解析 → 环境准备 → 模式判断 → 启动服务器
    
    【学习提示】这是Python程序的典型结构：
    1. 使用argparse处理命令行参数
    2. 条件判断决定不同的执行路径
    3. 导入和调用其他模块的函数
    4. 使用环境变量传递配置信息
    """
    
    # 📋 第一步：设置命令行参数解析器
    # 就像给程序安装"耳朵"，让它能听懂用户的指令
    parser = argparse.ArgumentParser(description="启动Stacks服务器。")
    
    # 添加 -c/--config 参数：让用户可以指定配置文件位置
    parser.add_argument(
        "-c", "--config",
        help="指定替代的config.yaml文件路径"
    )
    
    # 添加 --debug 参数：让用户可以开启调试模式
    parser.add_argument(
        "--debug",
        action="store_true",  # 这是一个布尔开关，有这个参数就是True，没有就是False
        help="启用Flask调试模式用于开发（文件变更时自动重载）"
    )
    
    # 解析命令行参数 - 就像"翻译"用户的指令
    args = parser.parse_args()

    # 🌍 设置UTF-8编码环境变量
    # 就像告诉程序："我们要用UTF-8编码来处理文字"，避免中文乱码
    os.environ.setdefault("LANG", "C.UTF-8")

    # 📖 第二步：读取版本信息并显示启动徽标
    # 就像电影开始前先放片头一样
    version_file = PROJECT_ROOT / "VERSION"
    version = version_file.read_text().strip() if version_file.exists() else "unknown"
    print_logo(version)  # 显示漂亮的启动徽标

    # 🏠 第三步：准备运行环境
    
    # 创建必要的文件夹（配置文件、日志、下载目录）
    ensure_directories()

    # 加载或创建配置文件
    config_path = setup_config(args.config)

    # 🔐 检测是否需要重置管理员密码
    # 这是一个特殊功能，通过环境变量触发
    if os.environ.get("RESET_ADMIN", "false").lower() == "true":
        print("! 检测到RESET_ADMIN=true - 管理员密码将被重置！\n")
        sys.stdout.flush()

    # 📂 切换工作目录到项目根目录
    # 就像告诉程序："你的工作地点在 d:/workspace/stacks"
    os.chdir(PROJECT_ROOT)

    # 🎯 第四步：决定运行模式
    # 检查是否开启调试模式（从命令行参数或环境变量）
    debug_mode = args.debug or os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true")

    # 🎭 根据模式选择不同的"舞台"
    if debug_mode:
        # 🎨 调试模式：使用Flask开发服务器
        # 就像试营业：功能完整，反应快速，适合开发调试
        
        print(f"{WARN}◼ 调试模式已启用 - 使用Flask开发服务器{RESET}")
        sys.stdout.flush()

        print("◼ 正在启动Stacks...")
        sys.stdout.flush()

        # 创建Flask应用 - 就像搭建一个临时的"试营业餐厅"
        app = create_app(config_path, debug_mode=debug_mode)

        # 设置优雅关闭的"保险丝"
        setup_signal_handlers(app)

        # 获取服务器配置（地址和端口）
        host = app.stacks_host
        port = app.stacks_port

        # 启动Flask开发服务器
        # 就像说："开始试营业，欢迎客人！"
        app.run(host, port, debug=debug_mode, threaded=True)
    else:
        # 🏢 生产模式：使用Gunicorn WSGI服务器
        # 就像正式营业：稳定高效，适合实际使用
        
        print(f"{INFO}◼ 正在使用Gunicorn启动Stacks...{RESET}")
        sys.stdout.flush()

        # 📤 将配置路径设置为环境变量
        # 就像把"菜单"传递给后厨工作人员
        os.environ["STACKS_CONFIG_PATH"] = config_path

        # 🔍 检查是从源代码运行还是从PEX文件运行
        # PEX是一种Python打包格式，就像把Python程序打包成exe文件
        if GUNICORN_CONFIG_FILE.exists():
            # 📝 从源代码运行
            
            # 设置PYTHONPATH - 告诉Python在哪里找模块
            current_pythonpath = os.environ.get("PYTHONPATH", "")
            src_path = str(PROJECT_ROOT / "src")
            if current_pythonpath:
                os.environ["PYTHONPATH"] = f"{src_path}:{current_pythonpath}"
            else:
                os.environ["PYTHONPATH"] = src_path

            # 构建Gunicorn启动命令
            # 就像写一个"启动脚本"
            gunicorn_cmd = [
                "gunicorn",  # 使用Gunicorn作为Web服务器
                "--config", str(GUNICORN_CONFIG_FILE),  # 使用配置文件
                "stacks.server.webserver:create_app()"  # 指定应用入口
            ]
            
            # 执行Gunicorn - 替换当前进程
            # 就像说："现在由Gunicorn接管，我们退场"
            os.execvp("gunicorn", gunicorn_cmd)
        else:
            # 📦 从PEX文件运行 - 就像从exe文件运行程序
            
            # 直接导入并运行Gunicorn
            from gunicorn.app.wsgiapp import run
            sys.argv = [
                "gunicorn",
                "--config", "python:stacks.gunicorn_config",
                "stacks.server.webserver:create_app()"
            ]
            run()

# ========== 🎬 程序启动入口点 ==========
# 这就像电影院的"检票口"，只有当观众（用户）真正运行这个文件时，
# 才会触发整个程序的启动流程

# 当这个文件被直接运行时（比如：python main.py），
# Python会自动设置 __name__ 为 "__main__"
# 如果这个文件被其他文件导入（比如：import main），__name__ 就不会是 "__main__"

if __name__ == "__main__":
    try:
        # 🎯 执行主函数 - 启动整个程序
        # 就像说："好戏开始！"
        main()  # 调用main()函数开始整个启动流程
    
    except Exception as e:
        # 🚨 如果启动过程中出现任何错误，就在这里处理
        
        # 输出错误信息到标准错误流（stderr）
        # 就像在电影院里大声喊："着火了！大家快跑！"
        print(f"\n启动过程中发生错误: {e}", file=sys.stderr)
        
        # 以错误代码1退出程序
        # 就像演砸了的演员下台一样
        sys.exit(1)  # 告诉操作系统："这个程序启动失败了"