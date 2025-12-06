"""
爬虫管理API接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.core.security import get_current_active_user

router = APIRouter()


class DataSourceCreate(BaseModel):
    name: str
    url: str
    industry_tag: Optional[str] = None


class SpiderRuleCreate(BaseModel):
    name: str
    data_source_id: int


class SpiderTestRequest(BaseModel):
    url: str
    selector: str


class SpiderTestResponse(BaseModel):
    success: bool
    data: Optional[List[str]] = None
    message: Optional[str] = None


@router.get("/sources", summary="获取数据源列表")
async def get_data_sources(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.post("/sources", summary="创建数据源")
async def create_data_source(
    source_data: DataSourceCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.get("/rules", summary="获取爬虫规则列表")
async def get_spider_rules(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.post("/rules", summary="创建爬虫规则")
async def create_spider_rule(
    rule_data: SpiderRuleCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.post("/test", response_model=SpiderTestResponse, summary="测试爬虫")
async def test_spider(
    test_data: SpiderTestRequest,
    current_user: dict = Depends(get_current_active_user)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.get("/industry-tags", summary="获取行业标签")
async def get_industry_tags(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")
