"""
Scrapy Pipelines
- 数据清洗
- 情感分析
- 去重
- MongoDB存储
"""
import re
import logging
from datetime import datetime
from typing import Optional

import pymongo
from scrapy import Spider
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)


class CleanPipeline:
    """数据清洗Pipeline"""
    
    # HTML标签正则
    HTML_TAG_RE = re.compile(r"<[^>]+>")
    # 多余空白正则
    WHITESPACE_RE = re.compile(r"\s+")
    # 表情符号正则（可选保留）
    EMOJI_RE = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "]+",
        flags=re.UNICODE,
    )
    
    def process_item(self, item, spider: Spider):
        # 清洗正文内容
        if "content" in item and item["content"]:
            item["content"] = self.clean_text(item["content"])
        
        # 清洗标题
        if "title" in item and item["title"]:
            item["title"] = self.clean_text(item["title"])
        
        # 确保数值字段为整数
        int_fields = ["likes", "comments", "shares", "views", "reposts", "upvotes"]
        for field in int_fields:
            if field in item and item[field]:
                item[field] = self.parse_count(item[field])
        
        # 添加采集时间
        if "crawl_time" not in item or not item["crawl_time"]:
            item["crawl_time"] = datetime.utcnow().isoformat()
        
        return item
    
    def clean_text(self, text: str) -> str:
        """清洗文本"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = self.HTML_TAG_RE.sub("", text)
        # 规范化空白
        text = self.WHITESPACE_RE.sub(" ", text)
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def parse_count(self, value) -> int:
        """解析数量（支持 1.2万、10k 等格式）"""
        if isinstance(value, int):
            return value
        
        if not value:
            return 0
        
        value = str(value).strip().lower()
        
        try:
            if "万" in value or "w" in value:
                num = float(re.sub(r"[万w]", "", value))
                return int(num * 10000)
            elif "亿" in value:
                num = float(value.replace("亿", ""))
                return int(num * 100000000)
            elif "k" in value:
                num = float(value.replace("k", ""))
                return int(num * 1000)
            else:
                return int(float(re.sub(r"[^\d.]", "", value)))
        except (ValueError, TypeError):
            return 0


class SentimentPipeline:
    """情感分析Pipeline"""
    
    def __init__(self, enabled: bool = True, model: str = "snownlp"):
        self.enabled = enabled
        self.model = model
        self._analyzer = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            enabled=crawler.settings.getbool("SENTIMENT_ENABLED", True),
            model=crawler.settings.get("SENTIMENT_MODEL", "snownlp"),
        )
    
    @property
    def analyzer(self):
        if self._analyzer is None:
            from libs.sentiment import SentimentAnalyzer
            self._analyzer = SentimentAnalyzer(model=self.model)
        return self._analyzer
    
    def process_item(self, item, spider: Spider):
        if not self.enabled:
            return item
        
        # 获取待分析文本
        text = item.get("content") or item.get("title") or ""
        
        if text:
            result = self.analyzer.analyze(text)
            item["sentiment"] = result["label"]
            item["sentiment_score"] = result["score"]
        
        return item


class DuplicatesPipeline:
    """去重Pipeline"""
    
    def __init__(self):
        self.seen_ids = set()
    
    def process_item(self, item, spider: Spider):
        # 构建唯一标识
        platform = item.get("platform", "unknown")
        content_id = item.get("content_id")
        
        if not content_id:
            return item
        
        unique_id = f"{platform}:{content_id}"
        
        if unique_id in self.seen_ids:
            raise DropItem(f"Duplicate item: {unique_id}")
        
        self.seen_ids.add(unique_id)
        return item


class MongoPipeline:
    """MongoDB存储Pipeline"""
    
    def __init__(self, mongo_uri: str, mongo_db: str):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client: Optional[pymongo.MongoClient] = None
        self.db = None
        self.enabled = True
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE"),
        )
    
    def open_spider(self, spider: Spider):
        # 检查MongoDB配置是否有效
        if not self.mongo_uri or self.mongo_uri.strip() == "":
            logger.warning("MongoDB URI not configured, MongoPipeline disabled")
            self.enabled = False
            return
        
        try:
            self.client = pymongo.MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # 测试连接
            self.client.admin.command('ping')
            self.db = self.client[self.mongo_db]
            logger.info(f"Connected to MongoDB: {self.mongo_db}")
            
            # 创建索引
            self._ensure_indexes()
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}, MongoPipeline disabled")
            self.enabled = False
    
    def close_spider(self, spider: Spider):
        if self.client:
            self.client.close()
    
    def _ensure_indexes(self):
        """确保索引存在"""
        # 主内容集合索引
        self.db.contents.create_index([("platform", 1), ("content_id", 1)], unique=True)
        self.db.contents.create_index([("publish_time", -1)])
        self.db.contents.create_index([("sentiment", 1)])
        self.db.contents.create_index([("matched_keywords", 1)])
        
        # 评论集合索引
        self.db.comments.create_index([("platform", 1), ("comment_id", 1)], unique=True)
        self.db.comments.create_index([("content_id", 1)])
    
    def process_item(self, item, spider: Spider):
        # 如果未启用，直接返回
        if not self.enabled:
            return item
        
        # 转换为字典
        data = dict(item)
        
        # 确定集合名称
        content_type = data.get("content_type", "post")
        collection_name = "comments" if content_type == "comment" else "contents"
        
        # 构建查询条件
        platform = data.get("platform", "unknown")
        id_field = "comment_id" if content_type == "comment" else "content_id"
        content_id = data.get(id_field)
        
        if not content_id:
            logger.warning(f"Missing {id_field}, skipping item")
            return item
        
        # Upsert操作
        try:
            self.db[collection_name].update_one(
                {"platform": platform, id_field: content_id},
                {"$set": data},
                upsert=True,
            )
        except pymongo.errors.DuplicateKeyError:
            logger.debug(f"Duplicate key: {platform}:{content_id}")
        except Exception as e:
            logger.error(f"MongoDB error: {e}")
        
        return item


class RedisPipeline:
    """Redis Pipeline（用于实时推送）"""
    
    def __init__(self, redis_host: str, redis_port: int, redis_db: int, redis_password: str):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_password = redis_password
        self.redis_client = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            redis_host=crawler.settings.get("REDIS_HOST"),
            redis_port=crawler.settings.getint("REDIS_PORT"),
            redis_db=crawler.settings.getint("REDIS_DB"),
            redis_password=crawler.settings.get("REDIS_PASSWORD"),
        )
    
    def open_spider(self, spider):
        import redis
        self.redis_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            password=self.redis_password,
            decode_responses=True,
        )
    
    def close_spider(self, spider):
        if self.redis_client:
            self.redis_client.close()
    
    def process_item(self, item, spider):
        import json
        
        # 推送到实时队列
        data = dict(item)
        channel = f"crawler:realtime:{data.get('platform', 'unknown')}"
        
        self.redis_client.lpush(channel, json.dumps(data, ensure_ascii=False, default=str))
        self.redis_client.ltrim(channel, 0, 9999)  # 保留最近10000条
        
        return item
