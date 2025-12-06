"""
Cookie池管理
支持：
- Redis存储
- 多平台Cookie管理
- Cookie有效性检测
"""
import json
import logging
import random
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

import redis

logger = logging.getLogger(__name__)


@dataclass
class CookieAccount:
    """Cookie账号"""
    username: str
    cookie: str
    platform: str
    status: str = "active"  # active/expired/banned
    last_used: Optional[str] = None
    fail_count: int = 0


class CookiePool:
    """Cookie池"""
    
    # Redis key模板
    KEY_TEMPLATE = "crawler:cookies:{platform}"
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
    ):
        """
        初始化Cookie池
        
        Args:
            host: Redis主机
            port: Redis端口
            db: Redis数据库
            password: Redis密码
        """
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
        )
    
    def _get_key(self, platform: str) -> str:
        """获取Redis key"""
        return self.KEY_TEMPLATE.format(platform=platform)
    
    def add_cookie(self, platform: str, username: str, cookie: str) -> bool:
        """添加Cookie"""
        key = self._get_key(platform)
        
        account = CookieAccount(
            username=username,
            cookie=cookie,
            platform=platform,
        )
        
        try:
            # 使用Hash存储，username作为field
            self.redis_client.hset(key, username, json.dumps(asdict(account)))
            logger.info(f"Added cookie for {platform}:{username}")
            return True
        except redis.RedisError as e:
            logger.error(f"Failed to add cookie: {e}")
            return False
    
    def get_cookie(self, platform: str) -> Optional[str]:
        """随机获取一个可用Cookie"""
        key = self._get_key(platform)
        
        try:
            # 获取所有Cookie
            all_cookies = self.redis_client.hgetall(key)
            
            if not all_cookies:
                return None
            
            # 过滤可用的Cookie
            available = []
            for username, data in all_cookies.items():
                try:
                    account = json.loads(data)
                    if account.get("status") == "active":
                        available.append(account)
                except json.JSONDecodeError:
                    continue
            
            if not available:
                return None
            
            # 随机选择
            selected = random.choice(available)
            return selected.get("cookie")
        
        except redis.RedisError as e:
            logger.error(f"Failed to get cookie: {e}")
            return None
    
    def delete_cookie(self, platform: str, cookie: str) -> bool:
        """删除或标记Cookie为失效"""
        key = self._get_key(platform)
        
        try:
            # 查找对应的username
            all_cookies = self.redis_client.hgetall(key)
            
            for username, data in all_cookies.items():
                try:
                    account = json.loads(data)
                    if account.get("cookie") == cookie:
                        # 标记为过期
                        account["status"] = "expired"
                        account["fail_count"] = account.get("fail_count", 0) + 1
                        self.redis_client.hset(key, username, json.dumps(account))
                        logger.info(f"Marked cookie as expired: {platform}:{username}")
                        return True
                except json.JSONDecodeError:
                    continue
            
            return False
        
        except redis.RedisError as e:
            logger.error(f"Failed to delete cookie: {e}")
            return False
    
    def update_status(self, platform: str, username: str, status: str) -> bool:
        """更新Cookie状态"""
        key = self._get_key(platform)
        
        try:
            data = self.redis_client.hget(key, username)
            if not data:
                return False
            
            account = json.loads(data)
            account["status"] = status
            
            if status == "expired":
                account["fail_count"] = account.get("fail_count", 0) + 1
            
            self.redis_client.hset(key, username, json.dumps(account))
            return True
        
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to update status: {e}")
            return False
    
    def get_all(self, platform: str) -> List[Dict]:
        """获取平台所有Cookie"""
        key = self._get_key(platform)
        
        try:
            all_cookies = self.redis_client.hgetall(key)
            
            result = []
            for username, data in all_cookies.items():
                try:
                    account = json.loads(data)
                    result.append(account)
                except json.JSONDecodeError:
                    continue
            
            return result
        
        except redis.RedisError as e:
            logger.error(f"Failed to get all cookies: {e}")
            return []
    
    def count(self, platform: str, status: str = None) -> int:
        """统计Cookie数量"""
        if status is None:
            key = self._get_key(platform)
            try:
                return self.redis_client.hlen(key)
            except redis.RedisError:
                return 0
        
        all_cookies = self.get_all(platform)
        return len([c for c in all_cookies if c.get("status") == status])
    
    def cleanup_expired(self, platform: str, max_fail_count: int = 3) -> int:
        """清理过期Cookie"""
        key = self._get_key(platform)
        removed = 0
        
        try:
            all_cookies = self.redis_client.hgetall(key)
            
            for username, data in all_cookies.items():
                try:
                    account = json.loads(data)
                    if account.get("fail_count", 0) >= max_fail_count:
                        self.redis_client.hdel(key, username)
                        removed += 1
                except json.JSONDecodeError:
                    self.redis_client.hdel(key, username)
                    removed += 1
            
            logger.info(f"Cleaned up {removed} expired cookies for {platform}")
            return removed
        
        except redis.RedisError as e:
            logger.error(f"Failed to cleanup: {e}")
            return 0
    
    @property
    def stats(self) -> Dict[str, Dict]:
        """获取所有平台统计"""
        platforms = ["weibo", "zhihu", "douyin", "toutiao"]
        
        result = {}
        for platform in platforms:
            result[platform] = {
                "total": self.count(platform),
                "active": self.count(platform, "active"),
                "expired": self.count(platform, "expired"),
            }
        
        return result


class WeiboCookieGenerator:
    """微博Cookie生成器（模拟登录）"""
    
    def __init__(self, cookie_pool: CookiePool):
        self.cookie_pool = cookie_pool
    
    def login(self, username: str, password: str) -> Optional[str]:
        """
        模拟登录获取Cookie
        
        注意：实际实现需要处理验证码、加密等
        这里只是示例框架
        """
        # TODO: 实现微博登录逻辑
        # 1. 获取登录参数（servertime, nonce, pubkey等）
        # 2. RSA加密密码
        # 3. 提交登录请求
        # 4. 处理验证码
        # 5. 获取Cookie
        
        logger.warning("WeiboCookieGenerator.login() is not implemented")
        return None
    
    def refresh_all(self) -> int:
        """刷新所有过期Cookie"""
        # TODO: 实现Cookie刷新逻辑
        return 0
