#!/usr/bin/env python3
"""
🌟 Gunicorn配置文件 - Stacks Web服务器设置 🌟

【这个文件的作用】
这个文件就像餐厅的"运营手册"，告诉Gunicorn（Web服务器）怎么管理网站：
- 在哪里"开店"（端口设置）
- 雇多少"员工"（工作进程）
- 怎么"服务顾客"（处理请求）
- 什么时候"开关门"（启动关闭流程）

【通俗理解】想象你开了一家在线餐厅：
- Gunicorn是餐厅经理
- 每个工作进程是一个厨师
- 顾客下单就是HTTP请求
- 厨师做菜就是处理请求

这个配置文件就是告诉经理：
- 餐厅地址在哪里（0.0.0.0:7788）
- 雇几个厨师（workers = 1）
- 厨师的工作方式（同步模式）
- 等等各种运营细节
"""

import multiprocessing  # 🔢 多进程模块，用于检测CPU核心数
import signal           # 📞 信号处理模块，用于优雅关闭程序
import sys              # 💻 系统模块，用于输出信息

# ========== 🏠 服务器基础设置 ==========
# 就像决定餐厅开在哪里、什么时间营业

# Server socket - 服务器监听地址和端口
bind = "0.0.0.0:7788"
"""
【解释】
- "0.0.0.0" = 在所有网络接口上监听（内外网都能访问）
- "7788" = 端口号，顾客通过 http://你的IP:7788 访问网站
- 就像餐厅地址：某某市某某区某某路7788号
"""

# ========== 👨‍🍳 工作进程设置 ==========
# 就像决定雇多少个厨师，每个厨师怎么工作

# Worker processes - 雇佣的工作进程数量
workers = 1
"""
【解释】
- 1 = 只雇1个厨师，一次只能处理1个请求
- 如果网站访问量大，需要增加数量
- 一般设为CPU核心数的2-4倍
"""

# Worker class - 工作进程类型
worker_class = "sync"
"""
【解释】
- "sync" = 同步模式：厨师做完一道菜再做下一道
- 还有 "async"（异步）、"gevent"（协程）等
- 同步模式简单稳定，适合大多数情况
"""

# Worker connections - 每个工作进程的最大连接数
worker_connections = 1000
"""
【解释】
- 每个厨师可以排队等待1000个订单
- 即使一次只能做一道菜，但可以有很多顾客排队等待
"""

# Timeout - 请求超时时间（秒）
timeout = 120
"""
【解释】
- 2分钟内厨师必须做完一道菜，否则换人
- 防止某个请求卡住影响其他请求
"""

# Keepalive - 保持连接时间（秒）
keepalive = 5
"""
【解释】
- 顾客点完菜后5秒内没新动作就断开连接
- 节省服务器资源，避免连接数过多
"""

# ========== 📝 日志设置 ==========
# 就像餐厅的营业记录本

# Access log - 访问日志
accesslog = None
"""
【解释】
- None = 不记录访问日志，节省磁盘空间
- 可以设为文件路径如 "/var/log/stacks_access.log"
"""

# Error log - 错误日志
errorlog = "-"
"""
【解释】
- "-" = 输出到控制台（标准输出）
- 也可以设为文件路径如 "/var/log/stacks_error.log"
"""

# Log level - 日志级别
loglevel = "info"
"""
【解释】
- "info" = 只记录重要信息
- 其他级别：debug（全部）、warning（警告）、error（错误）
"""

# Access log format - 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
"""
【解释】
- 记录格式：IP、用户、时间、请求、状态码、字节数、来源页面、浏览器等
- 这是标准格式，记录网站访问的详细信息
"""

# ========== 🏷️ 进程命名 ==========
# 给服务器和进程起名字，方便识别

# Process name - 进程名称
proc_name = "stacks"
"""
【解释】
- 在系统进程列表中显示为"stacks"
- 方便用 ps aux | grep stacks 查看进程状态
"""

# ========== ⚙️ 服务器运行机制 ==========
# 餐厅的运营方式设置

# Daemon - 是否后台运行
daemon = False
"""
【解释】
- False = 前台运行，方便看日志和调试
- True = 后台运行，像Windows服务一样
"""

# PID file - 进程ID文件
pidfile = None
"""
【解释】
- None = 不保存进程ID到文件
- 可以设为 "/var/run/stacks.pid" 方便管理
"""

# User and Group - 运行用户和组
user = None
group = None
"""
【解释】
- None = 使用启动程序时的用户身份运行
- 生产环境建议设为专用用户如 "www-data"
"""

# Temp upload dir - 临时上传目录
tmp_upload_dir = None
"""
【解释】
- None = 使用系统默认临时目录
- 可以指定专用目录如 "/tmp/stacks_uploads"
"""

# ========== 🔄 生命周期回调函数 ==========
# 这些函数在服务器启动、关闭等关键时刻被调用

def on_starting(server):
    """🚪 准备开店 - Gunicorn启动前调用"""
    print("◼ Gunicorn starting...")
    sys.stdout.flush()  # 立即显示消息，不等待缓冲区

def when_ready(server):
    """🎉 正式营业 - 服务器启动完成后调用"""
    print("◼ Stacks server ready")
    sys.stdout.flush()  # 告诉用户服务器已经准备好了

def on_exit(server):
    """🚪 准备关店 - Gunicorn关闭前调用"""
    print("◼ Gunicorn shutting down...")
    sys.stdout.flush()  # 告诉用户服务器正在关闭

def worker_exit(server, worker):
    """👨‍🍳 厨师下班 - 工作进程退出后调用"""
    # Cleanup happens automatically when the worker process exits
    # The Flask app's worker and queue objects will be garbage collected
    """
    【解释】
    - 工作进程退出时自动清理资源
    - Flask应用的工作进程和队列对象会被垃圾回收
    - pass 表示什么都不做，让系统自动处理
    """
    pass
