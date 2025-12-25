import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from stacks.downloader.sites.zlib import parse_zlib_download_link, is_zlib_domain
from stacks.constants import LEGAL_FILES

def parse_download_link_from_html(d, html_content, md5, mirror_url=None):
        """
        从 HTML 内容中解析出实际的文件下载链接
        
        这个函数是"链接提取器"，它的任务是从镜像站点的 HTML 页面中
        找到真正的文件下载链接。由于不同的镜像站点结构不同，我们需要
        使用多种方法来提取链接。
        
        核心挑战：
        1. 不同镜像站点的 HTML 结构不同
        2. 下载链接可能隐藏在各种 HTML 元素中（<a>、<button>、<span> 等）
        3. 需要区分真正的下载链接和导航链接
        
        Args:
            d: 下载器实例（用于访问日志记录器等）
            html_content: 从镜像站点获取的 HTML 内容
            md5: 文件的 MD5 哈希值（用于验证链接的正确性）
            mirror_url: 镜像站点的 URL（用于站点特定的解析器）
        
        Returns:
            str: 下载链接的完整 URL
            None: 如果没有找到下载链接
        
        工作流程：
        1. 首先尝试使用站点特定的解析器（如 Z-Library）
        2. 如果站点特定解析器失败，使用通用解析方法
        3. 通用解析方法会尝试 4 种不同的策略来查找下载链接
        """
        # ==================== 步骤 1: 尝试使用站点特定的解析器 ====================
        if mirror_url:
            # 检查是否是 Z-Library 域名
            if is_zlib_domain(mirror_url):
                d.logger.debug("使用 Z-Library 专用解析器")
                # 调用 Z-Library 专用的链接解析函数
                download_link = parse_zlib_download_link(d, html_content, mirror_url)
                if download_link:
                    return download_link
                d.logger.debug("Z-Library 解析器未找到链接，回退到通用解析器")

        # ==================== 步骤 2: 使用通用解析方法 ====================
        # 创建 BeautifulSoup 对象，用于解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 获取 MD5 的前 12 个字符
        # 下载链接通常包含 MD5 的前缀作为文件名的一部分
        # 例如：https://example.com/files/abc123def456.../book.epub
        md5_prefix = md5[:12]
        
        # 定义需要跳过的域名列表
        # 这些域名不是真正的文件托管站点，而是导航链接或社交媒体链接
        skip_domains = [
            'jdownloader.org',      # 下载管理器网站
            'telegram.org', 't.me', # Telegram 链接
            'discord.gg',           # Discord 链接
            'reddit.com',           # Reddit 链接
            'twitter.com',          # Twitter 链接
            'facebook.com',         # Facebook 链接
            'instagram.com',        # Instagram 链接
            'patreon.com',          # Patreon 链接
            'ko-fi.com',            # Ko-fi 链接
            'buymeacoffee.com',     # 捐赠链接
            'annas-archive.org/account',  # 账户页面
            'annas-archive.org/search',   # 搜索页面
            'annas-archive.org/md5',      # MD5 页面
            'annas-archive.org/donate',   # 捐赠页面
            '.onion'                # Tor 暗网链接
        ]

        # ==================== 方法 1: 查找包含 MD5 前缀的链接 ====================
        # 这是最常用的方法，适用于 slow_download 页面
        # 下载链接通常包含文件的 MD5 前缀
        for link in soup.find_all('a', href=True):
            href = link['href']

            # 必须是完整的 URL（以 http:// 或 https:// 开头）
            if not href.startswith('http'):
                continue

            # 跳过导航链接、社交媒体链接和 .onion 链接
            if any(skip in href.lower() for skip in skip_domains):
                continue

            # 跳过 slow_download 页面本身
            # 我们要找的是真正的文件下载链接，而不是另一个 slow_download 页面
            if 'slow_download' in href.lower():
                continue

            # 如果链接包含 MD5 前缀，很可能是下载链接
            if md5_prefix in href.lower():
                d.logger.debug(f"找到包含 MD5 前缀的下载链接: {href}")
                return href
        
        # ==================== 方法 2: 查找包含文件扩展名的链接 ====================
        # 这是外部镜像的备用方法
        # 查找包含 "download" 或 "get" 文本的链接，并且链接包含合法的文件扩展名
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text().strip().lower()
            
            # 必须是完整的 URL
            if not href.startswith('http'):
                continue
            
            # 跳过导航链接
            if any(skip in href.lower() for skip in skip_domains):
                continue
            
            # 查找包含下载指示词的链接
            if 'download' in link_text or 'get' in link_text:
                # 检查链接是否包含合法的文件扩展名或常见的下载脚本
                if any(ext in href.lower() for ext in LEGAL_FILES) \
                   or 'get.php' in href.lower() or 'main.php' in href.lower():
                    d.logger.debug(f"通过备用方法找到下载链接: {href}")
                    return href

        # ==================== 方法 3: 查找包含 URL 的剪贴板按钮 ====================
        # 有些站点使用 JavaScript 将下载链接复制到剪贴板
        # 按钮的 onclick 事件中包含 writeText() 函数，参数就是下载链接
        for btn in soup.find_all('button', onclick=True):
            onclick = btn['onclick']
            # 使用正则表达式提取 writeText() 函数中的 URL
            match = re.search(r"writeText\('([^']+)'", onclick)
            if match:
                url = match.group(1)

                # 验证 URL 是否包含 MD5 前缀
                if md5_prefix not in url:
                    continue

                # 返回完整的 URL（包括签名部分，即 ~/ 之后的所有内容）
                d.logger.debug(f"从剪贴板按钮找到 URL: {url}")
                return url
            
        # ==================== 方法 4: 查找包含原始 URL 的 span 元素 ====================
        # 有些站点直接在 <span> 标签中显示下载链接
        for span in soup.find_all('span'):
            text = span.get_text(strip=True)

            # 必须以 http 开头
            if not text.startswith("http"):
                continue
            # 必须包含 MD5 前缀
            if md5_prefix not in text:
                continue

            # 返回完整的 URL
            d.logger.debug(f"从 span 元素找到原始 URL: {text}")
            return text

        # 如果所有方法都失败了，返回 None
        return None
    
