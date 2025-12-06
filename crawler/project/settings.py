"""
Scrapy settings for crawler project
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

BOT_NAME = "crawler"
SPIDER_MODULES = ["project.spiders"]
NEWSPIDER_MODULE = "project.spiders"

# Crawl responsibly
ROBOTSTXT_OBEY = False

# 并发设置
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8

# 下载延迟
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True

# 禁用Cookies（使用自定义Cookie池）
COOKIES_ENABLED = False

# 禁用Telnet
TELNETCONSOLE_ENABLED = False

# 默认请求头
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}

# 中间件配置
DOWNLOADER_MIDDLEWARES = {
    "project.middlewares.RandomUserAgentMiddleware": 400,
    "project.middlewares.ProxyMiddleware": 410,
    "project.middlewares.CookieMiddleware": 420,
    "project.middlewares.RetryMiddleware": 500,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
}

# Pipeline配置
ITEM_PIPELINES = {
    "project.pipelines.CleanPipeline": 100,
    "project.pipelines.SentimentPipeline": 200,
    "project.pipelines.DuplicatesPipeline": 300,
    "project.pipelines.MongoPipeline": 400,
}

# 重试配置
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# 超时配置
DOWNLOAD_TIMEOUT = 30

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"

# ============ 自定义配置 ============

# MongoDB配置
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "crawler")

# Redis配置（用于去重和分布式）
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# 代理池配置
PROXY_POOL_URL = os.getenv("PROXY_POOL_URL", "http://localhost:5010/get")
PROXY_POOL_ENABLED = os.getenv("PROXY_POOL_ENABLED", "true").lower() == "true"

# Cookie池配置
COOKIE_POOL_REDIS_KEY = "crawler:cookies:{platform}"

# 情感分析配置
SENTIMENT_ENABLED = os.getenv("SENTIMENT_ENABLED", "true").lower() == "true"
SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "snownlp")  # snownlp/bert

# 关键词配置
KEYWORDS_FILE = BASE_DIR / "cfg" / "keywords.txt"
SITES_CONFIG_FILE = BASE_DIR / "cfg" / "sites.yml"

# 去重配置
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True

# 分布式爬虫配置（可选）
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"

# 自动限速
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 8.0

# 缓存配置（开发环境可开启）
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 3600
# HTTPCACHE_DIR = "httpcache"
