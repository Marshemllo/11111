"""
在线聊天API接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.core.security import get_current_active_user

router = APIRouter()


class ChatRoomCreate(BaseModel):
    name: str
    room_type: str = "group"


class ChatMessageCreate(BaseModel):
    content: str
    room_id: int


@router.get("/rooms", summary="获取聊天室列表")
async def get_chat_rooms(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.post("/rooms", summary="创建聊天室")
async def create_chat_room(
    room_data: ChatRoomCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.get("/rooms/{room_id}/messages", summary="获取聊天记录")
async def get_chat_messages(
    room_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.post("/rooms/{room_id}/messages", summary="发送消息")
async def send_message(
    room_id: int,
    message_data: ChatMessageCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")
