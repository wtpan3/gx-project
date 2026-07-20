from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Date, Text
from sqlalchemy.sql import func
from app.database import Base

class WBSTask(Base):
    __tablename__ = "wbs_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_code = Column(String(50), nullable=False)
    project_phase_l1 = Column(String(50), nullable=False)
    sub_phase_l2 = Column(String(50), nullable=False)
    task_package_l3 = Column(String(100), nullable=False)
    work_content_l4 = Column(String(200), nullable=False)
    work_detail_l5 = Column(String(200))
    stage_type = Column(String(50))
    plan_start_date = Column(Date, nullable=False)
    plan_end_date = Column(Date, nullable=False)
    status = Column(Enum('待开始', '进行中', '已完成', '已延期', '待补材料'), nullable=False)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    assignee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    progress_note = Column(Text)
    deliverables = Column(String(255))
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    source_device_id = Column(Integer)
    construction_year = Column(Integer)
    is_orphan = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
