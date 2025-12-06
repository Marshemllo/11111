"""
数据库初始化脚本
使用 SQLAlchemy 创建所有表并插入初始数据
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from passlib.context import CryptContext
from datetime import datetime

from app.db.database import engine, SessionLocal, Base, init_db
from app.db.models import (
    User, Menu, AIEngine, InfoCategory, ChatRoom,
    DataSource, SpiderRule
)

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_tables():
    """创建所有表"""
    print("正在创建数据库表...")
    init_db()
    print("✓ 数据库表创建完成!")


def insert_default_admin():
    """插入默认管理员"""
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print("✓ 管理员用户已存在")
            return
        
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=pwd_context.hash("admin123"),
            nickname="系统管理员",
            role="admin",
            is_active=True,
            is_superuser=True
        )
        db.add(admin)
        db.commit()
        print("✓ 默认管理员创建成功 (用户名: admin, 密码: admin123)")
    except Exception as e:
        db.rollback()
        print(f"✗ 创建管理员失败: {e}")
    finally:
        db.close()


def insert_default_ai_engines():
    """插入默认AI引擎配置 - 硅基流动免费模型"""
    db = SessionLocal()
    try:
        # 硅基流动免费模型
        engines = [
            {
                "name": "DeepSeek-R1-0528-Qwen3-8B",
                "provider": "siliconflow",
                "api_key": "sk-vubzfajwqoaynjfkrkopjxbfbxdgzexlgujewuauvhavcqfl",
                "api_base_url": "https://api.siliconflow.cn/v1",
                "model_name": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
                "description": "DeepSeek R1 推理模型 (免费)",
                "max_tokens": 4096,
                "is_default": True
            },
            {
                "name": "Qwen2.5-7B-Instruct",
                "provider": "siliconflow",
                "api_key": "sk-vubzfajwqoaynjfkrkopjxbfbxdgzexlgujewuauvhavcqfl",
                "api_base_url": "https://api.siliconflow.cn/v1",
                "model_name": "Qwen/Qwen2.5-7B-Instruct",
                "description": "通义千问2.5 7B指令模型 (免费)",
                "max_tokens": 4096,
                "is_default": False
            },
            {
                "name": "GLM-4-9B-Chat",
                "provider": "siliconflow",
                "api_key": "sk-vubzfajwqoaynjfkrkopjxbfbxdgzexlgujewuauvhavcqfl",
                "api_base_url": "https://api.siliconflow.cn/v1",
                "model_name": "THUDM/glm-4-9b-chat",
                "description": "智谱GLM-4 9B对话模型 (免费)",
                "max_tokens": 4096,
                "is_default": False
            },
            {
                "name": "Qwen2.5-Coder-7B-Instruct",
                "provider": "siliconflow",
                "api_key": "sk-vubzfajwqoaynjfkrkopjxbfbxdgzexlgujewuauvhavcqfl",
                "api_base_url": "https://api.siliconflow.cn/v1",
                "model_name": "Qwen/Qwen2.5-Coder-7B-Instruct",
                "description": "通义千问2.5代码模型 (免费)",
                "max_tokens": 4096,
                "is_default": False
            },
            {
                "name": "InternLM2.5-7B-Chat",
                "provider": "siliconflow",
                "api_key": "sk-vubzfajwqoaynjfkrkopjxbfbxdgzexlgujewuauvhavcqfl",
                "api_base_url": "https://api.siliconflow.cn/v1",
                "model_name": "internlm/internlm2_5-7b-chat",
                "description": "书生浦语2.5 7B对话模型 (免费)",
                "max_tokens": 4096,
                "is_default": False
            },
            {
                "name": "Yi-1.5-6B-Chat",
                "provider": "siliconflow",
                "api_key": "sk-vubzfajwqoaynjfkrkopjxbfbxdgzexlgujewuauvhavcqfl",
                "api_base_url": "https://api.siliconflow.cn/v1",
                "model_name": "01-ai/Yi-1.5-6B-Chat",
                "description": "零一万物Yi 1.5 6B对话模型 (免费)",
                "max_tokens": 4096,
                "is_default": False
            }
        ]
        
        for engine_data in engines:
            existing = db.query(AIEngine).filter(AIEngine.name == engine_data["name"]).first()
            if not existing:
                engine = AIEngine(**engine_data)
                db.add(engine)
        
        db.commit()
        print("✓ AI引擎配置创建成功")
    except Exception as e:
        db.rollback()
        print(f"✗ 创建AI引擎配置失败: {e}")
    finally:
        db.close()


def insert_default_categories():
    """插入默认信息分类"""
    db = SessionLocal()
    try:
        categories = [
            {"name": "新闻资讯", "icon": "news", "sort_order": 1, "description": "各类新闻资讯"},
            {"name": "行业动态", "icon": "industry", "sort_order": 2, "description": "行业相关动态"},
            {"name": "政策法规", "icon": "policy", "sort_order": 3, "description": "政策法规信息"},
            {"name": "舆情监控", "icon": "monitor", "sort_order": 4, "description": "舆情监控数据"},
            {"name": "数据报告", "icon": "report", "sort_order": 5, "description": "数据分析报告"}
        ]
        
        for cat_data in categories:
            existing = db.query(InfoCategory).filter(InfoCategory.name == cat_data["name"]).first()
            if not existing:
                category = InfoCategory(**cat_data)
                db.add(category)
        
        db.commit()
        print("✓ 信息分类创建成功")
    except Exception as e:
        db.rollback()
        print(f"✗ 创建信息分类失败: {e}")
    finally:
        db.close()


def insert_default_menus():
    """插入默认菜单"""
    db = SessionLocal()
    try:
        menus = [
            {"name": "数据大屏", "path": "/dashboard", "component": "dashboard/index", "icon": "DataBoard", "sort_order": 1},
            {"name": "用户管理", "path": "/users", "component": "users/index", "icon": "User", "sort_order": 2},
            {"name": "菜单管理", "path": "/menus", "component": "menus/index", "icon": "Menu", "sort_order": 3},
            {"name": "爬虫管理", "path": "/spiders", "component": "spiders/index", "icon": "Connection", "sort_order": 4},
            {"name": "报告管理", "path": "/reports", "component": "reports/index", "icon": "Document", "sort_order": 5},
            {"name": "在线聊天", "path": "/chat", "component": "chat/index", "icon": "ChatDotRound", "sort_order": 6}
        ]
        
        for menu_data in menus:
            existing = db.query(Menu).filter(Menu.path == menu_data["path"]).first()
            if not existing:
                menu = Menu(**menu_data)
                db.add(menu)
        
        db.commit()
        print("✓ 默认菜单创建成功")
    except Exception as e:
        db.rollback()
        print(f"✗ 创建菜单失败: {e}")
    finally:
        db.close()


def insert_default_chatroom():
    """插入默认聊天室"""
    db = SessionLocal()
    try:
        existing = db.query(ChatRoom).filter(ChatRoom.name == "公共聊天室").first()
        if not existing:
            room = ChatRoom(
                name="公共聊天室",
                description="欢迎来到公共聊天室，可以使用@成小理与AI助手对话",
                room_type="group"
            )
            db.add(room)
            db.commit()
        print("✓ 默认聊天室创建成功")
    except Exception as e:
        db.rollback()
        print(f"✗ 创建聊天室失败: {e}")
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 50)
    print("智能数据分析平台 - 数据库初始化")
    print("=" * 50)
    print()
    
    # 1. 创建表
    create_tables()
    print()
    
    # 2. 插入初始数据
    print("正在插入初始数据...")
    insert_default_admin()
    insert_default_ai_engines()
    insert_default_categories()
    insert_default_menus()
    insert_default_chatroom()
    
    print()
    print("=" * 50)
    print("数据库初始化完成!")
    print("=" * 50)
    print()
    print("默认管理员账号:")
    print("  用户名: admin")
    print("  密码: admin123")
    print()


if __name__ == "__main__":
    main()
