import time
import json
from stacks.constants import COOKIE_CACHE_FILE

def _load_cached_cookies(d):
    """Load cookies from cache file.

    Supports two formats:
    1. JSON format: {"timestamp": 123456, "cookies": {"name": "value", ...}}
    2. Simple dict format: {"name": "value", ...}

    If timestamp is present and cookies are >24h old, they're still loaded but marked as potentially stale.
    Cookies are set specifically for annas-archive.org domain.
    """
    if COOKIE_CACHE_FILE.exists():
        try:
            with open(COOKIE_CACHE_FILE, 'r') as f:
                data = json.load(f)

                # Detect format
                if 'cookies' in data:
                    # Format 1: Full format with timestamp
                    cookies_dict = data.get('cookies', {})
                    cached_time = data.get('timestamp', 0)

                    if time.time() - cached_time < 86400:
                        d.logger.info(f"Loaded {len(cookies_dict)} fresh cached cookies")
                    else:
                        d.logger.info(f"Loaded {len(cookies_dict)} cached cookies (potentially stale)")
                else:
                    # Format 2: Simple dict of cookies (manual entry)
                    cookies_dict = data
                    d.logger.info(f"Loaded {len(cookies_dict)} manually cached cookies")

                # Load cookies into session for annas-archive.org domain only
                for name, value in cookies_dict.items():
                    d.session.cookies.set(name, value, domain='annas-archive.org')

                return True
        except Exception as e:
            d.logger.debug(f"Failed to load cached cookies: {e}")
    return False

def _save_cookies_to_cache(d, cookies_dict):
    """Save cookies to cache file."""
    try:
        COOKIE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COOKIE_CACHE_FILE, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'cookies': cookies_dict
            }, f, indent=2)
        d.logger.debug(f"Cached {len(cookies_dict)} cookies")
    except Exception as e:
        d.logger.debug(f"Failed to cache cookies: {e}")

def _prewarm_cookies(d):
    """Pre-warm cookies using FlareSolverr if enabled."""
    if not d.flaresolverr_url:
        return False
    
    d.logger.info("Pre-warming cookies with FlareSolverr...")
    test_url = "https://annas-archive.org"

    success, cookies, _ = d.solve_with_flaresolverr(test_url)
    
    if success and cookies:
        _save_cookies_to_cache(d, cookies)
        d.logger.info("Cookies pre-warmed and cached")
        return True

    d.logger.warning("Failed to pre-warm cookies")
    return False
