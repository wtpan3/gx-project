from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Date, Text
from sqlalchemy.sql import func
from app.database import Base

class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('project_info.id'), nullable=False, comment='所属项目')
    risk_desc = Column(Text, comment='风险描述')
    trigger_condition = Column(Text, comment='触发条件')
    impact_description = Column(Text, comment='影响描述')
    risk_level = Column(Enum('高', '中', '低'), comment='风险等级（手工评定）')
    response_strategy = Column(Text, comment='应对措施')
    progress_note = Column(Text, comment='进展说明（自由文本）')
    responsible_person_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum('已识别', '应对中', '已关闭'), comment='风险状态')
    school_id = Column(Integer, ForeignKey('schools.id'))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
