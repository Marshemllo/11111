"""
基础爬虫类
"""
import scrapy
from scrapy.http import Response
from typing import Optional, Dict, Any, List
import json


class BaseSpider(scrapy.Spider):
    """基础爬虫类"""
    
    name = "base_spider"
    
    def __init__(
        self,
        spider_rule_id: int = None,
        start_urls: List[str] = None,
        allowed_domains: List[str] = None,
        rules: Dict[str, Any] = None,
        industry_tag: str = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.spider_rule_id = spider_rule_id
        self.industry_tag = industry_tag
        self.rules = rules or {}
        
        if start_urls:
            self.start_urls = start_urls
        if allowed_domains:
            self.allowed_domains = allowed_domains
    
    def parse(self, response: Response):
        """默认解析方法"""
        raise NotImplementedError("Subclasses must implement parse method")
    
    def extract_by_rule(self, response: Response, rule_name: str) -> Optional[str]:
        """根据规则提取数据"""
        if rule_name not in self.rules:
            return None
        
        rule = self.rules[rule_name]
        selector_type = rule.get("type", "xpath")
        selector = rule.get("selector")
        
        if not selector:
            return None
        
        if selector_type == "xpath":
            result = response.xpath(selector).get()
        elif selector_type == "css":
            result = response.css(selector).get()
        else:
            result = None
        
        return result.strip() if result else None
    
    def extract_list_by_rule(self, response: Response, rule_name: str) -> List[str]:
        """根据规则提取列表数据"""
        if rule_name not in self.rules:
            return []
        
        rule = self.rules[rule_name]
        selector_type = rule.get("type", "xpath")
        selector = rule.get("selector")
        
        if not selector:
            return []
        
        if selector_type == "xpath":
            results = response.xpath(selector).getall()
        elif selector_type == "css":
            results = response.css(selector).getall()
        else:
            results = []
        
        return [r.strip() for r in results if r.strip()]


class NewsSpider(BaseSpider):
    """新闻爬虫"""
    
    name = "news_spider"
    
    def parse(self, response: Response):
        """解析新闻列表页"""
        # 提取新闻链接
        news_links = self.extract_list_by_rule(response, "news_links")
        
        for link in news_links:
            yield response.follow(link, callback=self.parse_news)
        
        # 提取下一页链接
        next_page = self.extract_by_rule(response, "next_page")
        if next_page:
            yield response.follow(next_page, callback=self.parse)
    
    def parse_news(self, response: Response):
        """解析新闻详情页"""
        from sentiment_spider.items import NewsItem
        
        item = NewsItem()
        item["url"] = response.url
        item["title"] = self.extract_by_rule(response, "title")
        item["content"] = self.extract_by_rule(response, "content")
        item["author"] = self.extract_by_rule(response, "author")
        item["publish_time"] = self.extract_by_rule(response, "publish_time")
        item["source"] = self.extract_by_rule(response, "source")
        item["spider_rule_id"] = self.spider_rule_id
        item["industry_tag"] = self.industry_tag
        
        yield item


class ArticleSpider(BaseSpider):
    """文章爬虫"""
    
    name = "article_spider"
    
    def parse(self, response: Response):
        """解析文章列表页"""
        article_links = self.extract_list_by_rule(response, "article_links")
        
        for link in article_links:
            yield response.follow(link, callback=self.parse_article)
        
        next_page = self.extract_by_rule(response, "next_page")
        if next_page:
            yield response.follow(next_page, callback=self.parse)
    
    def parse_article(self, response: Response):
        """解析文章详情页"""
        from sentiment_spider.items import ArticleItem
        
        item = ArticleItem()
        item["url"] = response.url
        item["title"] = self.extract_by_rule(response, "title")
        item["content"] = self.extract_by_rule(response, "content")
        item["author"] = self.extract_by_rule(response, "author")
        item["publish_time"] = self.extract_by_rule(response, "publish_time")
        item["spider_rule_id"] = self.spider_rule_id
        item["industry_tag"] = self.industry_tag
        
        yield item
