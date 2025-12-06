"""
Cookie管理模块
支持：
- 自动获取Cookie（百度、Bing等）
- Cookie有效性检测
- 失效自动刷新
- 多平台Cookie管理
"""
import asyncio
import json
import logging
import random
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from urllib.parse import urljoin

import httpx
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


@dataclass
class CookieInfo:
    """Cookie信息"""
    platform: str
    cookies: Dict[str, str]
    cookie_string: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_valid: bool = True
    fail_count: int = 0
    
    @property
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False
    
    def to_dict(self) -> Dict:
        return {
            "platform": self.platform,
            "cookies": self.cookies,
            "cookie_string": self.cookie_string,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_valid": self.is_valid,
            "fail_count": self.fail_count,
        }


class BaseCookieFetcher(ABC):
    """Cookie获取器基类"""
    
    platform: str = "base"
    
    def __init__(self):
        self.ua = UserAgent()
        self.timeout = 30
    
    @abstractmethod
    async def fetch(self) -> Optional[CookieInfo]:
        """获取Cookie"""
        pass
    
    @abstractmethod
    async def validate(self, cookie_info: CookieInfo) -> bool:
        """验证Cookie有效性"""
        pass
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
        }
    
    def _cookies_to_string(self, cookies: Dict[str, str]) -> str:
        """Cookie字典转字符串"""
        return "; ".join(f"{k}={v}" for k, v in cookies.items())
    
    def _string_to_cookies(self, cookie_str: str) -> Dict[str, str]:
        """Cookie字符串转字典"""
        cookies = {}
        for item in cookie_str.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                cookies[key.strip()] = value.strip()
        return cookies


class BaiduCookieFetcher(BaseCookieFetcher):
    """百度Cookie获取器"""
    
    platform = "baidu"
    
    # 百度入口URL
    ENTRY_URL = "https://www.baidu.com/"
    VALIDATE_URL = "https://www.baidu.com/s?wd=test"
    
    async def fetch(self) -> Optional[CookieInfo]:
        """获取百度Cookie"""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                # 访问首页获取初始Cookie
                response = await client.get(
                    self.ENTRY_URL,
                    headers=self._get_headers(),
                )
                
                if response.status_code != 200:
                    logger.warning(f"Baidu entry failed: {response.status_code}")
                    return None
                
                # 提取Cookie
                cookies = dict(response.cookies)
                
                # 可能需要额外请求获取更多Cookie
                if "BAIDUID" not in cookies:
                    # 尝试搜索页
                    search_resp = await client.get(
                        self.VALIDATE_URL,
                        headers=self._get_headers(),
                    )
                    cookies.update(dict(search_resp.cookies))
                
                if not cookies:
                    logger.warning("No cookies obtained from Baidu")
                    return None
                
                cookie_string = self._cookies_to_string(cookies)
                
                return CookieInfo(
                    platform=self.platform,
                    cookies=cookies,
                    cookie_string=cookie_string,
                    expires_at=datetime.now() + timedelta(hours=24),
                )
        
        except Exception as e:
            logger.error(f"Failed to fetch Baidu cookie: {e}")
            return None
    
    async def validate(self, cookie_info: CookieInfo) -> bool:
        """验证百度Cookie"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = self._get_headers()
                headers["Cookie"] = cookie_info.cookie_string
                
                response = await client.get(
                    self.VALIDATE_URL,
                    headers=headers,
                )
                
                # 检查是否正常返回搜索结果
                if response.status_code == 200:
                    # 检查是否有验证码或异常
                    content = response.text
                    if "百度安全验证" in content or "验证码" in content:
                        return False
                    return True
                
                return False
        
        except Exception as e:
            logger.error(f"Baidu cookie validation failed: {e}")
            return False


class BingCookieFetcher(BaseCookieFetcher):
    """Bing Cookie获取器"""
    
    platform = "bing"
    
    ENTRY_URL = "https://www.bing.com/"
    VALIDATE_URL = "https://www.bing.com/search?q=test"
    
    async def fetch(self) -> Optional[CookieInfo]:
        """获取Bing Cookie"""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                # 访问首页
                response = await client.get(
                    self.ENTRY_URL,
                    headers=self._get_headers(),
                )
                
                if response.status_code != 200:
                    logger.warning(f"Bing entry failed: {response.status_code}")
                    return None
                
                cookies = dict(response.cookies)
                
                # 访问搜索页获取更多Cookie
                search_resp = await client.get(
                    self.VALIDATE_URL,
                    headers=self._get_headers(),
                )
                cookies.update(dict(search_resp.cookies))
                
                if not cookies:
                    logger.warning("No cookies obtained from Bing")
                    return None
                
                cookie_string = self._cookies_to_string(cookies)
                
                return CookieInfo(
                    platform=self.platform,
                    cookies=cookies,
                    cookie_string=cookie_string,
                    expires_at=datetime.now() + timedelta(hours=24),
                )
        
        except Exception as e:
            logger.error(f"Failed to fetch Bing cookie: {e}")
            return None
    
    async def validate(self, cookie_info: CookieInfo) -> bool:
        """验证Bing Cookie"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = self._get_headers()
                headers["Cookie"] = cookie_info.cookie_string
                
                response = await client.get(
                    self.VALIDATE_URL,
                    headers=headers,
                )
                
                if response.status_code == 200:
                    content = response.text
                    # 检查是否有验证码
                    if "captcha" in content.lower():
                        return False
                    return True
                
                return False
        
        except Exception as e:
            logger.error(f"Bing cookie validation failed: {e}")
            return False


