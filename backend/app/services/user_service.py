"""
用户服务层
用户增删改查业务逻辑
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models.user import User
from app.core.security import get_password_hash, verify_password


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_list(
        self,
        skip: int = 0,
        limit: int = 20,
        keyword: Optional[str] = None
    ) -> List[User]:
        """获取用户列表"""
        query = self.db.query(User)
        
        if keyword:
            query = query.filter(
                (User.username.contains(keyword)) |
                (User.nickname.contains(keyword)) |
                (User.email.contains(keyword))
            )
        
        return query.offset(skip).limit(limit).all()
    
    def create(
        self,
        username: str,
        email: str,
        password: str,
        nickname: Optional[str] = None,
        phone: Optional[str] = None
    ) -> User:
        """创建用户"""
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            nickname=nickname or username,
            phone=phone
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """更新用户"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """验证用户登录"""
        user = self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def toggle_status(self, user_id: int) -> Optional[User]:
        """切换用户状态"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        user.is_active = not user.is_active
        self.db.commit()
        self.db.refresh(user)
        return user
