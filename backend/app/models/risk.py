from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Date, Text
from sqlalchemy.sql import func
from app.database import Base

class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    risk_desc = Column(Text)
    trigger_condition = Column(Text)
    impact_description = Column(Text)
    probability = Column(Enum('高', '中', '低'))
    impact = Column(Enum('高', '中', '低'))
    risk_level = Column(Enum('高', '中', '低'))
    response_strategy = Column(Text)
    response_deadline = Column(Date)
    responsible_person_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum('已识别', '应对中', '已关闭'))
    school_id = Column(Integer, ForeignKey('schools.id'))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
