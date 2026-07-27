#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目计划API - V2.2重构版"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List
from datetime import datetime, date
import os
import uuid

from app.database import get_db
from app.models.wbs_task import WbsTask
from app.models.user import User
from app.models.school import School
from app.models.task_attachment import TaskAttachment
from app.core.security import get_current_user

router = APIRouter()

# 佐证材料上传配置
UPLOAD_SUBDIR = os.path.join("uploads", "task_attachments")
UPLOAD_DIR = os.path.abspath(UPLOAD_SUBDIR)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
# 类型白名单(扩展名)
ALLOWED_EXTS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"
}


@router.get("/project-plan/summary")
def get_project_summary(
    current_user_id: Optional[int] = Query(None, description="当前用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取项目计划汇总数据（4个卡片）
    - 整体进度：按L4完成率计算
    - 进行中任务数
    - 已延期任务数
    - 我的任务数
    """
    # 基础查询：排除已删除
    query = db.query(WbsTask).filter(WbsTask.is_orphan == 0)

    # 总任务数（L4任务）
    l4_tasks = query.filter(WbsTask.work_content_l4 != "").all()
    total_l4 = len(l4_tasks)

    # 已完成的L4任务数
    completed_l4 = len([t for t in l4_tasks if t.status == '已完成'])

    # 整体进度 = 已完成L4 / 总L4
    overall_progress = round((completed_l4 / total_l4 * 100)) if total_l4 > 0 else 0

    # 进行中任务数
    doing_count = query.filter(WbsTask.status == '进行中').count()

    # 已延期任务数（计划结束日期 < 今天 且 状态不是已完成）
    today = date.today()
    delayed_count = query.filter(
        and_(
            WbsTask.plan_end_date < today,
            WbsTask.status != '已完成'
        )
    ).count()

    # 我的任务数
    my_tasks_count = 0
    if current_user_id:
        my_tasks_count = query.filter(
            WbsTask.responsible_person_id == current_user_id
        ).count()

    return {
        "overall_progress": overall_progress,
        "doing_count": doing_count,
        "delayed_count": delayed_count,
        "my_tasks_count": my_tasks_count
    }


@router.get("/project-plan/gantt")
def get_gantt_view(
    status: Optional[str] = Query(None),
    responsible_person_id: Optional[int] = Query(None),
    school_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, description="截止日期起(含),按plan_end_date过滤"),
    date_to: Optional[str] = Query(None, description="截止日期止(含),按plan_end_date过滤"),
    delayed: Optional[bool] = Query(None, description="筛选已延期任务(计划结束日期<今天且状态≠已完成)"),
    db: Session = Depends(get_db)
):
    """
    获取甘特图视图数据
    - 返回L1-L4层级结构
    - 包含时间轴信息
    """
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

    # 筛选条件
    if status:
        query = query.filter(WbsTask.status == status)
    if responsible_person_id:
        query = query.filter(WbsTask.responsible_person_id == responsible_person_id)
    if school_id:
        query = query.filter(WbsTask.school_id == school_id)
    if keyword:
        query = query.filter(
            or_(
                WbsTask.work_content_l4.like(f"%{keyword}%"),
                WbsTask.task_code.like(f"%{keyword}%")
            )
        )
    if date_from:
        query = query.filter(WbsTask.plan_end_date >= date_from)
    if date_to:
        query = query.filter(WbsTask.plan_end_date <= date_to)
    if delayed:
        today = date.today()
        query = query.filter(
            and_(
                WbsTask.plan_end_date < today,
                WbsTask.status != '已完成'
            )
        )

    # 排序：按L1-L4层级排序
    results = query.order_by(
        WbsTask.project_phase_l1,
        WbsTask.sub_phase_l2,
        WbsTask.task_package_l3,
        WbsTask.work_content_l4
    ).all()

    # 组装层级结构
    items = []
    for task, assignee_name, school_name in results:
        items.append({
            "id": task.id,
            "task_code": task.task_code,
            "level": _get_task_level(task),
            "l1": task.project_phase_l1,
            "l2": task.sub_phase_l2,
            "l3": task.task_package_l3,
            "l4": task.work_content_l4,
            "assignee_name": assignee_name or "",
            "school_name": school_name or "",
            "plan_start_date": task.plan_start_date.isoformat() if task.plan_start_date else None,
            "plan_end_date": task.plan_end_date.isoformat() if task.plan_end_date else None,
            "status": task.status,
            "priority": task.priority,
            "stage_type": task.stage_type or "",
            "progress_note": task.progress_note or "",
            "progress": task.progress if task.progress is not None else 0,
            "parent_id": task.parent_id
        })

    return {"items": items}


def _get_task_level(task: WbsTask) -> int:
    """判断任务层级(表无parent_id,按最深非空层级字段推算)"""
    if task.work_detail_l5:
        return 5
    elif task.work_content_l4:
        return 4
    elif task.task_package_l3:
        return 3
    elif task.sub_phase_l2:
        return 2
    else:
        return 1


def _task_path(task: WbsTask, level: int) -> tuple:
    """取任务从L1到指定层级的路径元组,用于父子关系匹配"""
    fields = [
        task.project_phase_l1 or "",
        task.sub_phase_l2 or "",
        task.task_package_l3 or "",
        task.work_content_l4 or "",
        task.work_detail_l5 or "",
    ]
    return tuple(fields[:level])


def _get_direct_children(task: WbsTask, db: Session) -> List[WbsTask]:
    """取某任务的直接子任务(level+1 且 L1..L(level)路径前缀一致,同建设年份)"""
    level = _get_task_level(task)
    if level >= 5:
        return []
    my_path = _task_path(task, level)
    candidates = db.query(WbsTask).filter(
        WbsTask.is_orphan == 0,
        WbsTask.construction_year == task.construction_year,
        WbsTask.id != task.id
    ).all()
    children = []
    for c in candidates:
        if _get_task_level(c) == level + 1 and _task_path(c, level) == my_path:
            children.append(c)
    return children


def _get_ancestors(task: WbsTask, db: Session) -> List[WbsTask]:
    """取某任务的所有祖先任务(由近到远),按层级路径前缀匹配"""
    level = _get_task_level(task)
    ancestors = []
    for anc_level in range(level - 1, 0, -1):
        anc_path = _task_path(task, anc_level)
        candidates = db.query(WbsTask).filter(
            WbsTask.is_orphan == 0,
            WbsTask.construction_year == task.construction_year,
            WbsTask.id != task.id
        ).all()
        for a in candidates:
            if _get_task_level(a) == anc_level and _task_path(a, anc_level) == anc_path:
                ancestors.append(a)
                break
    return ancestors


def _cascade_status_up(task: WbsTask, db: Session):
    """
    父子状态联动(设计§6.7.1),自底向上逐级传导:
    - 规则2: 子任务变"进行中" → 祖先若"待开始"自动变"进行中"
    - 规则3: 父任务全部直接子任务"已完成" → 父任务自动"已完成"
    - 规则4: 父任务全部直接子任务"待开始" → 父任务"待开始"
    """
    for ancestor in _get_ancestors(task, db):
        children = _get_direct_children(ancestor, db)
        if not children:
            continue
        child_statuses = [c.status for c in children]
        if all(s == '已完成' for s in child_statuses):
            ancestor.status = '已完成'
        elif all(s == '待开始' for s in child_statuses):
            ancestor.status = '待开始'
        elif any(s in ('进行中', '已完成', '待补材料', '已延期') for s in child_statuses):
            if ancestor.status == '待开始':
                ancestor.status = '进行中'


@router.get("/project-plan/list")
def get_list_view(
    status: Optional[str] = Query(None),
    responsible_person_id: Optional[int] = Query(None),
    school_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, description="截止日期起(含),按plan_end_date过滤"),
    date_to: Optional[str] = Query(None, description="截止日期止(含),按plan_end_date过滤"),
    delayed: Optional[bool] = Query(None, description="筛选已延期任务(计划结束日期<今天且状态≠已完成)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    获取列表视图数据
    - 层级列表展示
    - 支持分页
    """
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

    # 筛选条件
    if status:
        query = query.filter(WbsTask.status == status)
    if responsible_person_id:
        query = query.filter(WbsTask.responsible_person_id == responsible_person_id)
    if school_id:
        query = query.filter(WbsTask.school_id == school_id)
    if keyword:
        query = query.filter(
            or_(
                WbsTask.work_content_l4.like(f"%{keyword}%"),
                WbsTask.task_code.like(f"%{keyword}%")
            )
        )
    if date_from:
        query = query.filter(WbsTask.plan_end_date >= date_from)
    if date_to:
        query = query.filter(WbsTask.plan_end_date <= date_to)
    if delayed:
        today = date.today()
        query = query.filter(
            and_(
                WbsTask.plan_end_date < today,
                WbsTask.status != '已完成'
            )
        )

    # 总数
    total = query.count()

    # 分页
    offset = (page - 1) * page_size
    results = query.order_by(
        WbsTask.project_phase_l1,
        WbsTask.sub_phase_l2,
        WbsTask.task_package_l3,
        WbsTask.work_content_l4
    ).offset(offset).limit(page_size).all()

    # 组装
    items = []
    for task, assignee_name, school_name in results:
        items.append({
            "id": task.id,
            "task_code": task.task_code,
            "level": _get_task_level(task),
            "l1": task.project_phase_l1,
            "l2": task.sub_phase_l2,
            "l3": task.task_package_l3,
            "l4": task.work_content_l4,
            "assignee_name": assignee_name or "",
            "assignee_id": task.responsible_person_id,
            "school_name": school_name or "",
            "school_id": task.school_id,
            "plan_start_date": task.plan_start_date.isoformat() if task.plan_start_date else None,
            "plan_end_date": task.plan_end_date.isoformat() if task.plan_end_date else None,
            "actual_start_date": task.actual_start_date.isoformat() if task.actual_start_date else None,
            "actual_end_date": task.actual_end_date.isoformat() if task.actual_end_date else None,
            "status": task.status,
            "priority": task.priority,
            "stage_type": task.stage_type or "",
            "progress_note": task.progress_note or "",
            "progress": task.progress if task.progress is not None else 0,
            "parent_id": task.parent_id,
            "deliverables": task.deliverables or ""
        })

    return {"total": total, "items": items}


@router.get("/project-plan/kanban")
def get_kanban_view(
    responsible_person_id: Optional[int] = Query(None),
    school_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, description="截止日期起(含),按plan_end_date过滤"),
    date_to: Optional[str] = Query(None, description="截止日期止(含),按plan_end_date过滤"),
    db: Session = Depends(get_db)
):
    """
    获取看板视图数据
    - 按状态分列
    - 返回每列的任务卡片
    """
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

    # 筛选条件
    if responsible_person_id:
        query = query.filter(WbsTask.responsible_person_id == responsible_person_id)
    if school_id:
        query = query.filter(WbsTask.school_id == school_id)
    if keyword:
        query = query.filter(
            or_(
                WbsTask.work_content_l4.like(f"%{keyword}%"),
                WbsTask.task_code.like(f"%{keyword}%")
            )
        )
    if date_from:
        query = query.filter(WbsTask.plan_end_date >= date_from)
    if date_to:
        query = query.filter(WbsTask.plan_end_date <= date_to)

    results = query.all()

    # 按状态分组
    kanban_data = {
        "待开始": [],
        "进行中": [],
        "已完成": [],
        "已延期": [],
        "待补材料": []
    }

    today = date.today()

    for task, assignee_name, school_name in results:
        # 计算是否延期（计划结束日期 < 今天 且 未完成）
        is_delayed = (
            task.plan_end_date and
            task.plan_end_date < today and
            task.status != '已完成'
        )

        # 延期任务强制归入"已延期"列
        status_key = '已延期' if is_delayed else task.status

        card = {
            "id": task.id,
            "title": task.work_content_l4 or task.task_package_l3 or task.sub_phase_l2 or task.project_phase_l1,
            "parent": f"{task.project_phase_l1} / {task.sub_phase_l2}" if task.sub_phase_l2 else task.project_phase_l1,
            "assignee_name": assignee_name or "",
            "school_name": school_name or "",
            "is_delayed": is_delayed,
            "delay_days": (today - task.plan_end_date).days if is_delayed else 0
        }

        kanban_data[status_key].append(card)

    # 统计各状态数量
    return {
        "columns": {
            "待开始": {"count": len(kanban_data["待开始"]), "items": kanban_data["待开始"]},
            "进行中": {"count": len(kanban_data["进行中"]), "items": kanban_data["进行中"]},
            "已完成": {"count": len(kanban_data["已完成"]), "items": kanban_data["已完成"]},
            "已延期": {"count": len(kanban_data["已延期"]), "items": kanban_data["已延期"]},
            "待补材料": {"count": len(kanban_data["待补材料"]), "items": kanban_data["待补材料"]}
        }
    }


@router.get("/project-plan/tasks/{task_id}")
def get_task_detail(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取任务详情"""
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

    return {
        "id": task.id,
        "task_code": task.task_code,
        "construction_year": task.construction_year,
        "project_phase_l1": task.project_phase_l1,
        "sub_phase_l2": task.sub_phase_l2,
        "task_package_l3": task.task_package_l3,
        "work_content_l4": task.work_content_l4,
        "work_detail_l5": task.work_detail_l5,
        "priority": task.priority,
        "stage_type": task.stage_type or "",
        "status": task.status,
        "plan_start_date": task.plan_start_date.isoformat() if task.plan_start_date else None,
        "plan_end_date": task.plan_end_date.isoformat() if task.plan_end_date else None,
        "actual_start_date": task.actual_start_date.isoformat() if task.actual_start_date else None,
        "actual_end_date": task.actual_end_date.isoformat() if task.actual_end_date else None,
        "responsible_person_id": task.responsible_person_id,
        "assignee_name": assignee_name or "",
        "school_id": task.school_id,
        "school_name": school_name or "",
        "progress_note": task.progress_note or "",
        "progress": task.progress if task.progress is not None else 0,
        "parent_id": task.parent_id,
        "deliverables": task.deliverables or "",
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }


@router.post("/project-plan/tasks", status_code=201)
def create_task(
    task_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    新增任务（方案A：基于 parent_id 挂靠）
    - task_code 后台自动生成（无需前端传）
    - 父任务决定层级：子层级 = 父层级 + 1，并继承父的 L1-L(父层级) 路径
    - L1 任务 parent_id 为空
    """
    task_name = (task_data.get("task_name") or "").strip()
    if not task_name:
        raise HTTPException(status_code=400, detail="任务名称不能为空")

    parent_id = task_data.get("parent_id")
    parent = None
    if parent_id:
        parent = db.query(WbsTask).filter(
            WbsTask.id == parent_id, WbsTask.is_orphan == 0
        ).first()
        if not parent:
            raise HTTPException(status_code=400, detail="父任务不存在")

    # 计算层级与 L1-L5 路径字段
    parent_level = _get_task_level(parent) if parent else 0
    new_level = parent_level + 1
    if new_level > 5:
        raise HTTPException(status_code=400, detail="任务层级最多 5 级，该父任务已是最末级")

    # 继承父路径，本级填 task_name
    fields = {
        "project_phase_l1": parent.project_phase_l1 if parent else "",
        "sub_phase_l2": parent.sub_phase_l2 if parent else "",
        "task_package_l3": parent.task_package_l3 if parent else "",
        "work_content_l4": parent.work_content_l4 if parent else "",
        "work_detail_l5": parent.work_detail_l5 if parent else "",
    }
    level_field = {1: "project_phase_l1", 2: "sub_phase_l2", 3: "task_package_l3",
                   4: "work_content_l4", 5: "work_detail_l5"}[new_level]
    fields[level_field] = task_name

    # 建设年份：继承父任务，否则用前端传值或当前年
    construction_year = (parent.construction_year if parent
                         else task_data.get("construction_year") or str(date.today().year))

    # 自动生成唯一 task_code：WBS-AUTO-{最大序号+1}
    auto_code = _gen_task_code(db)

    new_task = WbsTask(
        task_code=auto_code,
        construction_year=construction_year,
        project_phase_l1=fields["project_phase_l1"],
        sub_phase_l2=fields["sub_phase_l2"],
        task_package_l3=fields["task_package_l3"],
        work_content_l4=fields["work_content_l4"],
        work_detail_l5=fields["work_detail_l5"],
        parent_id=parent_id or None,
        priority=task_data.get("priority", "中"),
        stage_type=task_data.get("stage_type"),
        status=task_data.get("status", "待开始"),
        progress=_clamp_progress(task_data.get("progress")),
        plan_start_date=task_data.get("plan_start_date"),
        plan_end_date=task_data.get("plan_end_date"),
        responsible_person_id=task_data.get("responsible_person_id"),
        school_id=task_data.get("school_id"),
        progress_note=task_data.get("progress_note", ""),
        deliverables=task_data.get("deliverables", "")
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"id": new_task.id, "message": "任务创建成功"}


def _clamp_progress(val) -> int:
    """进度归一到 0-100 整数，非法值归 0"""
    try:
        return max(0, min(100, int(val)))
    except (TypeError, ValueError):
        return 0


def _gen_task_code(db: Session) -> str:
    """生成唯一任务编码 WBS-AUTO-{序号}"""
    import re
    rows = db.query(WbsTask.task_code).filter(
        WbsTask.task_code.like("WBS-AUTO-%")
    ).all()
    max_n = 0
    for (code,) in rows:
        m = re.search(r"WBS-AUTO-(\d+)", code or "")
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"WBS-AUTO-{max_n + 1:04d}"


@router.put("/project-plan/tasks/{task_id}")
def update_task(
    task_id: int,
    task_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新任务
    - 支持部分字段更新
    - 父子任务联动规则
    """
    task = db.query(WbsTask).filter(
        WbsTask.id == task_id,
        WbsTask.is_orphan == 0
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 规则5: 父任务不可越级完成——有未完成直接子任务时禁止手动改为"已完成"
    new_status = task_data.get("status")
    if new_status == '已完成' and task.status != '已完成':
        children = _get_direct_children(task, db)
        unfinished = [c for c in children if c.status != '已完成']
        if unfinished:
            raise HTTPException(
                status_code=400,
                detail=f"该任务还有 {len(unfinished)} 个子任务未完成,不能直接标记为已完成"
            )

    status_changed = new_status is not None and new_status != task.status

    # 更新字段
    for key, value in task_data.items():
        if hasattr(task, key) and value is not None:
            setattr(task, key, value)

    # 状态变更 → 触发父子联动向上传导(规则2/3/4)
    if status_changed:
        _cascade_status_up(task, db)

    db.commit()
    db.refresh(task)

    return {"message": "任务更新成功", "id": task.id}


@router.delete("/project-plan/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除任务（软删除）
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


@router.post("/project-plan/tasks/batch")
def batch_update_tasks(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量操作(设计§6.4)
    - action=status: 批量更新状态(含越级完成拦截+父子联动)
    - action=assignee: 批量分配责任人
    - action=delete: 批量软删除
    payload: { task_ids: [int], action: str, value: any }
    """
    task_ids = payload.get("task_ids") or []
    action = payload.get("action")
    value = payload.get("value")

    if not task_ids:
        raise HTTPException(status_code=400, detail="未选择任务")
    if action not in ("status", "assignee", "delete"):
        raise HTTPException(status_code=400, detail="不支持的操作类型")

    tasks = db.query(WbsTask).filter(
        WbsTask.id.in_(task_ids),
        WbsTask.is_orphan == 0
    ).all()

    affected = 0
    skipped = []
    for task in tasks:
        if action == "delete":
            task.is_orphan = 1
            affected += 1
        elif action == "assignee":
            task.responsible_person_id = value
            affected += 1
        elif action == "status":
            # 越级完成拦截(规则5)
            if value == '已完成' and task.status != '已完成':
                children = _get_direct_children(task, db)
                if [c for c in children if c.status != '已完成']:
                    skipped.append(task.task_code)
                    continue
            changed = value != task.status
            task.status = value
            if changed:
                _cascade_status_up(task, db)
            affected += 1

    db.commit()
    result = {"message": "批量操作完成", "affected": affected}
    if skipped:
        result["skipped"] = skipped
        result["message"] = f"完成{affected}项,{len(skipped)}项因有未完成子任务被跳过"
    return result


@router.get("/project-plan/filters")
def get_filter_options(db: Session = Depends(get_db)):
    """
    获取筛选选项
    - 状态列表
    - 责任人列表
    - 学校列表
    """
    # 状态列表
    statuses = ['待开始', '进行中', '已完成', '已延期', '待补材料']

    # 责任人列表
    assignees = db.query(
        User.id,
        User.real_name
    ).filter(
        User.status == "启用"
    ).all()

    # 学校列表
    schools = db.query(
        School.id,
        School.full_name
    ).all()

    return {
        "statuses": statuses,
        "assignees": [{"id": a.id, "name": a.real_name} for a in assignees],
        "schools": [{"id": s.id, "name": s.full_name} for s in schools]
    }


@router.get("/project-plan/parent-options")
def get_parent_options(db: Session = Depends(get_db)):
    """
    可选父任务列表（新增任务表单下拉用）
    - 返回 L1-L4 任务（L5 已是最末级，不能作父）
    - label 带完整路径 + 层级，方便识别
    """
    tasks = db.query(WbsTask).filter(WbsTask.is_orphan == 0).order_by(
        WbsTask.project_phase_l1, WbsTask.sub_phase_l2,
        WbsTask.task_package_l3, WbsTask.work_content_l4
    ).all()

    options = []
    for t in tasks:
        level = _get_task_level(t)
        if level >= 5:
            continue  # L5 不能有子任务
        # 路径：本级及以上非空字段用 / 连接
        path_parts = [p for p in [
            t.project_phase_l1, t.sub_phase_l2, t.task_package_l3, t.work_content_l4
        ][:level] if p]
        options.append({
            "id": t.id,
            "level": level,
            "label": f"{' / '.join(path_parts)} (L{level})"
        })

    return {"items": options}


# ========== 佐证材料上传(设计§6.7.2 待补材料流转) ==========

@router.get("/project-plan/tasks/{task_id}/attachments")
def list_attachments(task_id: int, db: Session = Depends(get_db)):
    """获取任务的佐证材料列表"""
    task = db.query(WbsTask).filter(WbsTask.id == task_id, WbsTask.is_orphan == 0).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    rows = db.query(TaskAttachment).filter(
        TaskAttachment.task_id == task_id
    ).order_by(TaskAttachment.uploaded_at.desc()).all()

    return {
        "items": [
            {
                "id": a.id,
                "file_name": a.file_name,
                "file_url": f"/{a.file_path.replace(os.sep, '/')}",
                "file_size": a.file_size,
                "description": a.description or "",
                "uploaded_by": a.uploaded_by,
                "uploaded_at": a.uploaded_at.isoformat() if a.uploaded_at else None
            }
            for a in rows
        ]
    }


@router.post("/project-plan/tasks/{task_id}/attachments", status_code=201)
async def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    uploaded_by: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传佐证材料
    - 类型白名单 + 20MB 大小限制 + UUID 重命名(防路径穿越/覆盖)
    """
    task = db.query(WbsTask).filter(WbsTask.id == task_id, WbsTask.is_orphan == 0).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 类型白名单校验(按扩展名)
    orig_name = file.filename or "unnamed"
    ext = os.path.splitext(orig_name)[1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型 {ext},仅允许 PDF/Office文档/图片"
        )

    # 读取内容并校验大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件超过 20MB 限制")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="文件为空")

    # UUID 重命名,只保留扩展名 → 杜绝原始文件名带来的路径穿越/覆盖
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(abs_path, "wb") as f:
        f.write(content)

    # 相对路径入库(供 StaticFiles 提供访问)
    rel_path = os.path.join(UPLOAD_SUBDIR, stored_name)
    attachment = TaskAttachment(
        task_id=task_id,
        file_name=orig_name,
        file_path=rel_path,
        file_size=len(content),
        description=description,
        uploaded_by=uploaded_by
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return {
        "id": attachment.id,
        "file_name": attachment.file_name,
        "file_url": f"/{rel_path.replace(os.sep, '/')}",
        "message": "上传成功"
    }


@router.delete("/project-plan/attachments/{attachment_id}", status_code=204)
def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除佐证材料(同时删除物理文件)"""
    attachment = db.query(TaskAttachment).filter(
        TaskAttachment.id == attachment_id
    ).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="材料不存在")

    # 删除物理文件(不存在则忽略)
    abs_path = os.path.abspath(attachment.file_path)
    if os.path.isfile(abs_path):
        try:
            os.remove(abs_path)
        except OSError:
            pass

    db.delete(attachment)
    db.commit()
    return None
