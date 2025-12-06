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
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import markdown
        import re
        
        report = self.get_by_id(report_id)
        if not report:
            return None
        
        # 确保报告目录存在
        report_dir = os.path.join(settings.REPORT_DIR, str(report_id))
        os.makedirs(report_dir, exist_ok=True)
        
        # PDF文件路径
        pdf_filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = os.path.join(report_dir, pdf_filename)
        
        # 注册中文字体（使用系统自带的微软雅黑）
        try:
            font_path = "C:/Windows/Fonts/msyh.ttc"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('MSYaHei', font_path))
                chinese_font = 'MSYaHei'
            else:
                chinese_font = 'Helvetica'
        except Exception:
            chinese_font = 'Helvetica'
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ChineseTitle',
            parent=styles['Title'],
            fontName=chinese_font,
            fontSize=18,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'ChineseHeading',
            parent=styles['Heading2'],
            fontName=chinese_font,
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10
        )
        body_style = ParagraphStyle(
            'ChineseBody',
            parent=styles['Normal'],
            fontName=chinese_font,
            fontSize=11,
            leading=18,
            spaceAfter=10
        )
        
        # 构建PDF内容
        story = []
        
        # 标题
        story.append(Paragraph(report.title, title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 元信息表格
        meta_data = [
            ['行业分类', report.industry or '未分类'],
            ['报告类型', report.report_type or '未知'],
            ['数据来源', report.data_source or '未知'],
            ['创建时间', report.created_at.strftime('%Y-%m-%d %H:%M:%S') if report.created_at else '未知'],
        ]
        meta_table = Table(meta_data, colWidths=[3*cm, 10*cm])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 1*cm))
        
        # 摘要
        if report.summary:
            story.append(Paragraph('摘要', heading_style))
            story.append(Paragraph(report.summary, body_style))
            story.append(Spacer(1, 0.5*cm))
        
        # 正文内容
        if report.content:
            story.append(Paragraph('报告内容', heading_style))
            # 将Markdown转换为纯文本段落
            content_text = report.content
            # 移除Markdown标记
            content_text = re.sub(r'#{1,6}\s*', '', content_text)  # 移除标题标记
            content_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', content_text)  # 移除粗体
            content_text = re.sub(r'\*([^*]+)\*', r'\1', content_text)  # 移除斜体
            content_text = re.sub(r'`([^`]+)`', r'\1', content_text)  # 移除代码标记
            
            # 按段落分割
            paragraphs = content_text.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para:
                    # 处理列表项
                    if para.startswith('- ') or para.startswith('* '):
                        para = '• ' + para[2:]
                    story.append(Paragraph(para, body_style))
        
        # 页脚信息
        story.append(Spacer(1, 2*cm))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontName=chinese_font,
            fontSize=9,
            textColor=colors.grey
        )
        story.append(Paragraph('--- 本报告由智能数据分析平台自动生成 ---', footer_style))
        
        # 生成PDF
        doc.build(story)
        
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
