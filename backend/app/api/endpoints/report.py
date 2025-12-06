"""
报告管理API接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.core.security import get_current_active_user

router = APIRouter()


class ReportCreate(BaseModel):
    title: str
    content: Optional[str] = None


@router.get("/", summary="获取报告列表")
async def get_reports(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.post("/", summary="创建报告")
async def create_report(
    report_data: ReportCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.get("/{report_id}", summary="获取报告详情")
async def get_report(
    report_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.delete("/{report_id}", summary="删除报告")
async def delete_report(
    report_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")
