"""
数据采集管理API接口
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.db.models import CrawlTask, CrawlItem, SavedData, User
from app.core.security import get_current_active_user
from app.services.crawler_service import crawler_service

router = APIRouter()


class CrawlRequest(BaseModel):
    keyword: str


class CrawlTaskResponse(BaseModel):
    id: int
    keyword: str
    status: str
    total_count: int
    current_count: int
    progress_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CrawlItemResponse(BaseModel):
    id: int
    task_id: int
    title: str
    cover_url: Optional[str] = None
    source_url: str
    source_name: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    deep_crawled: bool
    is_saved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SaveItemsRequest(BaseModel):
    item_ids: List[int]


class SavedDataResponse(BaseModel):
    id: int
    title: str
    cover_url: Optional[str] = None
    source_url: str
    source_name: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


async def do_crawl_task(task_id: int, keyword: str, user_id: int, db: Session):
    """后台执行采集任务"""
    task = db.query(CrawlTask).filter(CrawlTask.id == task_id).first()
    if not task:
        return
    
    try:
        task.status = "running"
        task.progress_message = "正在采集数据..."
        db.commit()
        
        results = await crawler_service.crawl_all(keyword)
        task.total_count = len(results)
        
        for i, item_data in enumerate(results):
            task.current_count = i + 1
            task.progress_message = f"正在处理 {i+1}/{len(results)}"
            db.commit()
            
            item = CrawlItem(
                task_id=task_id,
                title=item_data.get("title", ""),
                cover_url=item_data.get("cover_url"),
                source_url=item_data.get("source_url", ""),
                source_name=item_data.get("source_name"),
                summary=item_data.get("summary"),
            )
            db.add(item)
        
        task.status = "completed"
        task.progress_message = f"采集完成，共{len(results)}条数据"
        db.commit()
        
    except Exception as e:
        task.status = "failed"
        task.progress_message = f"采集失败: {str(e)}"
        db.commit()


@router.post("/start", response_model=CrawlTaskResponse)
async def start_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """开始采集任务"""
    user_id = int(current_user.get("sub"))
    
    task = CrawlTask(
        keyword=request.keyword,
        status="pending",
        user_id=user_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    background_tasks.add_task(do_crawl_task, task.id, request.keyword, user_id, db)
    
    return task


@router.get("/tasks", response_model=List[CrawlTaskResponse])
async def get_tasks(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取采集任务列表"""
    user_id = int(current_user.get("sub"))
    tasks = db.query(CrawlTask).filter(
        CrawlTask.user_id == user_id
    ).order_by(CrawlTask.created_at.desc()).limit(20).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=CrawlTaskResponse)
async def get_task(
    task_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取任务详情和进度"""
    task = db.query(CrawlTask).filter(CrawlTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.get("/tasks/{task_id}/items", response_model=List[CrawlItemResponse])
async def get_task_items(
    task_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取任务的采集数据"""
    items = db.query(CrawlItem).filter(CrawlItem.task_id == task_id).all()
    return items


@router.post("/items/{item_id}/deep-crawl")
async def deep_crawl_item(
    item_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """深度采集单个数据项"""
    item = db.query(CrawlItem).filter(CrawlItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="数据不存在")
    
    result = await crawler_service.deep_crawl(item.source_url)
    
    if result["success"]:
        item.content = result["content"]
        if result["cover_url"] and not item.cover_url:
            item.cover_url = result["cover_url"]
        item.deep_crawled = True
        item.deep_crawl_time = datetime.utcnow()
        db.commit()
        db.refresh(item)
        return {"success": True, "message": "深度采集成功", "item": item}
    else:
        return {"success": False, "message": "深度采集失败"}


@router.post("/items/save")
async def save_items(
    request: SaveItemsRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """保存选中的数据到数据库"""
    user_id = int(current_user.get("sub"))
    saved_count = 0
    
    for item_id in request.item_ids:
        item = db.query(CrawlItem).filter(CrawlItem.id == item_id).first()
        if item and not item.is_saved:
            saved_data = SavedData(
                crawl_item_id=item.id,
                title=item.title,
                cover_url=item.cover_url,
                source_url=item.source_url,
                source_name=item.source_name,
                summary=item.summary,
                content=item.content,
                user_id=user_id
            )
            db.add(saved_data)
            item.is_saved = True
            saved_count += 1
    
    db.commit()
    return {"success": True, "saved_count": saved_count}


@router.get("/saved", response_model=List[SavedDataResponse])
async def get_saved_data(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取已保存的数据列表"""
    user_id = int(current_user.get("sub"))
    data = db.query(SavedData).filter(
        SavedData.user_id == user_id
    ).order_by(SavedData.created_at.desc()).offset(skip).limit(limit).all()
    return data


@router.delete("/saved/{data_id}")
async def delete_saved_data(
    data_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除已保存的数据"""
    user_id = int(current_user.get("sub"))
    data = db.query(SavedData).filter(
        SavedData.id == data_id,
        SavedData.user_id == user_id
    ).first()
    if not data:
        raise HTTPException(status_code=404, detail="数据不存在")
    
    db.delete(data)
    db.commit()
    return {"success": True, "message": "删除成功"}
