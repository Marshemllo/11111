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


# ==================== 请求/响应模型 ====================

class UserCreate(BaseModel):
    """用户创建请求"""
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "user"  # user, admin, superadmin


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

@router.post("/create", response_model=UserResponse, summary="创建用户（超级管理员）")
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建用户接口（仅超级管理员可用）
    
    用户角色等级：
    - **user**: 普通用户
    - **admin**: 管理员
    - **superadmin**: 超级管理员
    """
    # 检查是否为超级管理员
    user_id = current_user.get("sub")
    operator = db.query(User).filter(User.id == int(user_id)).first()
    
    if not operator or operator.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅超级管理员可以创建用户"
        )
    
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 验证角色值
    valid_roles = ["user", "admin", "superadmin"]
    role = user_data.role if hasattr(user_data, 'role') and user_data.role in valid_roles else "user"
    
    # 创建新用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        nickname=user_data.nickname or user_data.username,
        phone=user_data.phone,
        role=role,
        is_active=True,
        is_superuser=(role == "superadmin")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token, summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口
    
    返回JWT访问令牌
    """
    # 查找用户
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()
    
    # 创建访问令牌
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前登录用户信息"""
    user_id = current_user.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


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
    获取用户列表（管理员和超级管理员可用）
    
    - **skip**: 跳过记录数
    - **limit**: 返回记录数
    - **keyword**: 搜索关键词
    
    权限说明：
    - 普通用户：无权访问
    - 管理员：可查看列表
    - 超级管理员：可查看列表
    """
    # 检查权限：只有管理员和超级管理员可以查看用户列表
    user_id = current_user.get("sub")
    operator = db.query(User).filter(User.id == int(user_id)).first()
    
    if not operator or operator.role not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可查看用户列表"
        )
    
    # 构建查询
    query = db.query(User)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) | 
            (User.email.contains(keyword)) |
            (User.nickname.contains(keyword))
        )
    
    # 分页
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户详情")
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取指定用户详情（管理员和超级管理员可用）
    """
    # 检查权限
    operator_id = current_user.get("sub")
    operator = db.query(User).filter(User.id == int(operator_id)).first()
    
    if not operator or operator.role not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户信息")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新指定用户信息（仅超级管理员可用）
    
    权限说明：
    - 普通用户：无权操作
    - 管理员：无权操作
    - 超级管理员：可更新用户信息
    """
    # 检查权限：只有超级管理员可以更新用户
    operator_id = current_user.get("sub")
    operator = db.query(User).filter(User.id == int(operator_id)).first()
    
    if not operator or operator.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅超级管理员可管理用户"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息
    if user_data.nickname is not None:
        user.nickname = user_data.nickname
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.avatar is not None:
        user.avatar = user_data.avatar
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除指定用户（仅超级管理员可用）
    
    权限说明：
    - 普通用户：无权操作
    - 管理员：无权操作
    - 超级管理员：可删除用户
    """
    # 检查权限：只有超级管理员可以删除用户
    operator_id = current_user.get("sub")
    operator = db.query(User).filter(User.id == int(operator_id)).first()
    
    if not operator or operator.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅超级管理员可管理用户"
        )
    
    # 不能删除自己
    if user_id == int(operator_id):
        raise HTTPException(status_code=400, detail="不能删除自己")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{user_id}/toggle-status", summary="切换用户状态")
async def toggle_user_status(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    启用/禁用用户（仅超级管理员可用）
    
    权限说明：
    - 普通用户：无权操作
    - 管理员：无权操作
    - 超级管理员：可切换用户状态
    """
    # 检查权限：只有超级管理员可以切换用户状态
    operator_id = current_user.get("sub")
    operator = db.query(User).filter(User.id == int(operator_id)).first()
    
    if not operator or operator.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅超级管理员可管理用户"
        )
    
    # 不能禁用自己
    if user_id == int(operator_id):
        raise HTTPException(status_code=400, detail="不能禁用自己")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return {"message": "操作成功", "is_active": user.is_active}
