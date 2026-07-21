#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WBS任务相关的Pydantic模型"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, validator


class WbsTaskBase(BaseModel):
    """WBS任务基础模型"""
    construction_year: str = Field(..., description="建设年份")
    project_phase_l1: str = Field(..., description="L1项目阶段")
    sub_phase_l2: str = Field(..., description="L2子阶段")
    task_package_l3: str = Field(..., description="L3任务包")
    work_content_l4: str = Field(..., description="L4工作内容")
    work_detail_l5: Optional[str] = Field(None, description="L5工作明细")

    task_code: str = Field(..., description="任务编码（唯一）")
    priority: str = Field("中", description="优先级：高/中/低")
    status: str = Field("待开始", description="状态：待开始/进行中/已完成/已暂停")

    plan_start_date: Optional[date] = Field(None, description="计划开始日期")
    plan_end_date: Optional[date] = Field(None, description="计划完成日期")
    actual_start_date: Optional[date] = Field(None, description="实际开始日期")
    actual_end_date: Optional[date] = Field(None, description="实际完成日期")

    responsible_person_id: Optional[int] = Field(None, description="责任人ID")
    school_id: Optional[int] = Field(None, description="关联学校ID")

    progress_note: Optional[str] = Field(None, description="进度说明")
    deliverables: Optional[str] = Field(None, description="交付物")


class WbsTaskCreate(WbsTaskBase):
    """创建WBS任务"""
    pass


class WbsTaskUpdate(BaseModel):
    """更新WBS任务（所有字段可选）"""
    construction_year: Optional[str] = None
    project_phase_l1: Optional[str] = None
    sub_phase_l2: Optional[str] = None
    task_package_l3: Optional[str] = None
    work_content_l4: Optional[str] = None
    work_detail_l5: Optional[str] = None

    task_code: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

    plan_start_date: Optional[date] = None
    plan_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None

    responsible_person_id: Optional[int] = None
    school_id: Optional[int] = None

    progress_note: Optional[str] = None
    deliverables: Optional[str] = None


class WbsTaskResponse(WbsTaskBase):
    """WBS任务响应模型"""
    id: int
    assignee_name: Optional[str] = Field(None, description="责任人姓名")
    school_name: Optional[str] = Field(None, description="学校全称")

    is_orphan: int = Field(0, description="是否删除：0正常/1已删除")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WbsTaskListResponse(BaseModel):
    """WBS任务列表分页响应"""
    total: int = Field(..., description="总记录数")
    items: list[WbsTaskResponse] = Field(..., description="任务列表")
