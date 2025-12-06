"""
报告模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class Report(Base):
    """AI生成报告表"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, comment="报告标题")
    summary = Column(Text, nullable=True, comment="报告摘要")
    content = Column(Text, nullable=True, comment="报告内容(Markdown/HTML)")
    industry = Column(String(100), nullable=True, comment="行业分类")
    report_type = Column(String(50), nullable=True, comment="报告类型")
    data_source = Column(String(255), nullable=True, comment="数据来源")
    pdf_path = Column(String(255), nullable=True, comment="PDF文件路径")
    status = Column(String(20), default="draft", comment="状态: draft/published/archived")
    view_count = Column(Integer, default=0, comment="查看次数")
    download_count = Column(Integer, default=0, comment="下载次数")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Report(id={self.id}, title={self.title})>"
