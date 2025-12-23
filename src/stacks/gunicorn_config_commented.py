#!/usr/bin/env python3
"""
🌟 Gunicorn配置文件详解 🌟

【这个文件是什么？】
Gunicorn就像餐厅的"服务员管理系统"，负责：
- 接收顾客（用户）的订单（HTTP请求）
- 把订单分配给厨师（工作进程）
- 确保餐厅高效有序运转
- 处理突发情况（错误处理、重启等

【通俗理解】想象你开了一家餐厅：
- Gunicorn就是餐厅经理
- Workers就是厨师们
- 每个厨师一次只能做一道菜（处理一个请求）
- 经理要合理分配工作，保证服务质量

这个配置文件就是告诉"餐厅经理"该怎么管理这家"Web餐厅"。
"""

import multiprocessing  # 导入多进程模块，用于检测CPU核心数
import signal           # 导入信号处理模块，用于优雅关闭
import sys              # 导入系统模块，用于输出信息

# ========== 🍽️ 服务器基础配置 ==========
# 就像餐厅的地址和开放时间

# Server socket - 餐厅的"地址和门牌号"
# 告诉Gunicorn在哪里"开店"（监听哪个端口）
bind = "0.0.0.0:7788"  
# 说明：
# - "0.0.0.0" 就像说"在所有网络接口上都开店"
# - ":7788" 就是门牌号（端口号）
# - 用户可以通过 http://你的IP:7788 访问网站

# ========== 👨‍🍳 工作进程配置 ==========
# 就像决定雇佣多少个厨师

# Worker processes - 雇佣多少个"厨师"
# 每个工作进程可以同时处理一个请求
workers = 1
# 说明：
# - 1表示只雇佣1个厨师，一次只能做一道菜
# - 如果网站访问量大，可以增加这个数字
# - 一般设为CPU核心数的2-4倍

# Worker class - 厨师的工作方式
worker_class = "sync"  # 同步模式：厨师做完一道菜再做下一道
# 还有其他模式如"async"（异步）、"gevent"（协程）等

# Worker connections - 每个厨师同时能接多少订单
worker_connections = 1000
# 说明：即使一次只能做一道菜，但可以排队等1000个订单

# Timeout - 厨师做菜的最长时间限制
timeout = 120  # 2分钟内必须完成，超时就被换掉
# 说明：防止某个厨师卡住不动，影响整体效率

# Keepalive - 保持连接的时间
keepalive = 5  # 5秒内没有新订单就休息
# 说明：顾客点完菜后，5秒内没新动作就关闭连接，节省资源

# ========== 📝 日志配置 ==========
# 就像餐厅的营业记录本

# Access log - 顾客来访记录
accesslog = None  # 不记录访问日志，节省磁盘空间
# 如果要记录，可以设为：accesslog = "/var/log/stacks_access.log"

# Error log - 错误记录本
errorlog = "-"  # "-"表示输出到标准输出（控制台）
# 也可以设为文件路径：errorlog = "/var/log/stacks_error.log"

# Log level - 记录哪些信息
loglevel = "info"  # 只记录重要信息
# 其他级别：debug（全部）、warning（警告）、error（错误）

# Access log format - 记录格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
# 这是访问日志的格式模板，记录：IP、用户、时间、请求等

# ========== 🏷️ 进程命名 ==========
# 给餐厅和员工起名字，方便识别

# Process name - 餐厅的名字
proc_name = "stacks"  # 在系统进程列表中显示为"stacks"
# 方便用 ps 命令查看：ps aux | grep stacks

# ========== ⚙️ 服务器运行机制 ==========
# 餐厅的运营方式

# Daemon - 是否后台运行
daemon = False  # False表示前台运行，方便看日志
# True表示后台运行，像系统服务一样

# PID file - 进程ID文件
pidfile = None  # 不保存进程ID文件
# 如果保存，可以设为：pidfile = "/var/run/stacks.pid"

# User and Group - 运行用户
user = None     # 不切换用户，用启动时的用户身份运行
group = None    # 不切换用户组

# Temp upload dir - 临时上传文件夹
tmp_upload_dir = None  # 不指定临时文件夹，使用系统默认

# ========== 🔄 生命周期回调函数 ==========
# 这些函数会在Gunicorn启动、关闭等关键时刻被调用
# 就像餐厅的"营业流程"：开店、营业、关店

def on_starting(server):
    """🚪 准备开店 - Gunicorn启动前调用"""
    print("◼ Gunicorn starting...")
    sys.stdout.flush()  # 立即显示消息

def when_ready(server):
    """🎉 正式营业 - 服务器启动完成后调用"""
    print("◼ Stacks server ready")
    sys.stdout.flush()  # 告诉用户："餐厅开门了！"

def on_exit(server):
    """🚪 准备关店 - Gunicorn关闭前调用"""
    print("◼ Gunicorn shutting down...")
    sys.stdout.flush()  # 告诉用户："准备关店了！"

def worker_exit(server, worker):
    """👨‍🍳 厨师下班 - 工作进程退出后调用"""
    # 工作进程退出时会自动清理资源
    # Flask应用的工作进程和队列对象会被垃圾回收
    pass  # 什么都不做，让系统自动处理

# ========== 💡 优化建议 ==========
"""
【性能优化建议】

1. 🔢 Workers数量：
   - 当前设为1，适合小网站
   - 大网站可以设为：workers = multiprocessing.cpu_count() * 2 + 1
   
2. ⚡ 端口设置：
   - 7788是默认端口，可以根据需要修改
   - 生产环境建议使用1024以上的端口
   
3. 📝 日志配置：
   - 开发时：loglevel = "debug"
   - 生产时：loglevel = "info" 或 "warning"
   - 记得配置日志轮转，防止日志文件过大
   
4. 🛡️ 安全设置：
   - 生产环境建议设置 user = "www-data"（专用用户运行）
   - 考虑设置 max_requests 和 max_requests_jitter 防止内存泄漏
   
5. 🚀 高并发优化：
   - 增加 worker_connections（当前1000）
   - 考虑使用 async worker_class
   - 调整 timeout 和 keepalive 参数
   
6. 📊 监控：
   - 可以添加状态检查接口
   - 配置健康检查
   - 设置资源使用监控
"""

# ========== 🔧 实际使用示例 ==========
"""
【如何根据实际情况调整配置】

场景1：小型个人网站（每天访问量<1000）
workers = 1
worker_class = "sync"
timeout = 120

场景2：中型网站（每天访问量1000-10000）
workers = 4
worker_class = "sync" 或 "gevent"
timeout = 60
worker_connections = 2000

场景3：大型网站（每天访问量>10000）
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
timeout = 30
worker_connections = 5000
keepalive = 2

场景4：高并发API服务
workers = multiprocessing.cpu_count() * 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 10
worker_connections = 10000
keepalive = 1
"""