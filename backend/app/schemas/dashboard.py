"""Dashboard 接口响应 Pydantic 模型"""
from typing import List, Optional
from datetime import date
from pydantic import BaseModel


# ===== 顶部卡片 =====
class StatCard(BaseModel):
    label: str
    value: int
    unit: str
    badge_red: bool = False  # 重点学校红色标记


# ===== 交付进度 =====
class ProgressItem(BaseModel):
    label: str
    count: int
    color: str


class SoftwareModuleProgress(BaseModel):
    name: str
    phase: str
    progress: int


class DeliveryProgress(BaseModel):
    overall_progress: int  # 项目整体进度百分比
    school_progress: List[ProgressItem]
    school_completed: int
    school_total: int
    hardware_progress: List[ProgressItem]
    hardware_completed: int
    hardware_total: int
    software_modules: List[SoftwareModuleProgress]


# ===== 里程碑 =====
class Milestone(BaseModel):
    phase: str
    task: str
    plan_start_date: Optional[date]
    plan_end_date: Optional[date]
    status: str


# ===== 风险 =====
class RiskItem(BaseModel):
    id: int
    risk_level: str
    description: str
    impact: Optional[str]
    response_plan: Optional[str]
    owner_name: Optional[str]
    registered_at: Optional[date]
    plan_close_date: Optional[date]
    status: str


# ===== 待办 =====
class TodoItem(BaseModel):
    id: int
    task_name: str
    priority: str
    assignee_name: Optional[str]  # 项目待办有,我的待办无
    plan_end_date: Optional[date]
    status: str


# ===== 总览响应 =====
class DashboardOverview(BaseModel):
    stat_cards: List[StatCard]
    delivery_progress: DeliveryProgress
    milestones: List[Milestone]
    risks: List[RiskItem]