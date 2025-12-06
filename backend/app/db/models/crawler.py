"""
数据采集模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class CrawlTask(Base):
    """采集任务表"""
    __tablename__ = "crawl_tasks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    keyword = Column(String(255), nullable=False, comment="采集关键词/需求")
    status = Column(String(20), default="pending", comment="状态: pending/running/completed/failed")
    total_count = Column(Integer, default=0, comment="采集总数")
    current_count = Column(Integer, default=0, comment="当前进度")
    progress_message = Column(String(255), nullable=True, comment="进度消息")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建用户ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联采集数据
    items = relationship("CrawlItem", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CrawlTask(id={self.id}, keyword={self.keyword}, status={self.status})>"


class CrawlItem(Base):
    """采集数据项表"""
    __tablename__ = "crawl_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("crawl_tasks.id"), nullable=False, comment="所属任务ID")
    title = Column(String(500), nullable=False, comment="标题")
    cover_url = Column(String(1000), nullable=True, comment="封面图URL")
    source_url = Column(String(1000), nullable=False, comment="来源URL")
    source_name = Column(String(100), nullable=True, comment="来源名称")
    summary = Column(Text, nullable=True, comment="摘要")
    content = Column(Text, nullable=True, comment="详细内容(深度采集)")
    deep_crawled = Column(Boolean, default=False, comment="是否已深度采集")
    deep_crawl_time = Column(DateTime, nullable=True, comment="深度采集时间")
    is_saved = Column(Boolean, default=False, comment="是否已保存到数据库")
    extra_data = Column(JSON, nullable=True, comment="额外数据")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联任务
    task = relationship("CrawlTask", back_populates="items")
    
    def __repr__(self):
        return f"<CrawlItem(id={self.id}, title={self.title[:20]}...)>"


class SavedData(Base):
    """已保存的数据表"""
    __tablename__ = "saved_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    crawl_item_id = Column(Integer, ForeignKey("crawl_items.id"), nullable=True, comment="来源采集项ID")
    title = Column(String(500), nullable=False, comment="标题")
    cover_url = Column(String(1000), nullable=True, comment="封面图URL")
    source_url = Column(String(1000), nullable=False, comment="来源URL")
    source_name = Column(String(100), nullable=True, comment="来源名称")
    summary = Column(Text, nullable=True, comment="摘要")
    content = Column(Text, nullable=True, comment="详细内容")
    category = Column(String(50), nullable=True, comment="分类")
    tags = Column(String(500), nullable=True, comment="标签(逗号分隔)")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="保存用户ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<SavedData(id={self.id}, title={self.title[:20]}...)>"
