"""Dashboard 数据聚合服务"""
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.school import School
from app.models.device_system import DeviceSystem
from app.models.device import Device
from app.models.wbs_task import WbsTask
from app.models.risk import Risk
from app.models.production_line import ProductionLine
from app.models.software_module import SoftwareModule
from app.models.user import User
from app.schemas.dashboard import (
    StatCard, DeliveryProgress, ProgressItem, SoftwareModuleProgress,
    Milestone, RiskItem, TodoItem, DashboardOverview
)


class DashboardService:
    """首页数据聚合"""

    @staticmethod
    def get_overview(db: Session) -> DashboardOverview:
        """获取首页总览数据"""
        return DashboardOverview(
            stat_cards=DashboardService._get_stat_cards(db),
            delivery_progress=DashboardService._get_delivery_progress(db),
            milestones=DashboardService._get_milestones(db),
            risks=DashboardService._get_risks(db)
        )

    @staticmethod
    def _get_stat_cards(db: Session) -> List[StatCard]:
        """7个顶部卡片统计"""
        total_schools = db.query(School).count()
        priority_schools = db.query(School).filter(School.is_key == True).count()
        total_systems = db.query(DeviceSystem).count()
        device_types_count = db.query(func.count(func.distinct(Device.device_name))).scalar() or 0
        production_lines_count = db.query(ProductionLine).filter(ProductionLine.is_enabled == 1).count()
        external_devices_count = db.query(func.count(func.distinct(Device.device_name))).filter(
            Device.source == '三方外采'
        ).scalar() or 0
        total_devices = db.query(func.sum(Device.quantity)).scalar() or 0

        return [
            StatCard(label='覆盖学校', value=total_schools, unit='所', badge_red=False),
            StatCard(label='重点学校', value=priority_schools, unit='所', badge_red=True),
            StatCard(label='系统总数', value=total_systems, unit='个', badge_red=False),
            StatCard(label='设备类型', value=device_types_count, unit='种', badge_red=False),
            StatCard(label='产线类型', value=production_lines_count, unit='种', badge_red=False),
            StatCard(label='外采设备', value=external_devices_count, unit='种', badge_red=False),
            StatCard(label='硬件总数', value=total_devices, unit='台', badge_red=False),
        ]

    @staticmethod
    def _get_delivery_progress(db: Session) -> DeliveryProgress:
        """交付进度:学校/硬件/软件"""
        # 学校进度(按状态分组统计 - 从WBS任务推导学校完成度)
        total_schools = db.query(School).count()
        # 简化:已完成学校 = 该校所有末级任务(level=3)均为已完成
        completed_schools = 0  # 需复杂SQL子查询,此处演示数据由seed提供,实际可优化
        school_progress = [
            ProgressItem(label='已完成', count=completed_schools, color='#52c41a'),
            ProgressItem(label='装修中', count=3, color='#722ed1'),
            ProgressItem(label='安装中', count=2, color='#fa8c16'),
            ProgressItem(label='调试中', count=0, color='#1677ff'),
            ProgressItem(label='培训中', count=0, color='#faad14'),
            ProgressItem(label='待启动', count=total_schools - completed_schools - 5, color='#8c8c8c'),
        ]

        # 硬件进度(按设备状态分组)
        total_devices = db.query(func.sum(Device.quantity)).scalar() or 0
        status_counts = db.query(Device.status, func.sum(Device.quantity)).group_by(Device.status).all()
        status_map = {s: (c or 0) for s, c in status_counts}
        hardware_progress = [
            ProgressItem(label='待发货', count=status_map.get('待发货', 0), color='#d9d9d9'),
            ProgressItem(label='已到货', count=status_map.get('已到货', 0), color='#1677ff'),
            ProgressItem(label='已安装', count=status_map.get('已安装', 0), color='#13c2c2'),
            ProgressItem(label='已调试', count=status_map.get('已调试', 0), color='#fa8c16'),
            ProgressItem(label='运行中', count=status_map.get('运行中', 0), color='#52c41a'),
        ]

        # 软件模块进度
        modules = db.query(SoftwareModule).order_by(SoftwareModule.sort_order).all()
        software_modules = [
            SoftwareModuleProgress(name=m.name, phase=m.phase, progress=m.progress)
            for m in modules
        ]

        # 整体进度(已完成末级任务数 / 总末级任务数,以work_content_l4为末级)
        total_tasks = db.query(WbsTask).filter(WbsTask.work_content_l4 != '').count()
        completed_tasks = db.query(WbsTask).filter(
            WbsTask.work_content_l4 != '',
            WbsTask.status == '已完成'
        ).count()
        overall_progress = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)

        return DeliveryProgress(
            overall_progress=overall_progress,
            school_progress=school_progress,
            school_completed=completed_schools,
            school_total=total_schools,
            hardware_progress=hardware_progress,
            hardware_completed=status_map.get('运行中', 0),
            hardware_total=total_devices,
            software_modules=software_modules
        )

    @staticmethod
    def _get_milestones(db: Session) -> List[Milestone]:
        """关键里程碑(取L2子阶段任务,按计划开始时间排序,最多展示4条)"""
        tasks = db.query(WbsTask).filter(
            WbsTask.sub_phase_l2 != ''
        ).order_by(WbsTask.plan_start_date).limit(4).all()

        return [
            Milestone(
                phase=t.project_phase_l1 or '',
                task=t.sub_phase_l2,
                plan_start_date=t.plan_start_date,
                plan_end_date=t.plan_end_date,
                status=t.status
            ) for t in tasks
        ]

    @staticmethod
    def _get_risks(db: Session) -> List[RiskItem]:
        """项目风险(仅活跃风险:状态≠已关闭,按等级+状态+响应期限排序,最多8条)"""
        risks = db.query(Risk, User.real_name).outerjoin(
            User, Risk.responsible_person_id == User.id
        ).filter(
            Risk.status != '已关闭'
        ).order_by(
            # 高→中→低
            func.field(Risk.risk_level, '高', '中', '低'),
            # 应对中→已识别
            func.field(Risk.status, '应对中', '已识别'),
            # 响应期限升序
            Risk.response_deadline
        ).limit(8).all()

        return [
            RiskItem(
                id=r.Risk.id,
                risk_level=r.Risk.risk_level,
                description=r.Risk.risk_desc or '',
                impact=r.Risk.impact_description,
                response_plan=r.Risk.response_strategy,
                owner_name=r.real_name,
                registered_at=r.Risk.created_at.date() if r.Risk.created_at else None,
                plan_close_date=r.Risk.response_deadline,
                status=r.Risk.status
            ) for r in risks
        ]

    @staticmethod
    def get_todos(
        db: Session,
        scope: str,  # 'project' | 'mine'
        range_filter: str,  # 'week' | 'month' | 'today'
        current_user_id: Optional[int] = None
    ) -> List[TodoItem]:
        """待办任务查询(按截止日期范围筛选,默认本周)"""
        # 时间范围
        today = date.today()
        if range_filter == 'today':
            start_date, end_date = today, today
        elif range_filter == 'week':
            # 本周一到周日
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        else:  # month
            start_date = today.replace(day=1)
            next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_date = next_month - timedelta(days=1)

        # 基础查询:末级任务(work_content_l4不为空) + 未完成状态
        query = db.query(WbsTask, User.real_name).outerjoin(
            User, WbsTask.responsible_person_id == User.id
        ).filter(
            WbsTask.work_content_l4 != '',
            WbsTask.status.in_(['待开始', '进行中', '已延期']),
            WbsTask.plan_end_date >= start_date,
            WbsTask.plan_end_date <= end_date
        )

        # scope筛选
        if scope == 'mine' and current_user_id:
            query = query.filter(WbsTask.responsible_person_id == current_user_id)

        # 排序:截止日期升序
        tasks = query.order_by(WbsTask.plan_end_date).all()

        return [
            TodoItem(
                id=t.WbsTask.id,
                task_name=t.WbsTask.work_content_l4,
                priority='中',  # 服务器表无priority字段,默认中
                assignee_name=t.real_name if scope == 'project' else None,
                plan_end_date=t.WbsTask.plan_end_date,
                status=t.WbsTask.status
            ) for t in tasks
        ]