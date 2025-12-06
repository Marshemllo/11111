"""
聊天相关模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base


class RoomType(enum.Enum):
    """聊天室类型"""
    PRIVATE = "private"  # 私聊
    GROUP = "group"      # 群聊


class ChatRoom(Base):
    """聊天室表"""
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=True, comment="聊天室名称")
    room_type = Column(String(20), default="group", comment="类型: private/group")
    avatar = Column(String(255), nullable=True, comment="聊天室头像")
    description = Column(String(255), nullable=True, comment="描述")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者ID")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关联消息
    messages = relationship("ChatMessage", back_populates="room")
    
    def __repr__(self):
        return f"<ChatRoom(id={self.id}, name={self.name})>"


class ChatRoomMember(Base):
    """聊天室成员表"""
    __tablename__ = "chat_room_members"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False, comment="聊天室ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    nickname = Column(String(50), nullable=True, comment="群内昵称")
    role = Column(String(20), default="member", comment="角色: owner/admin/member")
    is_muted = Column(Boolean, default=False, comment="是否被禁言")
    joined_at = Column(DateTime, server_default=func.now(), comment="加入时间")
    
    def __repr__(self):
        return f"<ChatRoomMember(room_id={self.room_id}, user_id={self.user_id})>"


class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False, comment="聊天室ID")
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="发送者ID")
    message_type = Column(String(20), default="text", comment="消息类型: text/image/file/ai_response")
    content = Column(Text, nullable=False, comment="消息内容")
    extra_data = Column(Text, nullable=True, comment="附加数据(JSON)")
    is_ai_command = Column(Boolean, default=False, comment="是否为AI命令")
    ai_response = Column(Text, nullable=True, comment="AI响应内容")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")
    created_at = Column(DateTime, server_default=func.now(), comment="发送时间")
    
    # 关联聊天室
    room = relationship("ChatRoom", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, room_id={self.room_id})>"
