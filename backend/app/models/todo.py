from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(Enum('高', '中', '低'), default='中')
    due_date = Column(Date)
    status = Column(Enum('待处理', '已完成'), default='待处理')
    assignee_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    creator_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    source_type = Column(Enum('project', 'wbs', 'system'), default='project')
    source_id = Column(Integer)
    transferred_from = Column(Integer)
    parent_id = Column(Integer, ForeignKey('todos.id', ondelete='CASCADE'))
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系（可选，方便查询）
    assignee = relationship("User", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[creator_id])

    # 树形结构自关联
    parent = relationship("Todo", remote_side=[id], foreign_keys=[parent_id], backref="children")
