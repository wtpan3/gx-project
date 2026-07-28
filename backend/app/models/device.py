from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Date
from sqlalchemy.sql import func
from app.database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('project_info.id'), nullable=False)
    project_name = Column(String(100), nullable=False)
    construction_year = Column(Integer, nullable=False)
    system_name = Column(String(100))
    device_name = Column(String(100), nullable=False)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    params = Column(Text)
    type = Column(Enum('硬件', '软件', '其他'), nullable=False)
    unit = Column(String(20), nullable=False)
    source = Column(Enum('三方外采', '库存设备'), nullable=False)
    quantity = Column(Integer, nullable=False)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    install_location = Column(String(100))
    status = Column(Enum('待发货', '已到货', '已安装', '已调试', '运行中'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    plan_arrival_date = Column(Date, nullable=False)
    delivery_no = Column(String(50))
    delivery_date = Column(Date)
    arrival_date = Column(Date)
    install_date = Column(Date)
    debug_date = Column(Date)
    accept_date = Column(Date)
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
