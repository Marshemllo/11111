"""
Scrapy Pipeline 定义
数据处理和存储管道
"""
import json
from datetime import datetime


class DatabasePipeline:
    """数据库存储管道"""
    
    def __init__(self):
        self.db = None
    
    def open_spider(self, spider):
        """爬虫启动时初始化数据库连接"""
        # 延迟导入以避免循环依赖
        from app.db.database import get_db_context
        self.get_db_context = get_db_context
    
    def close_spider(self, spider):
        """爬虫关闭时清理资源"""
        pass
    
    def process_item(self, item, spider):
        """处理每个数据项"""
        with self.get_db_context() as db:
            from app.db.models.spider import SpiderData
            
            # 创建数据记录
            data = SpiderData(
                spider_rule_id=item.get("spider_rule_id"),
                url=item.get("url"),
                title=item.get("title"),
                content=item.get("content"),
                raw_data=json.dumps(dict(item), ensure_ascii=False),
                industry_tag=item.get("industry_tag"),
                crawled_at=datetime.utcnow()
            )
            db.add(data)
        
        return item


class JsonExportPipeline:
    """JSON导出管道"""
    
    def __init__(self):
        self.items = []
    
    def open_spider(self, spider):
        """爬虫启动时初始化"""
        self.items = []
    
    def close_spider(self, spider):
        """爬虫关闭时导出数据"""
        if self.items:
            filename = f"output_{spider.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
    
    def process_item(self, item, spider):
        """处理每个数据项"""
        self.items.append(dict(item))
        return item


class DataCleaningPipeline:
    """数据清洗管道"""
    
    def process_item(self, item, spider):
        """清洗数据"""
        # 清理标题
        if item.get("title"):
            item["title"] = item["title"].strip()
        
        # 清理内容
        if item.get("content"):
            item["content"] = item["content"].strip()
            # 移除多余空白
            import re
            item["content"] = re.sub(r"\s+", " ", item["content"])
        
        # 添加爬取时间
        if not item.get("crawled_at"):
            item["crawled_at"] = datetime.utcnow().isoformat()
        
        return item
