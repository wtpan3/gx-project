from sqlalchemy import Column, Integer, String, DateTime, Enum, Date
from sqlalchemy.sql import func
from app.database import Base

class SoftwareModule(Base):
    __tablename__ = "software_modules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phase = Column(Enum('需求收集', '需求确认', '软件开发', '软件测试', '软件部署', '上线运行'), nullable=False)
    progress = Column(Integer, default=0)
    expected_completion_date = Column(Date)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
