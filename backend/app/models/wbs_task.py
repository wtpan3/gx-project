from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Date, Text
from sqlalchemy.sql import func
from app.database import Base

class WBSTask(Base):
    __tablename__ = "wbs_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_code = Column(String(50))
    task_name = Column(String(200), nullable=False)
    parent_id = Column(Integer, ForeignKey('wbs_tasks.id'))
    level = Column(Integer)
    phase = Column(String(50))
    assignee_id = Column(Integer, ForeignKey('users.id'))
    plan_start_date = Column(Date)
    plan_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    status = Column(Enum('未开始', '进行中', '已完成', '已延期', '已取消'))
    progress = Column(Integer, default=0)
    deliverables = Column(String(255))
    school_id = Column(Integer, ForeignKey('schools.id'))
    source_device_id = Column(Integer)
    construction_year = Column(Integer)
    is_orphan = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
