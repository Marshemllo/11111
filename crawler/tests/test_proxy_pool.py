"""
代理池模块测试
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from libs.proxy_pool import ProxyPool, Proxy


class TestProxy:
    """Proxy类测试"""
    
    def test_basic_proxy(self):
        """测试基本代理"""
        proxy = Proxy(host="127.0.0.1", port=8080)
        
        assert proxy.url == "http://127.0.0.1:8080"
        assert str(proxy) == "http://127.0.0.1:8080"
    
    def test_https_proxy(self):
        """测试HTTPS代理"""
        proxy = Proxy(host="127.0.0.1", port=8080, protocol="https")
        
        assert proxy.url == "https://127.0.0.1:8080"
    
    def test_auth_proxy(self):
        """测试带认证的代理"""
        proxy = Proxy(
            host="127.0.0.1",
            port=8080,
            username="user",
            password="pass"
        )
        
        assert proxy.url == "http://user:pass@127.0.0.1:8080"


class TestProxyPool:
    """ProxyPool类测试"""
    
    def test_static_proxies(self):
        """测试静态代理列表"""
        proxies = [
            "http://127.0.0.1:8080",
            "http://127.0.0.1:8081",
        ]
        
        pool = ProxyPool(static_proxies=proxies)
        
        proxy = pool.get_proxy()
        assert proxy in proxies
    
    def test_delete_proxy(self):
        """测试删除代理"""
        proxies = ["http://127.0.0.1:8080"]
        pool = ProxyPool(static_proxies=proxies)
        
        pool.delete_proxy("http://127.0.0.1:8080")
        
        # 删除后应该获取不到
        proxy = pool.get_proxy()
        assert proxy is None
    
    def test_clear_failed(self):
        """测试清除失效记录"""
        proxies = ["http://127.0.0.1:8080"]
        pool = ProxyPool(static_proxies=proxies)
        
        pool.delete_proxy("http://127.0.0.1:8080")
        pool.clear_failed()
        
        # 清除后应该能获取到
        proxy = pool.get_proxy()
        assert proxy == "http://127.0.0.1:8080"
    
    def test_stats(self):
        """测试统计信息"""
        proxies = ["http://127.0.0.1:8080", "http://127.0.0.1:8081"]
        pool = ProxyPool(static_proxies=proxies)
        
        pool.delete_proxy("http://127.0.0.1:8080")
        
        stats = pool.stats
        assert stats["static"] == 2
        assert stats["failed"] == 1
    
    @patch("libs.proxy_pool.requests.get")
    def test_get_from_api(self, mock_get):
        """测试从API获取代理"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"proxy": "192.168.1.1:8080"}
        mock_response.headers = {"content-type": "application/json"}
        mock_get.return_value = mock_response
        
        pool = ProxyPool(api_url="http://localhost:5010/get")
        proxy = pool.get_proxy()
        
        assert proxy == "http://192.168.1.1:8080"
    
    @patch("libs.proxy_pool.requests.get")
    def test_api_failure(self, mock_get):
        """测试API失败"""
        mock_get.side_effect = Exception("Connection error")
        
        pool = ProxyPool(api_url="http://localhost:5010/get")
        proxy = pool.get_proxy()
        
        assert proxy is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