def get_download_links(d, md5):
    """
    从 Anna's Archive 网站获取书籍的下载链接列表和文件名
    
    这个函数是"链接收集器"，它的任务是：
    1. 访问 Anna's Archive 的书籍页面
    2. 从页面中提取文件名（用于保存下载的文件）
    3. 从页面中提取所有可用的下载链接（包括慢速下载和外部镜像）
    
    核心功能：
    - 智能文件名提取（支持多种提取策略）
    - 过滤掉等待队列服务器（只选择无等待的服务器）
    - 收集所有可用的外部镜像链接
    
    Args:
        d: 下载器实例（包含 session、logger、配置等）
        md5: 书籍的 MD5 哈希值
    
    Returns:
        tuple: (filename, links)
            - filename: 提取的文件名（如 "Book Title.epub"）
            - links: 下载链接列表，每个链接是一个字典，包含：
                - url: 完整的下载 URL
                - domain: 域名
                - text: 显示文本（服务器名称）
                - type: 链接类型（'slow_download' 或 'external_mirror'）
    
    返回示例：
        ("Python编程从入门到实践.epub", [
            {
                'url': 'https://annas-archive.org/slow_download/abc123...',
                'domain': 'annas-archive.org',
                'text': 'Slow Partner Server',
                'type': 'slow_download'
            },
            {
                'url': 'https://libgen.is/get.php?md5=abc123...',
                'domain': 'libgen.is',
                'text': 'libgen.is',
                'type': 'external_mirror'
            }
        ])
    """
    # 构建书籍页面的 URL
    # Anna's Archive 的书籍页面格式：https://annas-archive.org/md5/{md5}
    url = f"https://annas-archive.org/md5/{md5}"

    try:
        # 使用 HTTP 会话访问书籍页面
        # 使用 session 可以保持 Cookie，提高访问成功率
        response = d.session.get(url, timeout=30)
        response.raise_for_status()  # 如果请求失败，抛出异常

        # 使用 BeautifulSoup 解析 HTML 内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # ==================== 辅助函数 1: 从 Filepath 元数据中提取文件名 ====================
        def extract_from_filepath():
            """
            从页面的 Filepath 元数据中提取原始文件名
            
            Anna's Archive 会显示文件的原始路径，例如：
            - Windows 路径：R:\Books\Python编程从入门到实践.epub
            - Unix 路径：lgli/Python编程从入门到实践.epub
            
            Returns:
                str: 提取的文件名，如果没有找到则返回 None
            """
            # 查找所有包含 MD5 代码的标签
            filepath_elements = soup.find_all('a', class_='js-md5-codes-tabs-tab')
            for element in filepath_elements:
                # 查找标签为 "Filepath" 的 span 元素
                label_span = element.find('span', class_='bg-[#aaa]')
                if label_span and 'Filepath' in label_span.get_text():
                    # 获取第二个 span 元素，它包含实际的文件路径
                    filepath_span = element.find_all('span')[1] if len(element.find_all('span')) > 1 else None
                    if filepath_span:
                        filepath_text = filepath_span.get_text().strip()

                        # 处理 Windows 风格的路径（R:\...\filename）
                        if '\\' in filepath_text:
                            filename = filepath_text.split('\\')[-1]
                        # 处理 Unix 风格的路径（lgli/filename 或 lgrsfic/filename）
                        elif '/' in filepath_text:
                            filename = filepath_text.split('/')[-1]
                        else:
                            filename = filepath_text

                        # URL 解码文件名（将 + 替换为空格等）
                        filename = filename.replace('+', ' ')

                        # 如果找到了有效的文件名，返回它
                        if filename and filename.strip():
                            d.logger.info(f"从 Filepath 元数据中提取文件名: {filename}")
                            return filename
            return None

        # ==================== 辅助函数 2: 从页面标题中提取文件名 ====================
        def extract_from_title():
            """
            从书籍标题和元数据中构建文件名
            
            这个方法会：
            1. 从页面标题中提取书籍名称
            2. 从元数据中提取文件扩展名（如 .pdf、.epub）
            3. 将它们组合成完整的文件名
            
            Returns:
                str: 构建的文件名，如果没有找到则返回 None
            """
            # 查找书籍信息 div（包含标题）
            # 使用 CSS 类选择器查找标题元素
            title_div = soup.find('div', class_=lambda x: x and 'font-semibold' in x and 'text-2xl' in x and 'leading-[1.2]' in x)
            title = None
            extension = None

            if title_div:
                # 获取文本内容，排除嵌套标签（如搜索图标链接）
                title = title_div.get_text(strip=True)
                # 移除搜索表情符号（如果有）
                title = title.replace('🔍', '').strip()
                d.logger.info(f"从书籍信息 div 中提取标题: {title}")
            else:
                d.logger.warning("未找到包含所需类的标题 div")

            # 查找元数据 div（包含文件扩展名等信息）
            metadata_div = soup.find('div', class_=lambda x: x and 'text-gray-800' in x and 'font-semibold' in x and 'text-sm' in x and 'mt-4' in x)

            if metadata_div:
                # 获取文本并用中间点（·）分割
                metadata_text = metadata_div.get_text(separator=' ', strip=True)
                parts = [part.strip() for part in metadata_text.split('·')]

                # 查找匹配合法文件扩展名的部分
                for part in parts:
                    part_upper = part.upper()
                    for legal_ext in LEGAL_FILES:
                        # 检查这个部分是否是扩展名（如 "PDF"、"EPUB"）
                        if part_upper == legal_ext.upper().replace('.', ''):
                            extension = legal_ext
                            d.logger.info(f"从元数据中提取扩展名: {extension}")
                            break
                    if extension:
                        break

            # 构建文件名
            if title and extension:
                # 清理标题中的非法文件名字符
                title = re.sub(r'[<>:"/\\|?*]', '_', title)
                # 移除末尾的句点和空格，避免双重扩展名（如 "title..pdf"）
                title = title.rstrip('. ')
                return f"{title}{extension}"
            elif title:
                # 没有找到扩展名，只使用标题
                d.logger.warning("未能从元数据中提取文件扩展名")
                return title
            else:
                # 没有找到标题
                return None

        # ==================== 步骤 1: 提取文件名 ====================
        filename = None
        # 根据用户偏好选择提取方法
        if d.prefer_title_naming:
            # 优先使用基于标题的命名方式
            d.logger.info("使用基于标题的文件名提取（首选）")
            filename = extract_from_title()
            if not filename or filename == "Unknown":
                d.logger.warning("标题提取失败，回退到 Filepath 元数据")
                filename = extract_from_filepath()
        else:
            # 优先使用 Filepath 元数据（默认）
            filename = extract_from_filepath()
            if not filename:
                d.logger.warning("未找到 Filepath 元数据，回退到标题提取")
                filename = extract_from_title()

        # 最终回退方案 - 在文件名中使用 MD5 哈希值
        if not filename:
            d.logger.warning("未找到文件名，回退到 Unknown")
            filename = f"Unknown ({md5})"
        elif d.include_hash == "prefix":
            # 在文件名前添加 MD5
            filename = f"{md5} - {filename}"
        elif d.include_hash == "suffix":
            # 在文件名后添加 MD5
            filename = f"{filename} - {md5}"

        # ==================== 步骤 2: 收集下载链接 ====================
        links = []
        
        # 查找下载面板 div
        # 下载面板包含所有的下载链接
        downloads_panel = soup.find('div', id='md5-panel-downloads')
        if not downloads_panel:
            d.logger.warning("页面上未找到下载面板")
            return filename, links
        
        # ==================== 收集慢速下载链接 ====================
        # 只接受 "no waitlist"（无等待）的服务器
        for li in downloads_panel.find_all('li', class_='list-disc'):
            a = li.find('a', href=True)
            if not a:
                continue
            
            href = a['href']
            li_text = li.get_text().strip()
            
            # 跳过快速下载链接（我们通过 API 处理）
            if '/fast_download/' in href:
                continue
            
            # 只接受慢速下载链接
            if '/slow_download/' in href:
                # 跳过等待队列服务器（它们有 60 秒的 JavaScript 倒计时）
                if 'slightly faster but with waitlist' in li_text.lower():
                    d.logger.debug(f"跳过等待队列服务器: {a.get_text().strip()}")
                    continue
                
                # 接受无等待服务器
                if 'no waitlist' in li_text.lower():
                    # 将相对 URL 转换为绝对 URL
                    full_url = urljoin(url, href)
                    server_name = a.get_text().strip() or "Slow Partner Server"
                    
                    links.append({
                        'url': full_url,
                        'domain': 'annas-archive.org',
                        'text': server_name,
                        'type': 'slow_download'
                    })
                    d.logger.debug(f"添加无等待服务器: {server_name}")
        
        # ==================== 收集外部镜像链接 ====================
        # 在 js-show-external ul 中查找
        external_ul = downloads_panel.find('ul', class_='js-show-external')
        if external_ul:
            for a in external_ul.find_all('a', href=True):
                href = a['href']

                # 只添加完整的 URL
                if not href.startswith('http'):
                    continue

                # 跳过 .onion URL（Tor 暗网链接）
                if '.onion' in href.lower():
                    d.logger.debug(f"跳过 .onion URL: {href}")
                    continue

                # 解析 URL 获取域名
                parsed = urlparse(href)
                domain = parsed.netloc

                # 如果没有有效域名，跳过
                if not domain:
                    continue

                links.append({
                    'url': href,
                    'domain': domain,
                    'text': domain,
                    'type': 'external_mirror'
                })
                d.logger.debug(f"添加外部镜像: {domain}")

        return filename, links

    except Exception as e:
        d.logger.error(f"获取下载链接时出错: {e}")
        return "Unknown", []