import logging
import requests
from pathlib import Path
from stacks.utils.md5utils import extract_md5
from stacks.downloader.cookies import _load_cached_cookies, _save_cookies_to_cache, _prewarm_cookies
from stacks.downloader.direct import download_direct
from stacks.downloader.fast_download import try_fast_download, get_fast_download_info, refresh_fast_download_info
from stacks.downloader.flaresolver import solve_with_flaresolverr
from stacks.downloader.html import get_download_links, parse_download_link_from_html
from stacks.downloader.mirrors import download_from_mirror
from stacks.downloader.orchestrator import orchestrate_download
from stacks.downloader.utils import get_unique_filename

class AnnaDownloader:
    """
    Anna's Archive 下载器核心类
    
    这是整个下载系统的主控制器，负责协调所有下载功能。
    它就像一个"下载指挥官"，管理着下载的整个流程。
    
    核心功能：
    1. 从 Anna's Archive 网站下载电子书
    2. 支持多种下载方式（快速下载、镜像下载）
    3. 自动处理 Cloudflare 防护
    4. 支持断点续传
    5. 文件完整性验证（MD5）
    
    使用场景：
    - 用户输入一个书籍链接或 MD5 值
    - 下载器自动解析链接，找到下载源
    - 尝试多种方式下载，直到成功
    - 下载完成后验证文件完整性
    """
    
    def __init__(self, output_dir="./downloads", incomplete_dir=None, progress_callback=None,
                 fast_download_config=None, flaresolverr_url=None, flaresolverr_timeout=60000,
                 status_callback=None, prefer_title_naming=False, include_hash="none"):
        """
        初始化下载器
        
        Args:
            output_dir: 下载文件保存目录（默认：./downloads）
            incomplete_dir: 未完成下载的临时目录（默认：output_dir/incomplete）
            progress_callback: 下载进度回调函数，用于显示下载进度
            fast_download_config: 快速下载配置字典
                - enabled: 是否启用快速下载
                - key: 快速下载 API 密钥
                - api_url: 快速下载 API 地址
            flaresolverr_url: FlareSolverr 服务地址（用于绕过 Cloudflare）
            flaresolverr_timeout: FlareSolverr 请求超时时间（毫秒）
            status_callback: 状态回调函数，用于显示下载状态
            prefer_title_naming: 是否优先使用书名作为文件名
            include_hash: 是否在文件名中包含 MD5 哈希值（"none", "prefix", "suffix"）
        
        初始化流程：
        1. 创建输出目录和临时目录
        2. 创建 HTTP 会话（用于保持连接状态）
        3. 配置快速下载功能
        4. 配置 FlareSolverr（用于绕过 Cloudflare）
        5. 加载缓存的 Cookie（用于保持登录状态）
        """
        # 创建输出目录，如果不存在则自动创建
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 设置未完成下载的临时目录
        if incomplete_dir:
            self.incomplete_dir = Path(incomplete_dir)
        else:
            self.incomplete_dir = self.output_dir / "incomplete"
        self.incomplete_dir.mkdir(parents=True, exist_ok=True)

        # 创建 HTTP 会话
        # Session 对象可以保持连接，提高性能，并自动处理 Cookie
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        })
        
        # 设置日志记录器
        self.logger = logging.getLogger('stacks_downloader')
        
        # 设置回调函数
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        
        # 快速下载配置
        # 快速下载是 Anna's Archive 的会员功能，可以直接下载文件，无需等待
        self.fast_download_config = fast_download_config or {}
        self.fast_download_enabled = self.fast_download_config.get('enabled', False)
        self.fast_download_key = self.fast_download_config.get('key')
        self.fast_download_api_url = self.fast_download_config.get(
            'api_url', 
            'https://annas-archive.org/dyn/api/fast_download.json'
        )
        
        # 快速下载状态信息
        self.fast_download_info = {
            'available': bool(self.fast_download_enabled and self.fast_download_key),
            'downloads_left': None,  # 剩余下载次数
            'downloads_per_day': None,  # 每天可下载次数
            'last_refresh': 0  # 上次刷新时间
        }
        
        # 快速下载信息刷新冷却时间（1小时）
        self.fast_download_refresh_cooldown = 3600  # 1 hour
        
        # FlareSolverr 配置
        # FlareSolverr 是一个工具，用于绕过 Cloudflare 的反爬虫保护
        # 如果不配置 FlareSolverr，下载会被 Cloudflare 阻止
        if flaresolverr_url and not flaresolverr_url.startswith(('http://', 'https://')):
            flaresolverr_url = f"http://{flaresolverr_url}"

        self.flaresolverr_url = flaresolverr_url
        self.flaresolverr_timeout = flaresolverr_timeout

        # 文件名偏好配置
        self.prefer_title_naming = prefer_title_naming
        self.include_hash = include_hash  # "none", "prefix", or "suffix"

        # 记录 FlareSolverr 配置状态
        if flaresolverr_url:
            self.logger.info(f"FlareSolverr enabled: {flaresolverr_url}")
            self.logger.info("Using ALL download sources (Anna's Archive slow_download + external mirrors)")
        else:
            self.logger.info("FlareSolverr not configured - using external mirrors and slow_download with cached cookies")

        # 加载缓存的 Cookie
        # Cookie 用于保持登录状态，避免每次都需要重新登录
        self.load_cached_cookies()
    
    # ==================== Cookie 管理 ====================
    
    def load_cached_cookies(self, domain='annas-archive.org'):
        """
        从缓存加载 Cookie
        
        Cookie 是网站用来识别用户身份的小数据片段。
        加载缓存的 Cookie 可以避免每次下载都需要重新登录。
        
        Args:
            domain: Cookie 所属的域名（默认：annas-archive.org）
        
        Returns:
            加载的 Cookie 字典
        """
        return _load_cached_cookies(self, domain)

    def save_cookies_to_cache(self, cookies_dict, domain='annas-archive.org'):
        """
        保存 Cookie 到缓存
        
        当成功登录或获取到新的 Cookie 时，将其保存到文件中，
        以便下次使用。
        
        Args:
            cookies_dict: 要保存的 Cookie 字典
            domain: Cookie 所属的域名
        """
        return _save_cookies_to_cache(self, cookies_dict, domain)

    def prewarm_cookies(self):
        """
        预热 Cookie
        
        在开始下载之前，先访问网站获取有效的 Cookie。
        这可以确保下载时不会因为 Cookie 过期而失败。
        
        Returns:
            是否成功预热 Cookie
        """
        return _prewarm_cookies(self)
    
    
    # ==================== 直接下载 ====================
    
    def download_direct(self, download_url, title=None, total_size=None, supports_resume=True, resume_attempts=3, md5=None, subfolder=None):
        """
        直接从 URL 下载文件
        
        这是最基础的下载方式，直接从给定的 URL 下载文件。
        
        Args:
            download_url: 文件的直接下载链接
            title: 文件标题（用于命名）
            total_size: 文件总大小（字节）
            supports_resume: 是否支持断点续传
            resume_attempts: 断点续传尝试次数
            md5: 文件的 MD5 哈希值（用于验证完整性）
            subfolder: 子文件夹路径
        
        Returns:
            下载成功返回文件路径，失败返回 None
        
        下载流程：
        1. 检查文件是否已存在
        2. 如果支持断点续传，检查是否有未完成的下载
        3. 开始下载文件
        4. 显示下载进度
        5. 下载完成后验证 MD5
        6. 将文件从临时目录移动到最终目录
        """
        return download_direct(self, download_url, title, total_size, supports_resume, resume_attempts, md5, subfolder)
    
    
    # ==================== 下载编排器 ====================
    
    def download(self, input_string, prefer_mirror=None, resume_attempts=3, filename=None, links=None, subfolder=None):
        """
        下载编排器 - 自动化下载的核心方法
        
        这是整个下载系统的"大脑"，负责协调所有下载方式。
        它会自动选择最佳的下载方式，并在失败时尝试其他方式。
        
        Args:
            input_string: 输入字符串，可以是：
                - Anna's Archive 书籍链接
                - MD5 哈希值
            prefer_mirror: 优先使用的镜像站点（可选）
            resume_attempts: 断点续传尝试次数
            filename: 指定的文件名（可选）
            links: 预先获取的下载链接列表（可选）
            subfolder: 子文件夹路径
        
        Returns:
            下载成功返回 (True, False, filepath)
            下载失败返回 (False, False, None)
        
        自动化下载流程：
        1. 解析输入字符串，提取 MD5
        2. 获取可用的下载链接（镜像站点）
        3. 尝试快速下载（如果启用且可用）
        4. 如果快速下载失败，尝试镜像下载
        5. 遍历所有镜像站点，直到成功或全部失败
        6. 验证下载的文件完整性
        7. 返回下载结果
        
        这个方法实现了"智能下载"：
        - 自动选择最快的下载方式
        - 自动处理失败和重试
        - 自动绕过 Cloudflare 保护
        - 自动验证文件完整性
        """
        return orchestrate_download(self, input_string, prefer_mirror, resume_attempts, filename, links, subfolder)
 
 
    # ==================== 快速下载 ====================
    
    def try_fast_download(self, md5):
        """
        尝试快速下载
        
        快速下载是 Anna's Archive 的会员功能，可以直接获取下载链接，
        无需访问下载页面。这比普通下载快很多。
        
        Args:
            md5: 书籍的 MD5 哈希值
        
        Returns:
            下载成功返回文件路径，失败返回 None
        
        工作原理：
        1. 使用 API 密钥调用快速下载接口
        2. 获取直接的下载链接
        3. 使用 download_direct 下载文件
        """
        return try_fast_download(self, md5)

    def get_fast_download_info(self):
        """
        获取快速下载信息
        
        查询快速下载的配额信息，包括：
        - 剩余下载次数
        - 每天可下载次数
        
        Returns:
            快速下载信息字典
        """
        return get_fast_download_info(self)

    def refresh_fast_download_info(self, force=False):
        """
        刷新快速下载信息
        
        定期刷新快速下载的配额信息，确保信息是最新的。
        
        Args:
            force: 是否强制刷新（忽略冷却时间）
        
        Returns:
            刷新后的快速下载信息
        """
        return refresh_fast_download_info(self, force)
    
    
    # ==================== FlareSolverr 集成 ====================
    
    def solve_with_flaresolverr(self, url):
        """
        使用 FlareSolverr 绕过 Cloudflare 保护
        
        Cloudflare 是一个反爬虫服务，会阻止自动化请求。
        FlareSolverr 是一个工具，可以模拟浏览器行为，绕过 Cloudflare。
        
        Args:
            url: 要访问的 URL
        
        Returns:
            (success, cookies, html_content)
            - success: 是否成功绕过
            - cookies: 获取的 Cookie
            - html_content: 页面 HTML 内容
        
        工作原理：
        1. 向 FlareSolverr 发送请求
        2. FlareSolverr 使用无头浏览器访问 URL
        3. FlareSolverr 等待 Cloudflare 验证完成
        4. FlareSolverr 返回验证后的 Cookie 和页面内容
        5. 使用这些 Cookie 继续下载
        """
        return solve_with_flaresolverr(self, url)
    
    
    # ==================== HTML 解析 ====================
    
    def parse_download_link_from_html(self, html_content, md5, mirror_url=None):
        """
        从 HTML 页面解析下载链接
        
        Anna's Archive 的下载页面包含下载链接，但不是直接的文件链接。
        需要解析 HTML 提取真正的下载链接。
        
        Args:
            html_content: HTML 页面内容
            md5: 书籍的 MD5 哈希值
            mirror_url: 镜像站点的 URL（用于日志）
        
        Returns:
            解析出的下载链接，失败返回 None
        
        解析过程：
        1. 使用正则表达式或 HTML 解析器查找下载链接
        2. 提取链接中的文件 URL
        3. 返回直接下载链接
        """
        return parse_download_link_from_html(self, html_content, md5, mirror_url)

    def get_download_links(self, md5):
        """
        获取下载链接列表
        
        从 Anna's Archive 获取所有可用的下载镜像链接。
        每个镜像都是不同的下载源，速度和可用性可能不同。
        
        Args:
            md5: 书籍的 MD5 哈希值
        
        Returns:
            下载链接列表，每个元素包含：
            - url: 下载页面 URL
            - type: 镜像类型（如 "slow_download", "external_mirror"）
            - domain: 域名
            - text: 显示文本
        
        工作原理：
        1. 访问书籍页面
        2. 解析页面中的下载链接
        3. 返回所有可用的镜像链接
        """
        return get_download_links(self, md5)
    
    
    # ==================== 镜像下载 ====================
    
    def download_from_mirror(self, mirror_url, mirror_type, md5, title=None, resume_attempts=3, subfolder=None):
        """
        从镜像站点下载
        
        镜像站点是 Anna's Archive 的合作伙伴，提供相同的文件。
        使用镜像可以分散负载，提高下载成功率。
        
        Args:
            mirror_url: 镜像站点的 URL
            mirror_type: 镜像类型（"slow_download" 或 "external_mirror"）
            md5: 书籍的 MD5 哈希值
            title: 文件标题
            resume_attempts: 断点续传尝试次数
            subfolder: 子文件夹路径
        
        Returns:
            下载成功返回文件路径，失败返回 None
        
        下载流程：
        1. 访问镜像站点的下载页面
        2. 如果遇到 Cloudflare 保护，使用 FlareSolverr 绕过
        3. 解析页面获取直接下载链接
        4. 使用 download_direct 下载文件
        5. 验证文件完整性
        """
        return download_from_mirror(self, mirror_url, mirror_type, md5, title, resume_attempts, subfolder)


    # ==================== 工具方法 ====================
    
    def extract_md5(self, input_string):
        """
        从输入字符串中提取 MD5 哈希值
        
        用户可以输入书籍链接或 MD5 值，这个方法会自动识别并提取 MD5。
        
        Args:
            input_string: 输入字符串（链接或 MD5）
        
        Returns:
            提取的 MD5 哈希值
        """
        return extract_md5(input_string)

    def get_unique_filename(self, base_path):
        """
        生成唯一的文件名
        
        如果文件已存在，在文件名后添加数字后缀，避免覆盖。
        
        Args:
            base_path: 基础文件路径
        
        Returns:
            唯一的文件路径
        
        示例：
            - 如果 "book.pdf" 已存在，返回 "book (1).pdf"
            - 如果 "book (1).pdf" 也存在，返回 "book (2).pdf"
        """
        return get_unique_filename(self, base_path)

    def cleanup(self):
        """
        清理资源
        
        在下载完成后，关闭 HTTP 会话，释放资源。
        这是一种良好的编程实践，避免资源泄漏。
        """
        try:
            if hasattr(self, 'session') and self.session:
                self.logger.info("Closing HTTP session...")
                self.session.close()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
