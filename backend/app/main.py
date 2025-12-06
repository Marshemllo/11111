"""
FastAPI 应用入口文件
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api import api_router
from app.db.database import init_db
from app.websocket.chat_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # 初始化数据库
    # init_db()  # 取消注释以自动创建表
    yield
    # 关闭时执行
    print("Shutting down...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智能数据分析平台 - 集成爬虫、AI分析、实时聊天的综合系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# ==================== WebSocket端点 ====================

@app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: int):
    """
    WebSocket聊天端点
    
    用于实时聊天功能
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # 处理不同类型的消息
            message_type = data.get("type")
            
            if message_type == "join_room":
                room_id = data.get("room_id")
                manager.join_room(user_id, room_id)
                # 通知房间其他成员
                await manager.broadcast_to_room(
                    {"type": "user_joined", "user_id": user_id},
                    room_id,
                    exclude_user=user_id
                )
            
            elif message_type == "leave_room":
                room_id = data.get("room_id")
                manager.leave_room(user_id, room_id)
                await manager.broadcast_to_room(
                    {"type": "user_left", "user_id": user_id},
                    room_id
                )
            
            elif message_type == "chat_message":
                room_id = data.get("room_id")
                content = data.get("content")
                
                # 检查是否是AI命令
                if content.startswith("@AI") or content.startswith("@ai"):
                    # 处理AI命令
                    from app.services.ai_service import AIService
                    ai_service = AIService()
                    command = ai_service.parse_ai_command(content[3:].strip())
                    result = await ai_service.execute_command(command)
                    
                    # 发送AI响应
                    await manager.broadcast_to_room(
                        {
                            "type": "ai_response",
                            "content": result["response_text"],
                            "action": result["action"],
                            "data": result.get("data")
                        },
                        room_id
                    )
                else:
                    # 普通消息广播
                    await manager.broadcast_to_room(
                        {
                            "type": "chat_message",
                            "user_id": user_id,
                            "content": content
                        },
                        room_id
                    )
            
            elif message_type == "private_message":
                target_user_id = data.get("target_user_id")
                content = data.get("content")
                await manager.send_personal_message(
                    {
                        "type": "private_message",
                        "from_user_id": user_id,
                        "content": content
                    },
                    target_user_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)


# ==================== 健康检查 ====================

@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/", tags=["根路径"])
async def root():
    """根路径"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


# ==================== 启动入口 ====================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
