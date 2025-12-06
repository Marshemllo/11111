"""
Cookie管理模块测试
"""
import pytest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from libs.cookie_manager import (
    CookieManager,
    CookieInfo,
    BaiduCookieFetcher,
    BingCookieFetcher,
    WeiboCookieFetcher,
    ZhihuCookieFetcher,
    get_cookie,
    fetch_baidu_cookie,
    fetch_bing_cookie,
)


class TestCookieInfo:
    """CookieInfo测试"""
    
    def test_create_cookie_info(self):
        """测试创建CookieInfo"""
        info = CookieInfo(
            platform="test",
            cookies={"key": "value"},
            cookie_string="key=value",
        )
        
        assert info.platform == "test"
        assert info.cookies == {"key": "value"}
        assert info.is_valid is True
        assert info.fail_count == 0
    
    def test_is_expired(self):
        """测试过期检测"""
        from datetime import datetime, timedelta
        
        # 未过期
        info1 = CookieInfo(
            platform="test",
            cookies={},
            cookie_string="",
            expires_at=datetime.now() + timedelta(hours=1),
        )
        assert info1.is_expired is False
        
        # 已过期
        info2 = CookieInfo(
            platform="test",
            cookies={},
            cookie_string="",
            expires_at=datetime.now() - timedelta(hours=1),
        )
        assert info2.is_expired is True
    
    def test_to_dict(self):
        """测试转字典"""
        info = CookieInfo(
            platform="test",
            cookies={"a": "1"},
            cookie_string="a=1",
        )
        
        d = info.to_dict()
        assert d["platform"] == "test"
        assert d["cookies"] == {"a": "1"}
        assert "created_at" in d


class TestBaiduCookieFetcher:
    """百度Cookie获取器测试"""
    
    @pytest.mark.asyncio
    async def test_fetch(self):
        """测试获取百度Cookie"""
        fetcher = BaiduCookieFetcher()
        cookie_info = await fetcher.fetch()
        
        assert cookie_info is not None
        assert cookie_info.platform == "baidu"
        assert len(cookie_info.cookies) > 0
        assert cookie_info.cookie_string != ""
    
    @pytest.mark.asyncio
    async def test_validate(self):
        """测试验证百度Cookie"""
        fetcher = BaiduCookieFetcher()
        cookie_info = await fetcher.fetch()
        
        if cookie_info:
            is_valid = await fetcher.validate(cookie_info)
            assert is_valid is True


class TestBingCookieFetcher:
    """Bing Cookie获取器测试"""
    
    @pytest.mark.asyncio
    async def test_fetch(self):
        """测试获取Bing Cookie"""
        fetcher = BingCookieFetcher()
        cookie_info = await fetcher.fetch()
        
        assert cookie_info is not None
        assert cookie_info.platform == "bing"
        assert len(cookie_info.cookies) > 0
    
    @pytest.mark.asyncio
    async def test_validate(self):
        """测试验证Bing Cookie"""
        fetcher = BingCookieFetcher()
        cookie_info = await fetcher.fetch()
        
        if cookie_info:
            is_valid = await fetcher.validate(cookie_info)
            assert is_valid is True


class TestCookieManager:
    """CookieManager测试"""
    
    @pytest.mark.asyncio
    async def test_get_cookie_baidu(self):
        """测试获取百度Cookie"""
        manager = CookieManager()
        cookie = await manager.get_cookie("baidu")
        
        assert cookie is not None
        assert len(cookie) > 0
    
    @pytest.mark.asyncio
    async def test_get_cookie_bing(self):
        """测试获取Bing Cookie"""
        manager = CookieManager()
        cookie = await manager.get_cookie("bing")
        
        assert cookie is not None
        assert len(cookie) > 0
    
    @pytest.mark.asyncio
    async def test_fetch_cookie(self):
        """测试获取新Cookie"""
        manager = CookieManager()
        cookie_info = await manager.fetch_cookie("baidu")
        
        assert cookie_info is not None
        assert cookie_info.platform == "baidu"
    
    @pytest.mark.asyncio
    async def test_validate_cookie(self):
        """测试验证Cookie"""
        manager = CookieManager()
        cookie = await manager.get_cookie("baidu")
        
        if cookie:
            is_valid = await manager.validate_cookie("baidu", cookie)
            assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_mark_invalid(self):
        """测试标记失效"""
        manager = CookieManager(auto_refresh=False)
        cookie = await manager.get_cookie("baidu")
        
        if cookie:
            await manager.mark_invalid("baidu", cookie)
            
            # 检查缓存中的状态
            if "baidu" in manager._cache:
                for info in manager._cache["baidu"]:
                    if info.cookie_string == cookie:
                        assert info.is_valid is False
                        break
    
    @pytest.mark.asyncio
    async def test_on_invalid_callback(self):
        """测试失效回调"""
        manager = CookieManager(auto_refresh=False)
        
        callback_called = False
        callback_platform = None
        
        async def on_invalid(platform, cookie):
            nonlocal callback_called, callback_platform
            callback_called = True
            callback_platform = platform
        
        manager.on_invalid(on_invalid)
        
        cookie = await manager.get_cookie("baidu")
        if cookie:
            await manager.mark_invalid("baidu", cookie)
            
            assert callback_called is True
            assert callback_platform == "baidu"
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """测试获取统计"""
        manager = CookieManager()
        await manager.get_cookie("baidu")
        
        stats = manager.get_stats()
        
        assert "baidu" in stats
        assert "total" in stats["baidu"]
        assert "valid" in stats["baidu"]
    
    @pytest.mark.asyncio
    async def test_refresh_all(self):
        """测试刷新所有"""
        manager = CookieManager()
        results = await manager.refresh_all()
        
        assert "baidu" in results
        assert "bing" in results


class TestConvenienceFunctions:
    """便捷函数测试"""
    
    @pytest.mark.asyncio
    async def test_get_cookie(self):
        """测试快速获取"""
        cookie = await get_cookie("baidu")
        assert cookie is not None
    
    @pytest.mark.asyncio
    async def test_fetch_baidu_cookie(self):
        """测试获取百度Cookie"""
        cookie = await fetch_baidu_cookie()
        assert cookie is not None
    
    @pytest.mark.asyncio
    async def test_fetch_bing_cookie(self):
        """测试获取Bing Cookie"""
        cookie = await fetch_bing_cookie()
        assert cookie is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
