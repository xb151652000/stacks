def download_from_mirror(d, mirror_url, mirror_type, md5, title=None, resume_attempts=3, subfolder=None):
    """
    从镜像站点下载文件（支持 Cookie 过期处理和 Cloudflare 防护绕过）

    这是"镜像下载器"，它的任务是从各种镜像站点下载文件。
    镜像站点通常有 Cloudflare 防护，所以我们需要使用 Cookie 和 FlareSolverr 来绕过。

    核心挑战：
    1. Cloudflare 防护：需要有效的 Cookie 或 FlareSolverr 来绕过
    2. Cookie 过期：Cookie 可能会过期，需要刷新或使用 FlareSolverr
    3. 不同镜像类型：slow_download 和 external_mirror 的处理方式不同

    Args:
        d: 下载器实例（AnnaDownloader 对象，包含 session、logger、配置等）
        mirror_url: 镜像站点的 URL（如 'https://annas-archive.org/slow_download/abc123'）
        mirror_type: 镜像类型，有两种：
            - 'slow_download': Anna's Archive 的慢速下载服务器
            - 'external_mirror': 外部镜像站点（如 libgen.is、archive.org 等）
        md5: 文件的 MD5 哈希值（用于验证下载链接的正确性）
        title: 文件标题（可选，用于保存文件时的命名）
        resume_attempts: 断点续传尝试次数（默认 3 次）
        subfolder: 子文件夹路径（可选，用于将文件保存到指定子文件夹）

    Returns:
        str: 下载的文件路径（如果成功）
        None: 如果下载失败

    工作流程：
    1. 根据 mirror_type 选择不同的处理策略
    2. 加载缓存的 Cookie（如果有的话）
    3. 访问镜像站点 URL
    4. 如果遇到 403/503 错误，使用 FlareSolverr 绕过防护
    5. 从 HTML 内容中提取下载链接
    6. 使用 download_direct 方法下载文件

    两种镜像类型的区别：
    - slow_download: 使用预热的 Cookie，遇到防护时直接使用 FlareSolverr
    - external_mirror: 先尝试直接访问，失败后刷新 Cookie，最后才使用 FlareSolverr
    """
    try:
        # ========== 情况 1：处理慢速下载 ==========
        if mirror_type == 'slow_download':
            d.logger.debug("访问慢速下载页面（通过 Cookie）")

            # 尝试加载缓存的 Cookie
            # Cookie 就像是"通行证"，可以绕过 Cloudflare 的部分检查
            d.load_cached_cookies(domain='annas-archive.org')

            # 如果有状态回调函数，通知用户当前状态
            # 这可以让用户界面显示下载进度
            if hasattr(d, 'status_callback'):
                d.status_callback("正在访问慢速下载页面...")

            try:
                # 使用 Cookie 访问慢速下载页面
                # timeout=30 表示最多等待 30 秒
                response = d.session.get(mirror_url, timeout=30)

                # ========== 检测 Cloudflare 防护 ==========
                # 403 = 禁止访问（通常是 Cloudflare 防护）
                # 503 = 服务不可用（可能是 Cloudflare 挑战页面）
                if response.status_code in [403, 503]:
                    # 如果没有配置 FlareSolverr，无法绕过防护
                    if not d.flaresolverr_url:
                        d.logger.warning(f"收到 {response.status_code} 错误，但未配置 FlareSolverr")
                        return None

                    d.logger.warning(f"收到 {response.status_code} 错误，正在使用 FlareSolverr 绕过防护...")

                    if hasattr(d, 'status_callback'):
                        d.status_callback("正在使用 FlareSolverr 解决验证码...")

                    # 使用 FlareSolverr 绕过 Cloudflare 防护
                    # FlareSolverr 是一个代理服务，可以自动解决 Cloudflare 挑战
                    success, cookies, html_content = d.solve_with_flaresolverr(mirror_url)

                    if not success:
                        d.logger.error("FlareSolverr 绕过失败")
                        return None

                    if hasattr(d, 'status_callback'):
                        d.status_callback("正在提取下载链接...")

                    # 从绕过防护后的 HTML 内容中提取下载链接
                    download_link = d.parse_download_link_from_html(html_content, md5, mirror_url)
                    if not download_link:
                        d.logger.warning("无法找到下载链接")
                        return None

                    if hasattr(d, 'status_callback'):
                        d.status_callback("正在下载文件...")

                    d.logger.info("通过 FlareSolverr 找到下载 URL，开始下载...")
                    # 使用直接下载方法下载文件
                    return d.download_direct(download_link, title=title, resume_attempts=resume_attempts, md5=md5, subfolder=subfolder)

                # 如果没有遇到防护，检查 HTTP 状态码
                # raise_for_status() 会在 4xx/5xx 错误时抛出异常
                response.raise_for_status()

                if hasattr(d, 'status_callback'):
                    d.status_callback("正在提取下载链接...")

                # 从 HTML 内容中提取下载链接
                download_link = d.parse_download_link_from_html(response.text, md5, mirror_url)
                if not download_link:
                    d.logger.warning("无法找到下载链接")
                    return None

                if hasattr(d, 'status_callback'):
                    d.status_callback("正在下载文件...")

                d.logger.info("找到下载 URL，开始下载...")
                return d.download_direct(download_link, title=title, resume_attempts=resume_attempts, md5=md5, subfolder=subfolder)

            except Exception as e:
                d.logger.error(f"访问慢速下载页面时出错: {e}")
                return None
        
        # ========== 情况 2：处理外部镜像 ==========
        else:  # external_mirror
            d.logger.debug(f"访问外部镜像: {mirror_url}")

            # 尝试加载缓存的 Cookie（针对这个镜像站点）
            d.load_cached_cookies(domain=mirror_url)

            try:
                # 尝试直接访问外部镜像
                response = d.session.get(mirror_url, timeout=30)

                # ========== 处理 403 错误（访问被拒绝）==========
                if response.status_code == 403:
                    # 如果配置了 FlareSolverr，尝试解决
                    if d.flaresolverr_url:
                        d.logger.warning("收到 403 错误 - 尝试刷新 Cookie")

                        # 尝试预热新的 Cookie
                        # prewarm_cookies() 会访问主页来获取新的有效 Cookie
                        if d.prewarm_cookies():
                            d.logger.info("使用新 Cookie 重试...")
                            # 使用新 Cookie 重新访问镜像
                            response = d.session.get(mirror_url, timeout=30)

                            if response.status_code == 403:
                                # 新 Cookie 也失败了，需要使用 FlareSolverr
                                d.logger.warning("刷新 Cookie 后仍然收到 403 错误，将使用 FlareSolverr 完整解决")
                            else:
                                # 新 Cookie 成功了，继续处理
                                response.raise_for_status()

                                if hasattr(d, 'status_callback'):
                                    d.status_callback("正在提取下载链接...")

                                download_link = d.parse_download_link_from_html(response.text, md5, mirror_url)
                                if not download_link:
                                    d.logger.warning("无法找到下载链接")
                                    return None

                                if hasattr(d, 'status_callback'):
                                    d.status_callback("正在下载文件...")

                                return d.download_direct(download_link, title=title, resume_attempts=resume_attempts, md5=md5, subfolder=subfolder)

                        # 如果 Cookie 刷新失败或仍然收到 403，使用 FlareSolverr
                        if hasattr(d, 'status_callback'):
                            d.status_callback("正在使用 FlareSolverr 解决验证码...")
                        success, cookies, html_content = d.solve_with_flaresolverr(mirror_url)

                        if success:
                            if hasattr(d, 'status_callback'):
                                d.status_callback("正在提取下载链接...")
                            download_link = d.parse_download_link_from_html(html_content, md5, mirror_url)
                            if download_link:
                                if hasattr(d, 'status_callback'):
                                    d.status_callback("正在下载文件...")
                                d.logger.info("通过 FlareSolverr 找到下载 URL，开始下载...")
                                return d.download_direct(download_link, title=title, resume_attempts=resume_attempts, md5=md5, subfolder=subfolder)
                        return None
                    else:
                        # 没有配置 FlareSolverr，无法解决 403 错误
                        d.logger.warning("收到 403 错误但未配置 FlareSolverr")
                        return None

                # 检查 HTTP 状态码
                response.raise_for_status()

                if hasattr(d, 'status_callback'):
                    d.status_callback("正在提取下载链接...")

                # 从 HTML 内容中提取下载链接
                download_link = d.parse_download_link_from_html(response.text, md5, mirror_url)
                if not download_link:
                    d.logger.warning("无法找到下载链接")
                    return None

                if hasattr(d, 'status_callback'):
                    d.status_callback("正在下载文件...")

                return d.download_direct(download_link, title=title, resume_attempts=resume_attempts, md5=md5, subfolder=subfolder)

            except Exception as e:
                d.logger.error(f"访问外部镜像时出错: {e}")
                return None
    
    except Exception as e:
        d.logger.error(f"从镜像下载时出错: {e}")
        return None
