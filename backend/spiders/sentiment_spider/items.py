"""
Scrapy Item 定义
"""
import scrapy


class BaseItem(scrapy.Item):
    """基础数据项"""
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    crawled_at = scrapy.Field()
    spider_rule_id = scrapy.Field()
    industry_tag = scrapy.Field()


class NewsItem(BaseItem):
    """新闻数据项"""
    author = scrapy.Field()
    publish_time = scrapy.Field()
    source = scrapy.Field()
    category = scrapy.Field()
    tags = scrapy.Field()


class ArticleItem(BaseItem):
    """文章数据项"""
    author = scrapy.Field()
    publish_time = scrapy.Field()
    views = scrapy.Field()
    likes = scrapy.Field()
    comments_count = scrapy.Field()


class ProductItem(scrapy.Item):
    """产品数据项"""
    url = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    original_price = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    brand = scrapy.Field()
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    images = scrapy.Field()
    crawled_at = scrapy.Field()
    spider_rule_id = scrapy.Field()
    industry_tag = scrapy.Field()
