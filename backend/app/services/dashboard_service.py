"""Dashboard 数据聚合服务"""
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

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

        # 学校进度统计 - 从 wbs_tasks 表真实查询各阶段学校数
        # 逻辑: 根据各学校关联的末级任务(level=3)完成情况判断学校所处阶段
        # 简化版: 统计各学校的任务完成比例，按阈值划分阶段

        # 获取所有学校ID列表
        schools = db.query(School.id, School.full_name).all()
        school_phase_counts = {
            '已完成': 0,
            '装修中': 0,
            '安装中': 0,
            '调试中': 0,
            '培训中': 0,
            '待启动': 0
        }

        for school_id, school_name in schools:
            # 查询该学校的末级任务(work_content_l4不为空)
            school_tasks = db.query(WbsTask).filter(
                WbsTask.school_id == school_id,
                WbsTask.work_content_l4 != ''
            ).all()

            if not school_tasks:
                # 无任务视为待启动
                school_phase_counts['待启动'] += 1
                continue

            # 统计任务完成情况
            total_tasks = len(school_tasks)
            completed_tasks = sum(1 for t in school_tasks if t.status == '已完成')
            completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0

            # 根据完成率和任务阶段关键词判断学校阶段
            if completion_rate >= 1.0:
                school_phase_counts['已完成'] += 1
            elif completion_rate == 0:
                school_phase_counts['待启动'] += 1
            else:
                # 根据进行中任务的阶段名称判断
                in_progress_tasks = [t for t in school_tasks if t.status == '进行中']
                if in_progress_tasks:
                    # 取第一个进行中任务的阶段作为学校当前阶段
                    phase_name = in_progress_tasks[0].project_phase_l1 or ''
                    if '装修' in phase_name or '环境' in phase_name:
                        school_phase_counts['装修中'] += 1
                    elif '安装' in phase_name:
                        school_phase_counts['安装中'] += 1
                    elif '调试' in phase_name:
                        school_phase_counts['调试中'] += 1
                    elif '培训' in phase_name:
                        school_phase_counts['培训中'] += 1
                    else:
                        # 默认按完成率判断
                        if completion_rate > 0.8:
                            school_phase_counts['培训中'] += 1
                        elif completion_rate > 0.6:
                            school_phase_counts['调试中'] += 1
                        elif completion_rate > 0.4:
                            school_phase_counts['安装中'] += 1
                        else:
                            school_phase_counts['装修中'] += 1
                else:
                    # 无进行中任务但有已完成，按完成率判断
                    if completion_rate > 0.8:
                        school_phase_counts['培训中'] += 1
                    elif completion_rate > 0.6:
                        school_phase_counts['调试中'] += 1
                    elif completion_rate > 0.4:
                        school_phase_counts['安装中'] += 1
                    else:
                        school_phase_counts['装修中'] += 1

        completed_schools = school_phase_counts['已完成']
        school_progress = [
            ProgressItem(label='已完成', count=school_phase_counts['已完成'], color='#52c41a'),
            ProgressItem(label='装修中', count=school_phase_counts['装修中'], color='#722ed1'),
            ProgressItem(label='安装中', count=school_phase_counts['安装中'], color='#fa8c16'),
            ProgressItem(label='调试中', count=school_phase_counts['调试中'], color='#1677ff'),
            ProgressItem(label='培训中', count=school_phase_counts['培训中'], color='#faad14'),
            ProgressItem(label='待启动', count=school_phase_counts['待启动'], color='#8c8c8c'),
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
        """关键里程碑(取L1项目阶段+L2子阶段,去重后按层级展示,L1父/L2子,不限条数)
        V2.3需求§6.1.5/§6.2.6: 取L1+L2作为里程碑节点，层级展示，去重，按计划开始时间排序。
        """
        tasks = db.query(WbsTask).filter(
            WbsTask.is_orphan == 0,
            WbsTask.project_phase_l1 != ''
        ).all()

        def _agg_status(statuses):
            """聚合状态: 全已完成→已完成; 有已延期→已延期; 有进行中/部分完成→进行中; 否则→未开始"""
            s = set(statuses)
            if s and all(x == '已完成' for x in s):
                return '已完成'
            if '已延期' in s:
                return '已延期'
            if '进行中' in s or '已完成' in s or '待补材料' in s:
                return '进行中'
            return '未开始'

        def _date_range(items, getter):
            vals = [getter(t) for t in items if getter(t) is not None]
            return (min(vals) if vals else None, max(vals) if vals else None)

        # 按L1分组
        l1_groups = {}
        for t in tasks:
            l1_groups.setdefault(t.project_phase_l1, []).append(t)

        # L1按最早计划开始时间排序
        def _min_start(items):
            vals = [t.plan_start_date for t in items if t.plan_start_date is not None]
            return min(vals) if vals else date.max

        result = []
        for l1_name in sorted(l1_groups.keys(), key=lambda k: _min_start(l1_groups[k])):
            l1_tasks = l1_groups[l1_name]
            l1_start, _ = _date_range(l1_tasks, lambda t: t.plan_start_date)
            _, l1_end = _date_range(l1_tasks, lambda t: t.plan_end_date)
            # L1父节点
            result.append(Milestone(
                level=1,
                phase=l1_name,
                task=l1_name,
                plan_start_date=l1_start,
                plan_end_date=l1_end,
                status=_agg_status([t.status for t in l1_tasks])
            ))
            # 该L1下的L2子节点(去重,过滤空L2)
            l2_groups = {}
            for t in l1_tasks:
                if t.sub_phase_l2:
                    l2_groups.setdefault(t.sub_phase_l2, []).append(t)
            for l2_name in sorted(l2_groups.keys(), key=lambda k: _min_start(l2_groups[k])):
                l2_tasks = l2_groups[l2_name]
                l2_start, _ = _date_range(l2_tasks, lambda t: t.plan_start_date)
                _, l2_end = _date_range(l2_tasks, lambda t: t.plan_end_date)
                result.append(Milestone(
                    level=2,
                    phase=l1_name,
                    task=l2_name,
                    plan_start_date=l2_start,
                    plan_end_date=l2_end,
                    status=_agg_status([t.status for t in l2_tasks])
                ))

        return result

    @staticmethod
    def _get_risks(db: Session) -> List[RiskItem]:
        """项目风险(仅活跃风险:状态≠已关闭,按等级+状态排序,最多8条)"""
        risks = db.query(Risk, User.real_name).outerjoin(
            User, Risk.responsible_person_id == User.id
        ).filter(
            Risk.status != '已关闭'
        ).order_by(
            # 高→中→低
            func.field(Risk.risk_level, '高', '中', '低'),
            # 应对中→已识别
            func.field(Risk.status, '应对中', '已识别'),
            # 创建时间升序（最新的排前面）
            Risk.created_at.desc()
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
                plan_close_date=None,  # V2.3轻量级模型：移除response_deadline
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
                priority=t.WbsTask.priority or '中',  # 读真实优先级(高/中/低),空则默认中
                assignee_name=t.real_name if scope == 'project' else None,
                plan_end_date=t.WbsTask.plan_end_date,
                status=t.WbsTask.status
            ) for t in tasks
        ]