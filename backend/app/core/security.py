"""
安全模块
JWT令牌生成与校验、密码加密等
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/users/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
    
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码JWT访问令牌
    
    Args:
        token: JWT令牌字符串
    
    Returns:
        解码后的数据字典，如果无效则返回None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    获取当前用户依赖项
    
    用于需要认证的API端点
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # 这里应该从数据库获取用户，暂时返回payload
    return payload


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """获取当前活跃用户"""
    # 可以在这里添加用户状态检查
    return current_user


def check_permission(required_permission: str):
    """
    权限检查装饰器工厂
    
    Args:
        required_permission: 需要的权限标识
    """
    async def permission_checker(current_user: dict = Depends(get_current_active_user)):
        user_permissions = current_user.get("permissions", [])
        if required_permission not in user_permissions and "admin" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return permission_checker