class WeiboCookieFetcher(BaseCookieFetcher):
    """微博Cookie获取器（访客模式）"""
    
    platform = "weibo"
    
    VISITOR_URL = "https://passport.weibo.com/visitor/genvisitor"
    INCARNATE_URL = "https://passport.weibo.com/visitor/visitor"
    VALIDATE_URL = "https://m.weibo.cn/api/container/getIndex?containerid=102803"
    
    async def fetch(self) -> Optional[CookieInfo]:
        """获取微博访客Cookie"""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                # Step 1: 获取访客参数
                headers = self._get_headers()
                
                gen_data = {
                    "cb": "gen_callback",
                    "fp": self._generate_fp(),
                }
                
                response = await client.post(
                    self.VISITOR_URL,
                    data=gen_data,
                    headers=headers,
                )
                
                if response.status_code != 200:
                    logger.warning(f"Weibo genvisitor failed: {response.status_code}")
                    return None
                
                # 解析返回的JSONP
                text = response.text
                match = re.search(r'gen_callback\((.*?)\)', text)
                if not match:
                    logger.warning("Failed to parse genvisitor response")
                    return None
                
                data = json.loads(match.group(1))
                if data.get("retcode") != 20000000:
                    logger.warning(f"Weibo genvisitor error: {data}")
                    return None
                
                tid = data.get("data", {}).get("tid")
                if not tid:
                    logger.warning("No tid in genvisitor response")
                    return None
                
                # Step 2: 获取Cookie
                incarnate_params = {
                    "a": "incarnate",
                    "t": tid,
                    "w": 2,
                    "c": "095",
                    "gc": "",
                    "cb": "cross_domain_callback",
                    "from": "weibo",
                }
                
                response2 = await client.get(
                    self.INCARNATE_URL,
                    params=incarnate_params,
                    headers=headers,
                )
                
                cookies = dict(response2.cookies)
                
                # 访问移动端API获取更多Cookie
                m_resp = await client.get(
                    "https://m.weibo.cn/",
                    headers=headers,
                )
                cookies.update(dict(m_resp.cookies))
                
                if not cookies:
                    logger.warning("No cookies obtained from Weibo")
                    return None
                
                cookie_string = self._cookies_to_string(cookies)
                
                return CookieInfo(
                    platform=self.platform,
                    cookies=cookies,
                    cookie_string=cookie_string,
                    expires_at=datetime.now() + timedelta(hours=2),  # 访客Cookie有效期较短
                )
        
        except Exception as e:
            logger.error(f"Failed to fetch Weibo cookie: {e}")
            return None
    
    def _generate_fp(self) -> str:
        """生成指纹参数"""
        import hashlib
        import json
        
        fp_data = {
            "os": "1",
            "browser": "Chrome119,0,0,0",
            "fonts": "undefined",
            "screenInfo": "1920*1080*24",
            "plugins": "",
        }
        
        fp_str = json.dumps(fp_data, separators=(",", ":"))
        return hashlib.md5(fp_str.encode()).hexdigest()
    
    async def validate(self, cookie_info: CookieInfo) -> bool:
        """验证微博Cookie"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = self._get_headers()
                headers["Cookie"] = cookie_info.cookie_string
                
                response = await client.get(
                    self.VALIDATE_URL,
                    headers=headers,
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        return data.get("ok") == 1
                    except json.JSONDecodeError:
                        return False
                
                return False
        
        except Exception as e:
            logger.error(f"Weibo cookie validation failed: {e}")
            return False


class ZhihuCookieFetcher(BaseCookieFetcher):
    """知乎Cookie获取器"""
    
    platform = "zhihu"
    
    ENTRY_URL = "https://www.zhihu.com/"
    VALIDATE_URL = "https://www.zhihu.com/api/v4/search_v3?t=general&q=test"
    
    async def fetch(self) -> Optional[CookieInfo]:
        """获取知乎Cookie"""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                headers = self._get_headers()
                
                # 访问首页
                response = await client.get(
                    self.ENTRY_URL,
                    headers=headers,
                )
                
                cookies = dict(response.cookies)
                
                # 生成d_c0（知乎设备ID）
                if "d_c0" not in cookies:
                    # 尝试通过API获取
                    api_resp = await client.get(
                        "https://www.zhihu.com/api/v4/me",
                        headers=headers,
                    )
                    cookies.update(dict(api_resp.cookies))
                
                if not cookies:
                    logger.warning("No cookies obtained from Zhihu")
                    return None
                
                cookie_string = self._cookies_to_string(cookies)
                
                return CookieInfo(
                    platform=self.platform,
                    cookies=cookies,
                    cookie_string=cookie_string,
                    expires_at=datetime.now() + timedelta(hours=12),
                )
        
        except Exception as e:
            logger.error(f"Failed to fetch Zhihu cookie: {e}")
            return None
    
    async def validate(self, cookie_info: CookieInfo) -> bool:
        """验证知乎Cookie"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = self._get_headers()
                headers["Cookie"] = cookie_info.cookie_string
                
                response = await client.get(
                    self.VALIDATE_URL,
                    headers=headers,
                )
                
                return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Zhihu cookie validation failed: {e}")
            return False


