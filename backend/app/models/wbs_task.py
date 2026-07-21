from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Date, Text
from sqlalchemy.sql import func
from app.database import Base

class WbsTask(Base):
    __tablename__ = "wbs_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_code = Column(String(50), nullable=False, unique=True)
    construction_year = Column(String(10), nullable=False)
    project_phase_l1 = Column(String(50), nullable=False)
    sub_phase_l2 = Column(String(50), nullable=False)
    task_package_l3 = Column(String(100), nullable=False)
    work_content_l4 = Column(String(200), nullable=False)
    work_detail_l5 = Column(String(200))

    priority = Column(Enum('高', '中', '低'), nullable=False, default='中')
    status = Column(Enum('待开始', '进行中', '已完成', '已延期', '待补材料'), nullable=False, default='待开始')

    plan_start_date = Column(Date)
    plan_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)

    responsible_person_id = Column(Integer, ForeignKey('users.id'))
    school_id = Column(Integer, ForeignKey('schools.id'))

    progress_note = Column(Text)
    deliverables = Column(String(255))

    is_orphan = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# 兼容旧代码的别名
WBSTask = WbsTask
