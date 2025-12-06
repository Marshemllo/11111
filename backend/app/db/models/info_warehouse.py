"""
信息仓库模型
存储采集的数据、文档、知识库等
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class InfoCategory(Base):
    """信息分类表"""
    __tablename__ = "info_categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    parent_id = Column(Integer, default=0, comment="父分类ID, 0为顶级分类")
    icon = Column(String(50), nullable=True, comment="图标")
    sort_order = Column(Integer, default=0, comment="排序")
    description = Column(Text, nullable=True, comment="分类描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<InfoCategory(id={self.id}, name={self.name})>"


class InfoDocument(Base):
    """信息文档表 - 存储采集的文章、新闻等"""
    __tablename__ = "info_documents"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, nullable=True, index=True, comment="分类ID")
    source_id = Column(Integer, nullable=True, comment="数据源ID")
    
    # 基本信息
    title = Column(String(500), nullable=False, index=True, comment="标题")
    content = Column(Text, nullable=True, comment="正文内容")
    summary = Column(Text, nullable=True, comment="摘要")
    author = Column(String(100), nullable=True, comment="作者")
    source_name = Column(String(100), nullable=True, comment="来源名称")
    source_url = Column(String(1000), nullable=True, comment="原文链接")
    
    # 媒体资源
    cover_image = Column(String(500), nullable=True, comment="封面图片URL")
    images = Column(JSON, nullable=True, comment="图片列表(JSON)")
    attachments = Column(JSON, nullable=True, comment="附件列表(JSON)")
    
    # 分类标签
    tags = Column(JSON, nullable=True, comment="标签列表(JSON)")
    industry = Column(String(50), nullable=True, index=True, comment="行业分类")
    region = Column(String(50), nullable=True, index=True, comment="地区")
    
    # 情感分析
    sentiment = Column(String(20), nullable=True, comment="情感倾向: positive/negative/neutral")
    sentiment_score = Column(Float, nullable=True, comment="情感分数 -1到1")
    
    # 统计数据
    view_count = Column(Integer, default=0, comment="浏览次数")
    like_count = Column(Integer, default=0, comment="点赞数")
    comment_count = Column(Integer, default=0, comment="评论数")
    share_count = Column(Integer, default=0, comment="分享数")
    
    # 状态
    status = Column(String(20), default="published", comment="状态: draft/published/archived")
    is_top = Column(Boolean, default=False, comment="是否置顶")
    is_hot = Column(Boolean, default=False, comment="是否热门")
    
    # 时间
    publish_time = Column(DateTime, nullable=True, comment="发布时间")
    crawl_time = Column(DateTime, nullable=True, comment="采集时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<InfoDocument(id={self.id}, title={self.title[:30] if self.title else ''})>"


class InfoKeyword(Base):
    """关键词表 - 用于热词分析"""
    __tablename__ = "info_keywords"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    keyword = Column(String(100), unique=True, nullable=False, index=True, comment="关键词")
    frequency = Column(Integer, default=1, comment="出现频次")
    category = Column(String(50), nullable=True, comment="关键词分类")
    is_hot = Column(Boolean, default=False, comment="是否热词")
    trend = Column(String(20), nullable=True, comment="趋势: up/down/stable")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<InfoKeyword(id={self.id}, keyword={self.keyword})>"


class InfoStatistics(Base):
    """信息统计表 - 按日期统计"""
    __tablename__ = "info_statistics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stat_date = Column(DateTime, nullable=False, index=True, comment="统计日期")
    category_id = Column(Integer, nullable=True, comment="分类ID")
    
    # 统计数据
    total_count = Column(Integer, default=0, comment="总数量")
    positive_count = Column(Integer, default=0, comment="正面数量")
    negative_count = Column(Integer, default=0, comment="负面数量")
    neutral_count = Column(Integer, default=0, comment="中性数量")
    
    # 地区分布 (JSON格式)
    region_distribution = Column(JSON, nullable=True, comment="地区分布")
    # 行业分布 (JSON格式)
    industry_distribution = Column(JSON, nullable=True, comment="行业分布")
    # 热词统计 (JSON格式)
    hot_keywords = Column(JSON, nullable=True, comment="热词统计")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    def __repr__(self):
        return f"<InfoStatistics(id={self.id}, stat_date={self.stat_date})>"
