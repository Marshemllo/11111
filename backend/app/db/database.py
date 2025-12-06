"""
数据库连接配置
使用SQLAlchemy ORM连接MySQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 连接池预检
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 最大溢出连接数
    echo=settings.DEBUG  # 调试模式下打印SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话依赖项
    
    用于FastAPI依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    获取数据库会话上下文管理器
    
    用于非FastAPI场景（如爬虫、后台任务）
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    
    创建所有表结构
    """
    # 导入所有模型以确保它们被注册
    from app.db.models import User, Menu, SpiderRule, DataSource, Report, ChatMessage, ChatRoom
    
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    删除所有表（仅用于测试）
    """
    Base.metadata.drop_all(bind=engine)
