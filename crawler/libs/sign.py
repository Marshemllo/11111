"""
签名生成器
支持：
- 微博签名
- 抖音签名
- 通用签名工具
"""
import hashlib
import hmac
import time
import random
import string
import base64
import json
import logging
from typing import Dict, Optional
from urllib.parse import urlencode, quote

logger = logging.getLogger(__name__)


class SignGenerator:
    """通用签名生成器"""
    
    @staticmethod
    def md5(text: str) -> str:
        """MD5签名"""
        return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def sha1(text: str) -> str:
        """SHA1签名"""
        return hashlib.sha1(text.encode()).hexdigest()
    
    @staticmethod
    def sha256(text: str) -> str:
        """SHA256签名"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def hmac_sha256(key: str, message: str) -> str:
        """HMAC-SHA256签名"""
        return hmac.new(
            key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def base64_encode(text: str) -> str:
        """Base64编码"""
        return base64.b64encode(text.encode()).decode()
    
    @staticmethod
    def base64_decode(text: str) -> str:
        """Base64解码"""
        return base64.b64decode(text.encode()).decode()
    
    @staticmethod
    def random_string(length: int = 16) -> str:
        """生成随机字符串"""
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def timestamp() -> int:
        """获取当前时间戳（秒）"""
        return int(time.time())
    
    @staticmethod
    def timestamp_ms() -> int:
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)


class WeiboSign:
    """微博签名生成器"""
    
    # 微博API密钥（公开的）
    APP_KEY = "1076766242"
    
    @classmethod
    def generate_visitor_id(cls) -> str:
        """生成访客ID"""
        # 格式：时间戳 + 随机数
        ts = SignGenerator.timestamp_ms()
        rand = random.randint(100000, 999999)
        return f"{ts}{rand}"
    
    @classmethod
    def generate_s_v2(cls, params: Dict) -> str:
        """
        生成微博s参数（v2版本）
        用于移动端API请求
        """
        # 排序参数
        sorted_params = sorted(params.items())
        param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        
        # 添加密钥
        sign_str = f"{param_str}&{cls.APP_KEY}"
        
        return SignGenerator.md5(sign_str)
    
    @classmethod
    def generate_ajax_sign(cls, url: str, data: Dict = None) -> Dict:
        """
        生成AJAX请求签名
        返回需要添加的请求参数
        """
        timestamp = SignGenerator.timestamp()
        
        return {
            "_t": timestamp,
            "_s": SignGenerator.random_string(8),
        }


class DouyinSign:
    """
    抖音签名生成器
    
    注意：抖音的签名算法较为复杂，通常需要：
    1. 使用JS引擎执行混淆的JS代码
    2. 或者使用逆向得到的算法
    
    这里提供基础框架，实际使用需要补充具体实现
    """
    
    # 设备信息
    DEFAULT_DEVICE = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "pc_client_type": 1,
        "version_code": "190500",
        "version_name": "19.5.0",
        "cookie_enabled": "true",
        "screen_width": 1920,
        "screen_height": 1080,
        "browser_language": "zh-CN",
        "browser_platform": "Win32",
        "browser_name": "Chrome",
        "browser_version": "119.0.0.0",
        "browser_online": "true",
        "engine_name": "Blink",
        "engine_version": "119.0.0.0",
        "os_name": "Windows",
        "os_version": "10",
        "cpu_core_num": 8,
        "device_memory": 8,
        "platform": "PC",
    }
    
    @classmethod
    def generate_device_id(cls) -> str:
        """生成设备ID"""
        # 19位数字
        return "".join(str(random.randint(0, 9)) for _ in range(19))
    
    @classmethod
    def generate_iid(cls) -> str:
        """生成install_id"""
        return "".join(str(random.randint(0, 9)) for _ in range(19))
    
    @classmethod
    def generate_mstoken(cls, length: int = 128) -> str:
        """生成msToken"""
        chars = string.ascii_letters + string.digits + "_-"
        return "".join(random.choice(chars) for _ in range(length))
    
    @classmethod
    def generate_ttwid(cls) -> str:
        """生成ttwid"""
        # 实际需要从抖音获取
        return SignGenerator.random_string(32)
    
    @classmethod
    def generate_x_bogus(cls, url: str, user_agent: str) -> Optional[str]:
        """
        生成X-Bogus签名
        
        注意：这是抖音的核心签名，需要逆向JS代码
        这里只是占位符，实际使用需要：
        1. 使用execjs执行混淆的JS
        2. 或使用已逆向的Python实现
        """
        logger.warning("DouyinSign.generate_x_bogus() requires JS execution")
        
        # TODO: 实现X-Bogus签名
        # 可以使用以下方式：
        # 1. execjs + 抖音的JS代码
        # 2. PyExecJS
        # 3. Node.js子进程
        
        return None
    
    @classmethod
    def generate_a_bogus(cls, url: str, data: str = "") -> Optional[str]:
        """
        生成a_bogus签名（新版）
        """
        logger.warning("DouyinSign.generate_a_bogus() requires JS execution")
        return None
    
    @classmethod
    def get_common_params(cls) -> Dict:
        """获取通用请求参数"""
        return {
            **cls.DEFAULT_DEVICE,
            "device_id": cls.generate_device_id(),
            "msToken": cls.generate_mstoken(),
        }


class ZhihuSign:
    """知乎签名生成器"""
    
    @classmethod
    def generate_x_zse_93(cls) -> str:
        """生成x-zse-93"""
        return "101_3_3.0"
    
    @classmethod
    def generate_x_zse_96(cls, path: str, dc0: str) -> str:
        """
        生成x-zse-96签名
        
        算法：
        1. 拼接 x-zse-93 + path + dc0
        2. MD5
        3. 加密（需要逆向）
        """
        x_zse_93 = cls.generate_x_zse_93()
        
        # 基础签名
        sign_str = f"{x_zse_93}+{path}+{dc0}"
        md5_hash = SignGenerator.md5(sign_str)
        
        # TODO: 需要进一步加密处理
        # 知乎使用了自定义的加密算法
        
        return f"2.0_{md5_hash}"
    
    @classmethod
    def generate_d_c0(cls) -> str:
        """生成d_c0 Cookie"""
        # 格式类似：AXXXXXXXXXXXXXXXXXX
        chars = string.ascii_uppercase + string.digits
        return "A" + "".join(random.choice(chars) for _ in range(24))


# 便捷函数
def weibo_sign(params: Dict) -> str:
    """微博签名"""
    return WeiboSign.generate_s_v2(params)


def douyin_common_params() -> Dict:
    """抖音通用参数"""
    return DouyinSign.get_common_params()


def zhihu_headers(path: str, dc0: str = None) -> Dict:
    """知乎请求头"""
    dc0 = dc0 or ZhihuSign.generate_d_c0()
    
    return {
        "x-zse-93": ZhihuSign.generate_x_zse_93(),
        "x-zse-96": ZhihuSign.generate_x_zse_96(path, dc0),
    }
