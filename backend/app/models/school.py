from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50))
    full_name = Column(String(200), nullable=False)
    region = Column(String(100))
    address = Column(String(255))
    campus_manager_id = Column(Integer, ForeignKey('users.id'))
    contact_person = Column(String(50))
    contact_phone = Column(String(20))
    project_status = Column(Enum('未启动', '实施中', '已完成', '已验收', '维护中'))
    remark = Column(Text)
    is_key = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
