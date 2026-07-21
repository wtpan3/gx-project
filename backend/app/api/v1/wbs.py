#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WBS任务管理API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional

from app.database import get_db
from app.schemas.wbs_task import (
    WbsTaskCreate,
    WbsTaskUpdate,
    WbsTaskResponse,
    WbsTaskListResponse
)
from app.models.wbs_task import WbsTask
from app.models.user import User
from app.models.school import School

router = APIRouter()


@router.get("/wbs-tasks", response_model=WbsTaskListResponse)
def get_wbs_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="L4关键词搜索"),
    db: Session = Depends(get_db)
):
    """
    获取WBS任务列表
    - 支持分页
    - 支持状态筛选（首页下钻）
    - 支持L4工作内容关键词搜索
    """
    # 基础查询：排除已删除
    query = db.query(
        WbsTask,
        User.real_name.label("assignee_name"),
        School.full_name.label("school_name")
    ).outerjoin(
        User, WbsTask.responsible_person_id == User.id
    ).outerjoin(
        School, WbsTask.school_id == School.id
    ).filter(
        WbsTask.is_orphan == 0
    )

    # 状态筛选
    if status:
        query = query.filter(WbsTask.status == status)

    # 关键词搜索（L4）
    if keyword:
        query = query.filter(WbsTask.work_content_l4.like(f"%{keyword}%"))

    # 总数统计
    total = query.count()

    # 分页
    offset = (page - 1) * page_size
    results = query.order_by(WbsTask.id.desc()).offset(offset).limit(page_size).all()

    # 组装响应
    items = []
    for task, assignee_name, school_name in results:
        task_dict = {
            **task.__dict__,
            "assignee_name": assignee_name,
            "school_name": school_name
        }
        items.append(WbsTaskResponse(**task_dict))

    return WbsTaskListResponse(total=total, items=items)


@router.get("/wbs-tasks/{task_id}", response_model=WbsTaskResponse)
def get_wbs_task_detail(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取WBS任务详情"""
    result = db.query(
        WbsTask,
        User.real_name.label("assignee_name"),
        School.full_name.label("school_name")
    ).outerjoin(
        User, WbsTask.responsible_person_id == User.id
    ).outerjoin(
        School, WbsTask.school_id == School.id
    ).filter(
        WbsTask.id == task_id,
        WbsTask.is_orphan == 0
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="任务不存在")

    task, assignee_name, school_name = result
    task_dict = {
        **task.__dict__,
        "assignee_name": assignee_name,
        "school_name": school_name
    }

    return WbsTaskResponse(**task_dict)


@router.post("/wbs-tasks", response_model=WbsTaskResponse, status_code=201)
def create_wbs_task(
    task_data: WbsTaskCreate,
    db: Session = Depends(get_db)
):
    """
    新增WBS任务
    - 校验task_code唯一性
    """
    # 检查task_code是否已存在
    exists = db.query(WbsTask).filter(
        WbsTask.task_code == task_data.task_code,
        WbsTask.is_orphan == 0
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail=f"任务编码 {task_data.task_code} 已存在")

    # 创建任务
    new_task = WbsTask(**task_data.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # 返回详情（包含关联信息）
    return get_wbs_task_detail(new_task.id, db)


@router.put("/wbs-tasks/{task_id}", response_model=WbsTaskResponse)
def update_wbs_task(
    task_id: int,
    task_data: WbsTaskUpdate,
    db: Session = Depends(get_db)
):
    """编辑WBS任务"""
    task = db.query(WbsTask).filter(
        WbsTask.id == task_id,
        WbsTask.is_orphan == 0
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 如果修改了task_code，检查唯一性
    if task_data.task_code and task_data.task_code != task.task_code:
        exists = db.query(WbsTask).filter(
            WbsTask.task_code == task_data.task_code,
            WbsTask.is_orphan == 0,
            WbsTask.id != task_id
        ).first()

        if exists:
            raise HTTPException(status_code=400, detail=f"任务编码 {task_data.task_code} 已被其他任务使用")

    # 更新字段（仅更新非None的字段）
    update_data = task_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    # 返回详情
    return get_wbs_task_detail(task_id, db)


@router.delete("/wbs-tasks/{task_id}", status_code=204)
def delete_wbs_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    删除WBS任务（软删除）
    - 标记 is_orphan = 1
    """
    task = db.query(WbsTask).filter(
        WbsTask.id == task_id,
        WbsTask.is_orphan == 0
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.is_orphan = 1
    db.commit()

    return None
