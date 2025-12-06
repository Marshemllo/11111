"""
基础Spider类
提供通用功能：关键词加载、配置读取、请求构建等
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import yaml
import scrapy
from scrapy.http import Request

logger = logging.getLogger(__name__)


class BaseSpider(scrapy.Spider):
    """基础Spider"""
    
    # 平台标识，子类必须覆盖
    platform: str = "base"
    
    # 自定义设置
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
    }
    
    def __init__(self, keywords: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 保存关键词参数，延迟加载
        self._keywords_arg = keywords
        self._keywords = None
        self._site_config = None
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """从crawler创建spider，确保settings可用"""
        spider = super().from_crawler(crawler, *args, **kwargs)
        
        # 现在settings可用，加载配置
        spider.keywords = spider._load_keywords(spider._keywords_arg)
        spider.site_config = spider._load_site_config()
        
        logger.info(f"Spider {spider.name} initialized with {len(spider.keywords)} keywords")
        return spider
    
    def _load_keywords(self, keywords_arg: Optional[str]) -> List[str]:
        """加载关键词列表"""
        # 优先使用命令行参数
        if keywords_arg:
            return [k.strip() for k in keywords_arg.split(",") if k.strip()]
        
        # 从配置文件加载
        base_dir = Path(__file__).resolve().parent.parent.parent
        keywords_file = base_dir / "cfg" / "keywords.txt"
        
        if hasattr(self, 'settings') and self.settings:
            keywords_file = Path(self.settings.get("KEYWORDS_FILE", str(keywords_file)))
        
        if keywords_file.exists():
            with open(keywords_file, "r", encoding="utf-8") as f:
                keywords = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            return keywords
        
        logger.warning(f"Keywords file not found: {keywords_file}")
        return []
    
    def _load_site_config(self) -> Dict[str, Any]:
        """加载站点配置"""
        base_dir = Path(__file__).resolve().parent.parent.parent
        config_file = base_dir / "cfg" / "sites.yml"
        
        if hasattr(self, 'settings') and self.settings:
            config_file = Path(self.settings.get("SITES_CONFIG_FILE", str(config_file)))
        
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get(self.platform, {})
        
        return {}
    
    def make_request(
        self,
        url: str,
        callback=None,
        meta: Dict = None,
        headers: Dict = None,
        **kwargs
    ) -> Request:
        """构建请求"""
        meta = meta or {}
        meta["platform"] = self.platform
        
        return Request(
            url=url,
            callback=callback or self.parse,
            meta=meta,
            headers=headers,
            **kwargs
        )
    
    def get_matched_keywords(self, text: str) -> List[str]:
        """获取匹配的关键词"""
        if not text:
            return []
        
        text_lower = text.lower()
        return [kw for kw in self.keywords if kw.lower() in text_lower]
    
    def parse_time(self, time_str: str) -> Optional[str]:
        """解析时间字符串为ISO格式"""
        if not time_str:
            return None
        
        # 常见时间格式
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M:%S",
            "%Y年%m月%d日 %H:%M",
            "%m-%d %H:%M",
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(time_str.strip(), fmt)
                # 补充年份
                if dt.year == 1900:
                    dt = dt.replace(year=datetime.now().year)
                return dt.isoformat()
            except ValueError:
                continue
        
        # 处理相对时间
        return self._parse_relative_time(time_str)
    
    def _parse_relative_time(self, time_str: str) -> Optional[str]:
        """解析相对时间（刚刚、5分钟前等）"""
        import re
        from datetime import timedelta
        
        now = datetime.now()
        time_str = time_str.strip()
        
        if "刚刚" in time_str or "刚才" in time_str:
            return now.isoformat()
        
        # X分钟前
        match = re.search(r"(\d+)\s*分钟前", time_str)
        if match:
            minutes = int(match.group(1))
            return (now - timedelta(minutes=minutes)).isoformat()
        
        # X小时前
        match = re.search(r"(\d+)\s*小时前", time_str)
        if match:
            hours = int(match.group(1))
            return (now - timedelta(hours=hours)).isoformat()
        
        # X天前
        match = re.search(r"(\d+)\s*天前", time_str)
        if match:
            days = int(match.group(1))
            return (now - timedelta(days=days)).isoformat()
        
        # 今天 HH:MM
        match = re.search(r"今天\s*(\d{1,2}):(\d{2})", time_str)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            return now.replace(hour=hour, minute=minute, second=0).isoformat()
        
        # 昨天 HH:MM
        match = re.search(r"昨天\s*(\d{1,2}):(\d{2})", time_str)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            yesterday = now - timedelta(days=1)
            return yesterday.replace(hour=hour, minute=minute, second=0).isoformat()
        
        return time_str
