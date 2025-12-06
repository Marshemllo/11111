"""
用户模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    phone = Column(String(20), nullable=True, comment="手机号")
    role = Column(String(20), default="user", comment="角色: admin/user")
    permissions = Column(Text, nullable=True, comment="权限列表(JSON)")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_superuser = Column(Boolean, default=False, comment="是否超级管理员")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
