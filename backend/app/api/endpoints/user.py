"""
用户管理API接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.db.database import get_db
from app.core.security import get_current_user, get_current_active_user

router = APIRouter()


# ==================== 请求/响应模型 ====================

class UserCreate(BaseModel):
    """用户创建请求"""
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    """用户更新请求"""
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    nickname: Optional[str]
    avatar: Optional[str]
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


# ==================== API接口 ====================

@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    - **username**: 用户名（唯一）
    - **email**: 邮箱（唯一）
    - **password**: 密码
    - **nickname**: 昵称（可选）
    - **phone**: 手机号（可选）
    """
    # TODO: 实现用户注册逻辑
    pass


@router.post("/login", response_model=Token, summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口
    
    返回JWT访问令牌
    """
    # TODO: 实现用户登录逻辑
    pass


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """获取当前登录用户信息"""
    # TODO: 实现获取当前用户信息逻辑
    pass


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
async def update_current_user(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前登录用户信息"""
    # TODO: 实现更新用户信息逻辑
    pass


@router.get("/", response_model=List[UserResponse], summary="获取用户列表")
async def get_users(
    skip: int = 0,
    limit: int = 20,
    keyword: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（管理员权限）
    
    - **skip**: 跳过记录数
    - **limit**: 返回记录数
    - **keyword**: 搜索关键词
    """
    # TODO: 实现获取用户列表逻辑
    pass


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户详情")
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取指定用户详情"""
    # TODO: 实现获取用户详情逻辑
    pass


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户信息")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新指定用户信息（管理员权限）"""
    # TODO: 实现更新用户逻辑
    pass


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除指定用户（管理员权限）"""
    # TODO: 实现删除用户逻辑
    pass


@router.post("/{user_id}/toggle-status", summary="切换用户状态")
async def toggle_user_status(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """启用/禁用用户（管理员权限）"""
    # TODO: 实现切换用户状态逻辑
    pass
