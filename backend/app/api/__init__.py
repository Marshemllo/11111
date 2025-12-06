# API Package
from fastapi import APIRouter

api_router = APIRouter()

# 导入所有端点路由
from app.api.endpoints import user, menu, spider, report, dashboard, chat

api_router.include_router(user.router, prefix="/users", tags=["用户管理"])
api_router.include_router(menu.router, prefix="/menus", tags=["菜单管理"])
api_router.include_router(spider.router, prefix="/spiders", tags=["爬虫管理"])
api_router.include_router(report.router, prefix="/reports", tags=["报告管理"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["数据大屏"])
api_router.include_router(chat.router, prefix="/chat", tags=["在线聊天"])
