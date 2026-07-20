from sqlalchemy import Column, Integer, String, DateTime, Date, Decimal, Text
from sqlalchemy.sql import func
from app.database import Base

class ProjectInfo(Base):
    __tablename__ = "project_info"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(200), nullable=False)
    project_code = Column(String(50), unique=True, nullable=False)
    construction_year = Column(Integer)
    budget = Column(Decimal(15, 2))
    contract_amount = Column(Decimal(15, 2))
    start_date = Column(Date)
    plan_end_date = Column(Date)
    actual_end_date = Column(Date)
    project_manager = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