class CookieManager:
    """Cookie管理器"""
    
    # 注册的Cookie获取器
    FETCHERS: Dict[str, type] = {
        "baidu": BaiduCookieFetcher,
        "bing": BingCookieFetcher,
        "weibo": WeiboCookieFetcher,
        "zhihu": ZhihuCookieFetcher,
    }
    
    def __init__(
        self,
        redis_client=None,
        auto_refresh: bool = True,
        refresh_interval: int = 3600,
    ):
        """
        初始化Cookie管理器
        
        Args:
            redis_client: Redis客户端（可选，用于持久化）
            auto_refresh: 是否自动刷新
            refresh_interval: 刷新间隔（秒）
        """
        self.redis_client = redis_client
        self.auto_refresh = auto_refresh
        self.refresh_interval = refresh_interval
        
        # 内存缓存
        self._cache: Dict[str, List[CookieInfo]] = {}
        
        # 获取器实例
        self._fetchers: Dict[str, BaseCookieFetcher] = {}
        
        # 失效回调
        self._on_invalid_callbacks: List[Callable] = []
    
    def register_fetcher(self, platform: str, fetcher_class: type) -> None:
        """注册自定义Cookie获取器"""
        self.FETCHERS[platform] = fetcher_class
    
    def _get_fetcher(self, platform: str) -> Optional[BaseCookieFetcher]:
        """获取平台对应的获取器"""
        if platform not in self._fetchers:
            fetcher_class = self.FETCHERS.get(platform)
            if fetcher_class:
                self._fetchers[platform] = fetcher_class()
        
        return self._fetchers.get(platform)
    
    async def get_cookie(self, platform: str, force_refresh: bool = False) -> Optional[str]:
        """
        获取Cookie
        
        Args:
            platform: 平台名称
            force_refresh: 是否强制刷新
        
        Returns:
            Cookie字符串
        """
        # 检查缓存
        if not force_refresh and platform in self._cache:
            valid_cookies = [c for c in self._cache[platform] if c.is_valid and not c.is_expired]
            if valid_cookies:
                # 随机选择一个
                cookie_info = random.choice(valid_cookies)
                return cookie_info.cookie_string
        
        # 从Redis获取
        if self.redis_client and not force_refresh:
            cookie_info = await self._get_from_redis(platform)
            if cookie_info and cookie_info.is_valid:
                return cookie_info.cookie_string
        
        # 自动获取新Cookie
        cookie_info = await self.fetch_cookie(platform)
        if cookie_info:
            return cookie_info.cookie_string
        
        return None
    
    async def fetch_cookie(self, platform: str) -> Optional[CookieInfo]:
        """获取新Cookie"""
        fetcher = self._get_fetcher(platform)
        if not fetcher:
            logger.warning(f"No fetcher registered for platform: {platform}")
            return None
        
        cookie_info = await fetcher.fetch()
        
        if cookie_info:
            # 缓存
            if platform not in self._cache:
                self._cache[platform] = []
            self._cache[platform].append(cookie_info)
            
            # 持久化到Redis
            if self.redis_client:
                await self._save_to_redis(cookie_info)
            
            logger.info(f"Fetched new cookie for {platform}")
        
        return cookie_info
    
    async def validate_cookie(self, platform: str, cookie_string: str) -> bool:
        """验证Cookie有效性"""
        fetcher = self._get_fetcher(platform)
        if not fetcher:
            return False
        
        cookie_info = CookieInfo(
            platform=platform,
            cookies=fetcher._string_to_cookies(cookie_string),
            cookie_string=cookie_string,
        )
        
        return await fetcher.validate(cookie_info)
    
    async def mark_invalid(self, platform: str, cookie_string: str) -> None:
        """标记Cookie为失效"""
        # 更新缓存
        if platform in self._cache:
            for cookie_info in self._cache[platform]:
                if cookie_info.cookie_string == cookie_string:
                    cookie_info.is_valid = False
                    cookie_info.fail_count += 1
                    break
        
        # 更新Redis
        if self.redis_client:
            await self._mark_invalid_in_redis(platform, cookie_string)
        
        # 触发回调
        for callback in self._on_invalid_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(platform, cookie_string)
                else:
                    callback(platform, cookie_string)
            except Exception as e:
                logger.error(f"Callback error: {e}")
        
        # 自动刷新
        if self.auto_refresh:
            logger.info(f"Auto-refreshing cookie for {platform}")
            await self.fetch_cookie(platform)
    
    def on_invalid(self, callback: Callable) -> None:
        """注册失效回调"""
        self._on_invalid_callbacks.append(callback)
    
    async def refresh_all(self) -> Dict[str, bool]:
        """刷新所有平台Cookie"""
        results = {}
        
        for platform in self.FETCHERS.keys():
            try:
                cookie_info = await self.fetch_cookie(platform)
                results[platform] = cookie_info is not None
            except Exception as e:
                logger.error(f"Failed to refresh {platform}: {e}")
                results[platform] = False
        
        return results
    
    async def _get_from_redis(self, platform: str) -> Optional[CookieInfo]:
        """从Redis获取Cookie"""
        if not self.redis_client:
            return None
        
        try:
            key = f"cookie_manager:{platform}"
            data = self.redis_client.get(key)
            
            if data:
                info = json.loads(data)
                return CookieInfo(
                    platform=info["platform"],
                    cookies=info["cookies"],
                    cookie_string=info["cookie_string"],
                    created_at=datetime.fromisoformat(info["created_at"]),
                    expires_at=datetime.fromisoformat(info["expires_at"]) if info.get("expires_at") else None,
                    is_valid=info.get("is_valid", True),
                    fail_count=info.get("fail_count", 0),
                )
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        
        return None
    
    async def _save_to_redis(self, cookie_info: CookieInfo) -> None:
        """保存Cookie到Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"cookie_manager:{cookie_info.platform}"
            data = json.dumps(cookie_info.to_dict())
            
            # 设置过期时间
            ttl = self.refresh_interval * 2
            if cookie_info.expires_at:
                ttl = int((cookie_info.expires_at - datetime.now()).total_seconds())
            
            self.redis_client.setex(key, ttl, data)
        except Exception as e:
            logger.error(f"Redis save error: {e}")
    
    async def _mark_invalid_in_redis(self, platform: str, cookie_string: str) -> None:
        """在Redis中标记Cookie失效"""
        if not self.redis_client:
            return
        
        try:
            key = f"cookie_manager:{platform}"
            data = self.redis_client.get(key)
            
            if data:
                info = json.loads(data)
                if info.get("cookie_string") == cookie_string:
                    info["is_valid"] = False
                    info["fail_count"] = info.get("fail_count", 0) + 1
                    self.redis_client.set(key, json.dumps(info))
        except Exception as e:
            logger.error(f"Redis mark invalid error: {e}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = {}
        
        for platform, cookies in self._cache.items():
            valid = [c for c in cookies if c.is_valid and not c.is_expired]
            invalid = [c for c in cookies if not c.is_valid]
            expired = [c for c in cookies if c.is_expired]
            
            stats[platform] = {
                "total": len(cookies),
                "valid": len(valid),
                "invalid": len(invalid),
                "expired": len(expired),
            }
        
        return stats


# 便捷函数
async def get_cookie(platform: str) -> Optional[str]:
    """快速获取Cookie"""
    manager = CookieManager()
    return await manager.get_cookie(platform)


async def fetch_baidu_cookie() -> Optional[str]:
    """获取百度Cookie"""
    fetcher = BaiduCookieFetcher()
    cookie_info = await fetcher.fetch()
    return cookie_info.cookie_string if cookie_info else None


async def fetch_bing_cookie() -> Optional[str]:
    """获取Bing Cookie"""
    fetcher = BingCookieFetcher()
    cookie_info = await fetcher.fetch()
    return cookie_info.cookie_string if cookie_info else None


# 同步包装器
def get_cookie_sync(platform: str) -> Optional[str]:
    """同步获取Cookie"""
    return asyncio.run(get_cookie(platform))
