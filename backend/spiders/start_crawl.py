"""
后端调用 Scrapy 的脚本
"""
import sys
import os
import json
from typing import Dict, Any, Optional
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_spider(
    spider_name: str,
    spider_rule_id: int,
    start_urls: list,
    allowed_domains: list = None,
    rules: Dict[str, Any] = None,
    industry_tag: str = None,
    settings_override: Dict[str, Any] = None
):
    """
    运行爬虫
    
    Args:
        spider_name: 爬虫名称
        spider_rule_id: 爬虫规则ID
        start_urls: 起始URL列表
        allowed_domains: 允许的域名列表
        rules: 爬取规则
        industry_tag: 行业标签
        settings_override: 覆盖的设置
    """
    # 切换到爬虫目录
    os.chdir(os.path.join(os.path.dirname(__file__), "sentiment_spider"))
    
    # 获取项目设置
    settings = get_project_settings()
    
    # 覆盖设置
    if settings_override:
        for key, value in settings_override.items():
            settings.set(key, value)
    
    # 创建爬虫进程
    process = CrawlerProcess(settings)
    
    # 根据爬虫名称选择爬虫类
    spider_class = get_spider_class(spider_name)
    
    # 启动爬虫
    process.crawl(
        spider_class,
        spider_rule_id=spider_rule_id,
        start_urls=start_urls,
        allowed_domains=allowed_domains,
        rules=rules,
        industry_tag=industry_tag
    )
    process.start()


def get_spider_class(spider_name: str):
    """根据名称获取爬虫类"""
    from sentiment_spider.crawlers.base_spider import NewsSpider, ArticleSpider, BaseSpider
    
    spider_map = {
        "news_spider": NewsSpider,
        "article_spider": ArticleSpider,
        "base_spider": BaseSpider,
    }
    
    return spider_map.get(spider_name, BaseSpider)


def start_spider_async(
    spider_name: str,
    spider_rule_id: int,
    start_urls: list,
    allowed_domains: list = None,
    rules: Dict[str, Any] = None,
    industry_tag: str = None
) -> Process:
    """
    异步启动爬虫（在单独进程中运行）
    
    Returns:
        Process: 爬虫进程对象
    """
    process = Process(
        target=run_spider,
        args=(spider_name, spider_rule_id, start_urls, allowed_domains, rules, industry_tag)
    )
    process.start()
    return process


def test_spider(
    url: str,
    rules: Dict[str, Any] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    测试爬虫效果
    
    Args:
        url: 测试URL
        rules: 爬取规则
        timeout: 超时时间（秒）
    
    Returns:
        测试结果
    """
    import requests
    from lxml import html
    import time
    
    start_time = time.time()
    result = {
        "success": False,
        "data": [],
        "error": None,
        "elapsed_time": 0
    }
    
    try:
        # 发送请求
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # 解析HTML
        tree = html.fromstring(response.content)
        
        # 应用规则提取数据
        extracted_data = {}
        if rules:
            for field_name, rule in rules.items():
                selector_type = rule.get("type", "xpath")
                selector = rule.get("selector")
                
                if selector:
                    if selector_type == "xpath":
                        values = tree.xpath(selector)
                    elif selector_type == "css":
                        from lxml.cssselect import CSSSelector
                        sel = CSSSelector(selector)
                        values = sel(tree)
                    else:
                        values = []
                    
                    # 提取文本
                    if values:
                        if hasattr(values[0], "text_content"):
                            extracted_data[field_name] = values[0].text_content().strip()
                        else:
                            extracted_data[field_name] = str(values[0]).strip()
        
        result["success"] = True
        result["data"] = [extracted_data] if extracted_data else []
    
    except requests.RequestException as e:
        result["error"] = f"请求错误: {str(e)}"
    except Exception as e:
        result["error"] = f"解析错误: {str(e)}"
    
    result["elapsed_time"] = time.time() - start_time
    return result


if __name__ == "__main__":
    # 测试用例
    test_result = test_spider(
        url="https://example.com",
        rules={
            "title": {"type": "xpath", "selector": "//title/text()"},
            "content": {"type": "xpath", "selector": "//body//p/text()"}
        }
    )
    print(json.dumps(test_result, ensure_ascii=False, indent=2))
