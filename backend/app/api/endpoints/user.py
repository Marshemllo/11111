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
from app.db.models import User
from app.core.security import (
    get_current_user, get_current_active_user, 
    verify_password, get_password_hash, create_access_token
)

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "user"


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=Token, summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="用户已被禁用")
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/logout", summary="用户登出")
async def logout():
    return {"message": "登出成功"}


@router.get("/", response_model=List[UserResponse], summary="获取用户列表")
async def get_users(
    skip: int = 0,
    limit: int = 20,
    keyword: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("sub")
    operator = db.query(User).filter(User.id == int(user_id)).first()
    if not operator or operator.role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="权限不足")
    
    query = db.query(User)
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) |
            (User.email.contains(keyword)) |
            (User.nickname.contains(keyword))
        )
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户详情")
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    operator_id = current_user.get("sub")
    operator = db.query(User).filter(User.id == int(operator_id)).first()
    if not operator or operator.role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="权限不足")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/create", response_model=UserResponse, summary="创建用户")
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    operator_id = current_user.get("sub")
    operator = db.query(User).filter(User.id == int(operator_id)).first()
    if not operator or operator.role != "superadmin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        nickname=user_data.nickname or user_data.username,
        phone=user_data.phone,
        role=user_data.role if user_data.role in ["user", "admin"] else "user",
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")


@router.post("/{user_id}/toggle-status", summary="切换用户状态")
async def toggle_user_status(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    raise HTTPException(status_code=501, detail="功能开发中")
