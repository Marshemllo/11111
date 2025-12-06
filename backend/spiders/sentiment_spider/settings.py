"""
Scrapy 配置文件
"""

# Scrapy settings for sentiment_spider project

BOT_NAME = "sentiment_spider"

SPIDER_MODULES = ["sentiment_spider.crawlers"]
NEWSPIDER_MODULE = "sentiment_spider.crawlers"

# Crawl responsibly by identifying yourself
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Configure a delay for requests
DOWNLOAD_DELAY = 0.5

# Disable cookies
COOKIES_ENABLED = False

# Disable Telnet Console
TELNETCONSOLE_ENABLED = False

# Override the default request headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# Enable or disable spider middlewares
# SPIDER_MIDDLEWARES = {
#    "sentiment_spider.middlewares.SentimentSpiderSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# DOWNLOADER_MIDDLEWARES = {
#    "sentiment_spider.middlewares.SentimentSpiderDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
ITEM_PIPELINES = {
    "sentiment_spider.pipelines.DatabasePipeline": 300,
}

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
