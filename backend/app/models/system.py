from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base

class System(Base):
    """系统字典表 - 系统归属产线, 设备归属系统"""
    __tablename__ = "systems"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('project_info.id'), nullable=False, default=1)
    name = Column(String(100), nullable=False)
    production_line_id = Column(Integer, ForeignKey('production_lines.id'))
    description = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('project_id', 'name', name='uq_systems_project_name'),
    )
