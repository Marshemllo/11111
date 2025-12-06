"""
爬虫相关模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base


class SpiderStatus(enum.Enum):
    """爬虫状态枚举"""
    IDLE = "idle"           # 空闲
    RUNNING = "running"     # 运行中
    PAUSED = "paused"       # 暂停
    ERROR = "error"         # 错误
    COMPLETED = "completed" # 完成


class DataSource(Base):
    """数据源表"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="数据源名称")
    url = Column(String(500), nullable=False, comment="数据源URL")
    source_type = Column(String(50), nullable=False, comment="数据源类型")
    industry_tag = Column(String(100), nullable=True, comment="行业标签")
    description = Column(Text, nullable=True, comment="描述")
    config = Column(Text, nullable=True, comment="配置信息(JSON)")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联爬虫规则
    spider_rules = relationship("SpiderRule", back_populates="data_source")
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name={self.name})>"


class SpiderRule(Base):
    """爬虫规则表"""
    __tablename__ = "spider_rules"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="爬虫名称")
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False, comment="数据源ID")
    spider_type = Column(String(50), nullable=False, comment="爬虫类型")
    start_urls = Column(Text, nullable=False, comment="起始URL列表(JSON)")
    allowed_domains = Column(Text, nullable=True, comment="允许的域名(JSON)")
    rules = Column(Text, nullable=True, comment="爬取规则(JSON)")
    item_fields = Column(Text, nullable=True, comment="数据字段定义(JSON)")
    status = Column(String(20), default="idle", comment="状态")
    last_run_at = Column(DateTime, nullable=True, comment="最后运行时间")
    last_run_result = Column(Text, nullable=True, comment="最后运行结果")
    total_items = Column(Integer, default=0, comment="总爬取数量")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联数据源
    data_source = relationship("DataSource", back_populates="spider_rules")
    
    def __repr__(self):
        return f"<SpiderRule(id={self.id}, name={self.name})>"


class SpiderData(Base):
    """爬虫数据表"""
    __tablename__ = "spider_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    spider_rule_id = Column(Integer, ForeignKey("spider_rules.id"), nullable=False, comment="爬虫规则ID")
    url = Column(String(500), nullable=False, comment="数据来源URL")
    title = Column(String(255), nullable=True, comment="标题")
    content = Column(Text, nullable=True, comment="内容")
    raw_data = Column(Text, nullable=True, comment="原始数据(JSON)")
    industry_tag = Column(String(100), nullable=True, comment="行业标签")
    crawled_at = Column(DateTime, server_default=func.now(), comment="爬取时间")
    
    def __repr__(self):
        return f"<SpiderData(id={self.id}, title={self.title})>"
