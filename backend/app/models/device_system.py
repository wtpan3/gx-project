from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.database import Base

class DeviceSystem(Base):
    __tablename__ = "device_systems"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100))
    construction_year = Column(Integer)
    system_name = Column(String(100))
    device_name = Column(String(100))
    brand = Column(String(100))
    model = Column(String(100))
    params = Column(Text)
    type = Column(Enum('硬件', '软件', '其他'))
    unit = Column(String(20))
    plan_quantity = Column(Integer)
    is_enabled = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
