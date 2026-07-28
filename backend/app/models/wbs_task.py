from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Date, Text
from sqlalchemy.sql import func
from app.database import Base

class WbsTask(Base):
    __tablename__ = "wbs_tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('project_info.id'), nullable=False)
    task_code = Column(String(50), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('wbs_tasks.id'), nullable=True)
    project_phase_l1 = Column(String(50), nullable=False)
    sub_phase_l2 = Column(String(50), nullable=False)
    task_package_l3 = Column(String(100), nullable=False)
    work_content_l4 = Column(String(200), nullable=False)
    work_detail_l5 = Column(String(200))

    priority = Column(Enum('高', '中', '低'), nullable=False)
    stage_type = Column(Enum('到货验收', '加电测试', '校级验收', '培训', '无'), nullable=True)
    status = Column(Enum('待开始', '进行中', '已完成', '已延期', '待补材料'), nullable=False, default='待开始')

    plan_start_date = Column(Date, nullable=False)
    plan_end_date = Column(Date, nullable=False)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)

    responsible_person_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    source_device_id = Column(Integer, ForeignKey('devices.id'), nullable=True)
    construction_year = Column(Integer, nullable=True)

    progress_note = Column(Text)
    deliverables = Column(String(255))

    is_orphan = Column(Integer, default=0)
    requires_material = Column(Integer, default=0)
    material_status = Column(Enum('无要求', '待上传', '部分上传', '已完成'), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# 兼容旧代码的别名
WBSTask = WbsTask
