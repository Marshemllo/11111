"""
代理池管理
支持：
- 从代理池API获取代理
- 代理验证
- 失效代理删除
"""
import logging
import random
from typing import Optional, List
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)


@dataclass
class Proxy:
    """代理对象"""
    host: str
    port: int
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    
    @property
    def url(self) -> str:
        """获取代理URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    def __str__(self) -> str:
        return self.url


class ProxyPool:
    """代理池"""
    
    def __init__(
        self,
        api_url: str = None,
        static_proxies: List[str] = None,
        timeout: int = 5,
    ):
        """
        初始化代理池
        
        Args:
            api_url: 代理池API地址（如 proxy_pool 项目）
            static_proxies: 静态代理列表
            timeout: 请求超时时间
        """
        self.api_url = api_url
        self.static_proxies = static_proxies or []
        self.timeout = timeout
        
        # 缓存的代理列表
        self._cached_proxies: List[str] = []
        self._failed_proxies: set = set()
    
    def get_proxy(self) -> Optional[str]:
        """获取一个代理"""
        # 优先从API获取
        if self.api_url:
            proxy = self._get_from_api()
            if proxy:
                return proxy
        
        # 从静态列表获取
        if self.static_proxies:
            available = [p for p in self.static_proxies if p not in self._failed_proxies]
            if available:
                return random.choice(available)
        
        # 从缓存获取
        if self._cached_proxies:
            available = [p for p in self._cached_proxies if p not in self._failed_proxies]
            if available:
                return random.choice(available)
        
        return None
    
    def _get_from_api(self) -> Optional[str]:
        """从API获取代理"""
        try:
            # 支持 proxy_pool 项目的API格式
            response = requests.get(self.api_url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                
                if data:
                    # proxy_pool 格式: {"proxy": "ip:port"}
                    proxy = data.get("proxy")
                    if proxy:
                        if not proxy.startswith("http"):
                            proxy = f"http://{proxy}"
                        self._cached_proxies.append(proxy)
                        return proxy
                else:
                    # 纯文本格式
                    proxy = response.text.strip()
                    if proxy:
                        if not proxy.startswith("http"):
                            proxy = f"http://{proxy}"
                        self._cached_proxies.append(proxy)
                        return proxy
        
        except requests.RequestException as e:
            logger.warning(f"Failed to get proxy from API: {e}")
        
        return None
    
    def delete_proxy(self, proxy: str) -> None:
        """标记代理为失效"""
        self._failed_proxies.add(proxy)
        
        # 尝试通知代理池API
        if self.api_url:
            try:
                # proxy_pool 项目的删除接口
                delete_url = self.api_url.replace("/get", "/delete")
                # 提取 ip:port
                proxy_addr = proxy.replace("http://", "").replace("https://", "")
                requests.get(f"{delete_url}?proxy={proxy_addr}", timeout=2)
            except requests.RequestException:
                pass
        
        logger.debug(f"Proxy marked as failed: {proxy}")
    
    def get_all(self) -> List[str]:
        """获取所有可用代理"""
        proxies = []
        
        # 从API批量获取
        if self.api_url:
            try:
                all_url = self.api_url.replace("/get", "/all")
                response = requests.get(all_url, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data:
                        proxy = item.get("proxy") if isinstance(item, dict) else str(item)
                        if proxy:
                            if not proxy.startswith("http"):
                                proxy = f"http://{proxy}"
                            proxies.append(proxy)
            except requests.RequestException:
                pass
        
        # 添加静态代理
        proxies.extend(self.static_proxies)
        
        # 过滤失效代理
        return [p for p in proxies if p not in self._failed_proxies]
    
    def verify_proxy(self, proxy: str, test_url: str = "https://httpbin.org/ip") -> bool:
        """验证代理是否可用"""
        try:
            response = requests.get(
                test_url,
                proxies={"http": proxy, "https": proxy},
                timeout=self.timeout,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def clear_failed(self) -> None:
        """清除失效代理记录"""
        self._failed_proxies.clear()
    
    @property
    def stats(self) -> dict:
        """获取代理池统计"""
        return {
            "cached": len(self._cached_proxies),
            "failed": len(self._failed_proxies),
            "static": len(self.static_proxies),
        }


class ProxyPoolManager:
    """代理池管理器（支持多个代理源）"""
    
    def __init__(self):
        self.pools: List[ProxyPool] = []
    
    def add_pool(self, pool: ProxyPool) -> None:
        """添加代理池"""
        self.pools.append(pool)
    
    def get_proxy(self) -> Optional[str]:
        """从所有池中获取代理"""
        for pool in self.pools:
            proxy = pool.get_proxy()
            if proxy:
                return proxy
        return None
    
    def delete_proxy(self, proxy: str) -> None:
        """在所有池中标记代理失效"""
        for pool in self.pools:
            pool.delete_proxy(proxy)
