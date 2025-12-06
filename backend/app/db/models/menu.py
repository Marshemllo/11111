"""
菜单模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Menu(Base):
    """菜单表"""
    __tablename__ = "menus"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="菜单名称")
    path = Column(String(100), nullable=True, comment="路由路径")
    component = Column(String(100), nullable=True, comment="组件路径")
    icon = Column(String(50), nullable=True, comment="图标名称")
    parent_id = Column(Integer, ForeignKey("menus.id"), nullable=True, comment="父菜单ID")
    order_num = Column(Integer, default=0, comment="排序号")
    permission = Column(String(100), nullable=True, comment="权限标识")
    menu_type = Column(String(10), default="menu", comment="类型: menu/button")
    is_visible = Column(Boolean, default=True, comment="是否可见")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 自引用关系
    children = relationship("Menu", backref="parent", remote_side=[id])
    
    def __repr__(self):
        return f"<Menu(id={self.id}, name={self.name})>"
