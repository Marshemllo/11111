"""
WebSocket连接管理与消息广播
"""
from typing import Dict, List, Set, Optional
from fastapi import WebSocket
import json
from datetime import datetime


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接: {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # 房间成员: {room_id: Set[user_id]}
        self.room_members: Dict[int, Set[int]] = {}
        # 用户所在房间: {user_id: Set[room_id]}
        self.user_rooms: Dict[int, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """
        建立WebSocket连接
        
        Args:
            websocket: WebSocket连接对象
            user_id: 用户ID
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_rooms[user_id] = set()
    
    def disconnect(self, user_id: int):
        """
        断开WebSocket连接
        
        Args:
            user_id: 用户ID
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # 从所有房间中移除用户
        if user_id in self.user_rooms:
            for room_id in self.user_rooms[user_id]:
                if room_id in self.room_members:
                    self.room_members[room_id].discard(user_id)
            del self.user_rooms[user_id]
    
    def join_room(self, user_id: int, room_id: int):
        """
        用户加入房间
        
        Args:
            user_id: 用户ID
            room_id: 房间ID
        """
        if room_id not in self.room_members:
            self.room_members[room_id] = set()
        self.room_members[room_id].add(user_id)
        
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room_id)
    
    def leave_room(self, user_id: int, room_id: int):
        """
        用户离开房间
        
        Args:
            user_id: 用户ID
            room_id: 房间ID
        """
        if room_id in self.room_members:
            self.room_members[room_id].discard(user_id)
        
        if user_id in self.user_rooms:
            self.user_rooms[user_id].discard(room_id)
    
    async def send_personal_message(self, message: dict, user_id: int):
        """
        发送私人消息
        
        Args:
            message: 消息内容
            user_id: 目标用户ID
        """
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_json(message)
    
    async def broadcast_to_room(self, message: dict, room_id: int, exclude_user: Optional[int] = None):
        """
        向房间广播消息
        
        Args:
            message: 消息内容
            room_id: 房间ID
            exclude_user: 排除的用户ID（通常是发送者）
        """
        if room_id not in self.room_members:
            return
        
        for user_id in self.room_members[room_id]:
            if exclude_user and user_id == exclude_user:
                continue
            await self.send_personal_message(message, user_id)
    
    async def broadcast_to_all(self, message: dict, exclude_user: Optional[int] = None):
        """
        向所有在线用户广播消息
        
        Args:
            message: 消息内容
            exclude_user: 排除的用户ID
        """
        for user_id, websocket in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            await websocket.send_json(message)
    
    def get_online_users(self) -> List[int]:
        """获取所有在线用户ID"""
        return list(self.active_connections.keys())
    
    def get_room_online_users(self, room_id: int) -> List[int]:
        """获取房间内在线用户ID"""
        if room_id not in self.room_members:
            return []
        
        online_users = []
        for user_id in self.room_members[room_id]:
            if user_id in self.active_connections:
                online_users.append(user_id)
        return online_users
    
    def is_user_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.active_connections


# 全局连接管理器实例
manager = ConnectionManager()


class MessageBuilder:
    """消息构建器"""
    
    @staticmethod
    def chat_message(
        room_id: int,
        sender_id: int,
        sender_name: str,
        content: str,
        message_type: str = "text",
        extra_data: Optional[dict] = None
    ) -> dict:
        """构建聊天消息"""
        return {
            "type": "chat_message",
            "data": {
                "room_id": room_id,
                "sender_id": sender_id,
                "sender_name": sender_name,
                "content": content,
                "message_type": message_type,
                "extra_data": extra_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    @staticmethod
    def ai_response(
        room_id: int,
        content: str,
        action: str,
        data: Optional[dict] = None
    ) -> dict:
        """构建AI响应消息"""
        return {
            "type": "ai_response",
            "data": {
                "room_id": room_id,
                "content": content,
                "action": action,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    @staticmethod
    def user_join(room_id: int, user_id: int, username: str) -> dict:
        """构建用户加入消息"""
        return {
            "type": "user_join",
            "data": {
                "room_id": room_id,
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    @staticmethod
    def user_leave(room_id: int, user_id: int, username: str) -> dict:
        """构建用户离开消息"""
        return {
            "type": "user_leave",
            "data": {
                "room_id": room_id,
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    @staticmethod
    def system_notification(content: str, level: str = "info") -> dict:
        """构建系统通知消息"""
        return {
            "type": "system_notification",
            "data": {
                "content": content,
                "level": level,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    @staticmethod
    def online_users(room_id: int, users: List[dict]) -> dict:
        """构建在线用户列表消息"""
        return {
            "type": "online_users",
            "data": {
                "room_id": room_id,
                "users": users,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
