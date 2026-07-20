"""Dashboard 首页接口"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardOverview, TodoItem

router = APIRouter()


@router.get('/overview', response_model=DashboardOverview)
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取首页总览数据(卡片+进度+里程碑+风险)"""
    return DashboardService.get_overview(db)


@router.get('/todos', response_model=list[TodoItem])
def get_todos(
    scope: str = Query('project', regex='^(project|mine)$'),
    range: str = Query('week', regex='^(week|month|today)$', alias='range'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取待办任务(项目待办/我的待办,按时间范围筛选)"""
    return DashboardService.get_todos(
        db=db,
        scope=scope,
        range_filter=range,
        current_user_id=current_user.id if scope == 'mine' else None
    )
