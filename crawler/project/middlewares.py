"""
Scrapy中间件
- 代理中间件
- User-Agent中间件
- Cookie中间件
- 重试中间件
"""
import random
import logging
from typing import Optional

from scrapy import signals
from scrapy.http import Request, Response
from scrapy.exceptions import IgnoreRequest
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware:
    """随机User-Agent中间件"""
    
    def __init__(self):
        self.ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self.mobile_ua_list = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/119.0.0.0 Mobile Safari/537.36",
        ]
    
    def process_request(self, request: Request, spider) -> None:
        # 检查是否需要移动端UA
        if request.meta.get("mobile", False):
            ua = random.choice(self.mobile_ua_list)
        else:
            ua = self.ua.random
        
        request.headers["User-Agent"] = ua


class ProxyMiddleware:
    """代理中间件"""
    
    def __init__(self, proxy_pool_url: str, enabled: bool = True):
        self.proxy_pool_url = proxy_pool_url
        self.enabled = enabled
        self._proxy_pool = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_pool_url=crawler.settings.get("PROXY_POOL_URL"),
            enabled=crawler.settings.getbool("PROXY_POOL_ENABLED", True),
        )
    
    @property
    def proxy_pool(self):
        if self._proxy_pool is None:
            from libs.proxy_pool import ProxyPool
            self._proxy_pool = ProxyPool(self.proxy_pool_url)
        return self._proxy_pool
    
    def process_request(self, request: Request, spider) -> None:
        if not self.enabled:
            return
        
        # 跳过不需要代理的请求
        if request.meta.get("no_proxy", False):
            return
        
        proxy = self.proxy_pool.get_proxy()
        if proxy:
            request.meta["proxy"] = proxy
            logger.debug(f"Using proxy: {proxy}")
    
    def process_exception(self, request: Request, exception, spider):
        """代理失败时删除并重试"""
        proxy = request.meta.get("proxy")
        if proxy:
            self.proxy_pool.delete_proxy(proxy)
            logger.warning(f"Proxy failed, removed: {proxy}")
        
        # 返回新请求进行重试
        return request.copy()


class CookieMiddleware:
    """Cookie池中间件"""
    
    def __init__(self, redis_host: str, redis_port: int, redis_db: int, redis_password: str):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_password = redis_password
        self._cookie_pool = None
        self._cookie_manager = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            redis_host=crawler.settings.get("REDIS_HOST"),
            redis_port=crawler.settings.getint("REDIS_PORT"),
            redis_db=crawler.settings.getint("REDIS_DB"),
            redis_password=crawler.settings.get("REDIS_PASSWORD"),
        )
    
    @property
    def cookie_pool(self):
        if self._cookie_pool is None:
            from libs.cookie_pool import CookiePool
            self._cookie_pool = CookiePool(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
            )
        return self._cookie_pool
    
    @property
    def cookie_manager(self):
        """获取Cookie管理器（支持自动获取）"""
        if self._cookie_manager is None:
            from libs.cookie_manager import CookieManager
            self._cookie_manager = CookieManager(auto_refresh=True)
        return self._cookie_manager
    
    def process_request(self, request: Request, spider) -> None:
        # 获取平台标识
        platform = request.meta.get("platform", getattr(spider, "platform", None))
        if not platform:
            return
        
        # 跳过不需要Cookie的请求
        if request.meta.get("no_cookie", False):
            return
        
        # 优先从Cookie池获取
        cookie = self.cookie_pool.get_cookie(platform)
        
        # 如果Cookie池没有，尝试自动获取
        if not cookie:
            cookie = self._auto_fetch_cookie(platform)
        
        if cookie:
            request.headers["Cookie"] = cookie
            request.meta["cookie_used"] = cookie
    
    def _auto_fetch_cookie(self, platform: str) -> Optional[str]:
        """自动获取Cookie"""
        import asyncio
        
        try:
            # 检查是否支持自动获取
            if platform in self.cookie_manager.FETCHERS:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    cookie = loop.run_until_complete(
                        self.cookie_manager.get_cookie(platform)
                    )
                    if cookie:
                        logger.info(f"Auto-fetched cookie for {platform}")
                    return cookie
                finally:
                    loop.close()
        except Exception as e:
            logger.error(f"Failed to auto-fetch cookie for {platform}: {e}")
        
        return None
    
    def process_response(self, request: Request, response: Response, spider) -> Response:
        """检测Cookie失效并自动刷新"""
        platform = request.meta.get("platform")
        cookie = request.meta.get("cookie_used")
        
        # 检测失效特征
        is_invalid = False
        
        if response.status == 403:
            is_invalid = True
        elif response.status == 200:
            body_start = response.body[:2000].lower()
            # 常见失效特征
            invalid_patterns = [
                b"login", b"signin", b"passport",
                b"\xe7\x99\xbb\xe5\xbd\x95",  # "登录"
                b"\xe9\xaa\x8c\xe8\xaf\x81",  # "验证"
                b"captcha", b"verify",
            ]
            for pattern in invalid_patterns:
                if pattern in body_start:
                    is_invalid = True
                    break
        
        if is_invalid and cookie and platform:
            logger.warning(f"Cookie invalid for {platform}, attempting refresh...")
            
            # 标记失效
            self.cookie_pool.delete_cookie(platform, cookie)
            
            # 尝试自动刷新
            self._auto_refresh_cookie(platform)
        
        return response
    
    def _auto_refresh_cookie(self, platform: str) -> None:
        """自动刷新Cookie"""
        import asyncio
        
        try:
            if platform in self.cookie_manager.FETCHERS:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        self.cookie_manager.fetch_cookie(platform)
                    )
                    logger.info(f"Cookie refreshed for {platform}")
                finally:
                    loop.close()
        except Exception as e:
            logger.error(f"Failed to refresh cookie for {platform}: {e}")


class RetryMiddleware:
    """自定义重试中间件"""
    
    RETRY_EXCEPTIONS = (
        TimeoutError,
        ConnectionError,
        IOError,
    )
    
    def __init__(self, retry_times: int, retry_codes: list):
        self.retry_times = retry_times
        self.retry_codes = set(retry_codes)
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            retry_times=crawler.settings.getint("RETRY_TIMES", 3),
            retry_codes=crawler.settings.getlist("RETRY_HTTP_CODES"),
        )
    
    def process_response(self, request: Request, response: Response, spider) -> Response:
        if response.status in self.retry_codes:
            return self._retry(request, f"HTTP {response.status}", spider) or response
        return response
    
    def process_exception(self, request: Request, exception, spider):
        if isinstance(exception, self.RETRY_EXCEPTIONS):
            return self._retry(request, str(exception), spider)
    
    def _retry(self, request: Request, reason: str, spider) -> Optional[Request]:
        retry_count = request.meta.get("retry_count", 0)
        
        if retry_count < self.retry_times:
            retry_count += 1
            logger.info(f"Retrying {request.url} (attempt {retry_count}): {reason}")
            
            new_request = request.copy()
            new_request.meta["retry_count"] = retry_count
            new_request.dont_filter = True
            
            return new_request
        
        logger.error(f"Gave up retrying {request.url}: {reason}")
        return None


class SpiderOpenCloseMiddleware:
    """Spider开启/关闭信号处理"""
    
    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext
    
    def spider_opened(self, spider):
        logger.info(f"Spider opened: {spider.name}")
    
    def spider_closed(self, spider):
        logger.info(f"Spider closed: {spider.name}")
