from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Date
from sqlalchemy.sql import func
from app.database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100))
    construction_year = Column(Integer)
    system_id = Column(Integer, ForeignKey('device_systems.id'))
    device_name = Column(String(100))
    brand = Column(String(100))
    model = Column(String(100))
    params = Column(Text)
    type = Column(Enum('硬件', '软件', '其他'))
    unit = Column(String(20))
    source = Column(Enum('三方外采', '库存设备'))
    quantity = Column(Integer)
    school_id = Column(Integer, ForeignKey('schools.id'))
    install_location = Column(String(100))
    status = Column(Enum('待发货', '已到货', '已安装', '已调试', '运行中'))
    supplier_id = Column(Integer)
    plan_arrival_date = Column(Date)
    delivery_no = Column(String(50))
    delivery_date = Column(Date)
    arrival_date = Column(Date)
    install_date = Column(Date)  # 修正:对齐数据库列名(原 installation_date)
    debug_date = Column(Date)    # 修正:对齐数据库列名(原 debugging_date)
    accept_date = Column(Date)   # 修正:对齐数据库列名(原 acceptance_date)
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
