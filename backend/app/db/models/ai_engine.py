"""
AI引擎配置模型
存储各种AI服务的API配置
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from app.db.database import Base


class AIEngine(Base):
    """AI引擎配置表"""
    __tablename__ = "ai_engines"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, comment="引擎名称")
    provider = Column(String(50), nullable=False, comment="服务提供商: openai/azure/siliconflow/local")
    api_key = Column(String(500), nullable=True, comment="API密钥(加密存储)")
    api_base_url = Column(String(255), nullable=True, comment="API基础URL")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    description = Column(Text, nullable=True, comment="引擎描述")
    
    # 配置参数
    max_tokens = Column(Integer, default=2048, comment="最大Token数")
    temperature = Column(Float, default=0.7, comment="温度参数")
    timeout = Column(Integer, default=30, comment="超时时间(秒)")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_default = Column(Boolean, default=False, comment="是否默认引擎")
    
    # 使用统计
    total_requests = Column(Integer, default=0, comment="总请求次数")
    total_tokens = Column(Integer, default=0, comment="总消耗Token")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<AIEngine(id={self.id}, name={self.name}, provider={self.provider})>"


class AIConversation(Base):
    """AI对话记录表"""
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    engine_id = Column(Integer, nullable=True, comment="使用的AI引擎ID")
    session_id = Column(String(100), index=True, comment="会话ID")
    
    # 对话内容
    role = Column(String(20), nullable=False, comment="角色: user/assistant/system")
    content = Column(Text, nullable=False, comment="消息内容")
    
    # Token统计
    prompt_tokens = Column(Integer, default=0, comment="输入Token数")
    completion_tokens = Column(Integer, default=0, comment="输出Token数")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    def __repr__(self):
        return f"<AIConversation(id={self.id}, user_id={self.user_id}, role={self.role})>"
