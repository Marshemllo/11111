"""
报告服务层
报告生成业务逻辑
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, date
import os

from app.db.models.report import Report
from app.core.config import settings


class ReportService:
    """报告服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, report_id: int) -> Optional[Report]:
        """根据ID获取报告"""
        return self.db.query(Report).filter(Report.id == report_id).first()
    
    def get_list(
        self,
        skip: int = 0,
        limit: int = 20,
        industry: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        keyword: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[Report], int]:
        """获取报告列表"""
        query = self.db.query(Report)
        
        if industry:
            query = query.filter(Report.industry == industry)
        
        if start_date:
            query = query.filter(Report.created_at >= start_date)
        
        if end_date:
            query = query.filter(Report.created_at <= end_date)
        
        if keyword:
            query = query.filter(
                (Report.title.contains(keyword)) |
                (Report.summary.contains(keyword))
            )
        
        if status:
            query = query.filter(Report.status == status)
        
        total = query.count()
        items = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
        
        return items, total
    
    def create(
        self,
        title: str,
        created_by: int,
        summary: Optional[str] = None,
        content: Optional[str] = None,
        industry: Optional[str] = None,
        report_type: Optional[str] = None,
        data_source: Optional[str] = None
    ) -> Report:
        """创建报告"""
        report = Report(
            title=title,
            summary=summary,
            content=content,
            industry=industry,
            report_type=report_type,
            data_source=data_source,
            created_by=created_by
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def update(self, report_id: int, **kwargs) -> Optional[Report]:
        """更新报告"""
        report = self.get_by_id(report_id)
        if not report:
            return None
        
        for key, value in kwargs.items():
            if hasattr(report, key) and value is not None:
                setattr(report, key, value)
        
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def delete(self, report_id: int) -> bool:
        """删除报告"""
        report = self.get_by_id(report_id)
        if not report:
            return False
        
        # 删除关联的PDF文件
        if report.pdf_path and os.path.exists(report.pdf_path):
            os.remove(report.pdf_path)
        
        self.db.delete(report)
        self.db.commit()
        return True
    
    def increment_view_count(self, report_id: int) -> None:
        """增加查看次数"""
        report = self.get_by_id(report_id)
        if report:
            report.view_count += 1
            self.db.commit()
    
    def increment_download_count(self, report_id: int) -> None:
        """增加下载次数"""
        report = self.get_by_id(report_id)
        if report:
            report.download_count += 1
            self.db.commit()
    
    def generate_pdf(self, report_id: int) -> Optional[str]:
        """
        生成报告PDF
        
        Args:
            report_id: 报告ID
        
        Returns:
            PDF文件路径
        """
        report = self.get_by_id(report_id)
        if not report:
            return None
        
        # 确保报告目录存在
        report_dir = os.path.join(settings.REPORT_DIR, str(report_id))
        os.makedirs(report_dir, exist_ok=True)
        
        # PDF文件路径
        pdf_filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = os.path.join(report_dir, pdf_filename)
        
        # TODO: 实现PDF生成逻辑
        # 可以使用 weasyprint, reportlab, pdfkit 等库
        
        # 更新报告的PDF路径
        report.pdf_path = pdf_path
        self.db.commit()
        
        return pdf_path
    
    def get_industries(self) -> List[str]:
        """获取所有行业分类"""
        result = self.db.query(Report.industry).distinct().filter(
            Report.industry.isnot(None)
        ).all()
        return [r[0] for r in result]
