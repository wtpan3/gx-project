from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class TaskAttachment(Base):
    """任务佐证材料"""
    __tablename__ = "task_attachments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('wbs_tasks.id'), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)   # 原始文件名
    file_path = Column(String(500), nullable=False)   # 存储路径(相对 uploads)
    file_size = Column(Integer)                        # 字节
    description = Column(String(500))                  # 材料说明
    uploaded_by = Column(Integer)                      # 上传人ID
    uploaded_at = Column(DateTime, server_default=func.now())
