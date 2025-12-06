"""
报告管理API接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date

from app.db.database import get_db
from app.core.security import get_current_active_user

router = APIRouter()


# ==================== 请求/响应模型 ====================

class ReportCreate(BaseModel):
    """报告创建请求"""
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    industry: Optional[str] = None
    report_type: Optional[str] = None
    data_source: Optional[str] = None


class ReportUpdate(BaseModel):
    """报告更新请求"""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    industry: Optional[str] = None
    report_type: Optional[str] = None
    status: Optional[str] = None


class ReportResponse(BaseModel):
    """报告响应"""
    id: int
    title: str
    summary: Optional[str]
    industry: Optional[str]
    report_type: Optional[str]
    status: str
    view_count: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReportDetailResponse(ReportResponse):
    """报告详情响应"""
    content: Optional[str]
    data_source: Optional[str]
    pdf_path: Optional[str]


class ReportListResponse(BaseModel):
    """报告列表响应"""
    total: int
    items: List[ReportResponse]


class AIGenerateRequest(BaseModel):
    """AI生成报告请求"""
    topic: str
    industry: Optional[str] = None
    data_source_ids: Optional[List[int]] = None
    template: Optional[str] = None


# ==================== API接口 ====================

@router.get("/", response_model=ReportListResponse, summary="获取报告列表")
async def get_reports(
    skip: int = 0,
    limit: int = 20,
    industry: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取报告列表
    
    - **industry**: 按行业筛�?
    - **start_date**: 开始日�?
    - **end_date**: 结束日期
    - **keyword**: 搜索关键�?
    - **status**: 报告状�?
    """
    from app.services.report_service import ReportService
    report_service = ReportService(db)
    items, total = report_service.get_list(
        skip=skip,
        limit=limit,
        industry=industry,
        start_date=start_date,
        end_date=end_date,
        keyword=keyword,
        status=status
    )
    return ReportListResponse(total=total, items=items)


@router.get("/industries", response_model=List[str], summary="获取行业列表")
async def get_industries(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取所有行业分�?""
    from app.services.report_service import ReportService
    report_service = ReportService(db)
    return report_service.get_industries()


@router.get("/{report_id}", response_model=ReportDetailResponse, summary="获取报告详情")
async def get_report(
    report_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取指定报告详情"""
    from app.services.report_service import ReportService
    report_service = ReportService(db)
    report = report_service.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存�?)
    report_service.increment_view_count(report_id)
    return report


@router.post("/", response_model=ReportResponse, summary="创建报告")
async def create_report(
    report_data: ReportCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """手动创建报告"""
    from app.services.report_service import ReportService
    report_service = ReportService(db)
    report = report_service.create(
        title=report_data.title,
        created_by=current_user.get("id"),
        summary=report_data.summary,
        content=report_data.content,
        industry=report_data.industry,
        report_type=report_data.report_type,
        data_source=report_data.data_source
    )
    return report


@router.put("/{report_id}", response_model=ReportResponse, summary="更新报告")
async def update_report(
    report_id: int,
    report_data: ReportUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新指定报告"""
    from app.services.report_service import ReportService
    report_service = ReportService(db)
    report = report_service.update(
        report_id,
        title=report_data.title,
        summary=report_data.summary,
        content=report_data.content,
        industry=report_data.industry,
        report_type=report_data.report_type,
        status=report_data.status
    )
    if not report:
        raise HTTPException(status_code=404, detail="报告不存�?)
    return report


@router.delete("/{report_id}", summary="删除报告")
async def delete_report(
    report_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除指定报告"""
    from app.services.report_service import ReportService
    report_service = ReportService(db)
    success = report_service.delete(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="报告不存�?)
    return {"message": "删除成功"}


@router.get("/{report_id}/download", summary="下载报告PDF")
async def download_report(
    report_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    下载报告PDF文件
    
    返回PDF文件�?
    """
    import os
    from app.services.report_service import ReportService
    report_service = ReportService(db)
    report = report_service.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存�?)
    
    # 如果没有PDF文件，先生成
    if not report.pdf_path or not os.path.exists(report.pdf_path):
        pdf_path = report_service.generate_pdf(report_id)
        if not pdf_path:
            raise HTTPException(status_code=500, detail="PDF生成失败")
    else:
        pdf_path = report.pdf_path
    
    report_service.increment_download_count(report_id)
    return FileResponse(
        path=pdf_path,
        filename=f"{report.title}.pdf",
        media_type="application/pdf"
    )


@router.post("/{report_id}/generate-pdf", summary="生成报告PDF")
async def generate_report_pdf(
    report_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """为指定报告生成PDF文件"""
    from app.services.report_service import ReportService
    report_service = ReportService(db)
    pdf_path = report_service.generate_pdf(report_id)
    if not pdf_path:
        raise HTTPException(status_code=404, detail="报告不存在或生成失败")
    return {"message": "PDF生成成功", "pdf_path": pdf_path}


@router.post("/ai-generate", response_model=ReportResponse, summary="AI生成报告")
async def ai_generate_report(
    request: AIGenerateRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    使用AI生成报告
    
    - **topic**: 报告主题
    - **industry**: 行业分类
    - **data_source_ids**: 数据源ID列表
    - **template**: 报告模板
    """
    from app.services.report_service import ReportService
    from app.services.ai_service import AIService
    
    report_service = ReportService(db)
    ai_service = AIService()
    
    # 使用AI生成报告内容
    content = await ai_service.generate_report_content(
        topic=request.topic,
        data=[],
        template=request.template
    )
    
    # 创建报告
    report = report_service.create(
        title=f"{request.topic} 分析报告",
        created_by=current_user.get("id"),
        summary=f"关于{request.topic}的AI生成分析报告",
        content=content,
        industry=request.industry,
        report_type="AI生成",
        data_source="AI分析"
    )
    
    return report

