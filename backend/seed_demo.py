"""
首页Dashboard演示数据种子脚本
插入学校/设备/风险/WBS任务/产线/软件模块
"""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.school import School
from app.models.device_system import DeviceSystem
from app.models.device import Device
from app.models.wbs_task import WBSTask
from app.models.risk import Risk
from app.models.production_line import ProductionLine
from app.models.software_module import SoftwareModule
from app.models.user import User


def seed_demo_data():
    db = SessionLocal()
    today = date.today()
    try:
        print("开始插入首页演示数据...")

        # 检查是否已有数据
        if db.query(School).count() > 0:
            print("[WARN] schools 表已有数据,跳过种子插入")
            return

        # 获取已有用户(pm001不存在时用admin作为后备)
        admin = db.query(User).filter(User.username == 'admin').first()
        pm = db.query(User).filter(User.username == 'pm001').first()
        if not pm:
            pm = admin  # pm001不存在时使用admin

        # 1. 学校(20所,5所重点)
        schools_data = [
            ('SC001', '第一中学', '高新区', '高新路1号', '王校长', '13800001001', True),
            ('SC002', '第二小学', '高新区', '科技街2号', '李校长', '13800001002', True),
            ('SC003', '实验中学', '高新区', '创新大道3号', '张校长', '13800001003', True),
            ('SC004', '第三中学', '高新区', '智慧路4号', '赵校长', '13800001004', True),
            ('SC005', '外国语学校', '高新区', '国际路5号', '刘校长', '13800001005', True),
        ]
        for i in range(5, 20):
            schools_data.append((f'SC{i+1:03d}', f'第{i+1}学校', '高新区', f'教育路{i+1}号', f'校长{i+1}', f'1380000100{i+1}', False))

        schools = []
        for code, full_name, region, addr, contact_person, phone, is_key in schools_data:
            s = School(
                code=code,
                full_name=full_name,
                region=region,
                address=addr,
                contact_person=contact_person,
                contact_phone=phone,
                is_key=is_key,
                campus_manager_id=pm.id if pm else None
            )
            db.add(s)
            schools.append(s)
        db.flush()

        # 2. 设备系统(6个)
        systems_data = [
            ('数智工作台', '软件'), ('教育数据指挥中心', '软件'), ('智能应用创编平台', '软件'),
            ('应用能力服务', '软件'), ('AI算力中心', '硬件'), ('智能交互终端', '硬件')
        ]
        systems = []
        for sys_name, type_ in systems_data:
            s = DeviceSystem(
                project_name='高新区AI+教育项目',
                construction_year=2024,
                system_name=sys_name,
                device_name=sys_name,
                brand='标准',
                model='V1.0',
                type=type_,
                unit='套',
                plan_quantity=1
            )
            db.add(s)
            systems.append(s)
        db.flush()

        print(f"[OK] 插入 {len(schools)} 所学校, {len(systems)} 个系统")

        # 3. 设备(1240台,分布到各学校)
        devices = []
        device_types = ['服务器', 'GPU卡', '交换机', '智能黑板', 'VR设备', '机器人', '摄像头', '传感器']
        for i in range(1240):
            d = Device(
                project_name='高新区AI+教育项目',
                device_name=f'{device_types[i % len(device_types)]}-{i+1}',
                brand='标准品牌',
                model=f'型号{i+1}',
                unit='台',
                system_id=systems[i % len(systems)].id,
                school_id=schools[i % len(schools)].id,
                status=['待发货', '已到货', '已安装', '已调试', '运行中'][i % 5],
                source='三方外采' if i % 3 == 0 else '库存设备',
                quantity=1,
                construction_year=2024,
                type='硬件',
                plan_arrival_date=today - timedelta(days=30)
            )
            devices.append(d)
        db.bulk_save_objects(devices)
        print(f"[OK] 插入 {len(devices)} 台设备")

        # 4. 产线类型(3种)
        lines_data = [('智能制造产线', '用于智能硬件生产'), ('软件开发产线', '敏捷开发流水线'), ('内容制作产线', '数字内容生成')]
        for name, desc in lines_data:
            db.add(ProductionLine(name=name, description=desc, is_enabled=True))
        print(f"[OK] 插入 {len(lines_data)} 条产线")

        # 5. 软件模块(4个,对应原型)
        modules_data = [
            ('数智工作台', '上线运行', 80, 1),
            ('教育数据指挥中心', '软件测试', 50, 2),
            ('智能应用创编平台', '软件开发', 30, 3),
            ('应用能力服务', '上线运行', 90, 4)
        ]
        for name, phase, progress, order in modules_data:
            db.add(SoftwareModule(name=name, phase=phase, progress=progress, sort_order=order))
        print(f"[OK] 插入 {len(modules_data)} 个软件模块")

        # 6. WBS任务(5层结构,里程碑取L2子阶段,待办取L4工作内容)
        # 里程碑数据: (task_code, L1, L2, L3, L4, status, plan_start, plan_end, actual_start, actual_end)
        milestones_data = [
            ('WBS-001', '交付实施', '硬件到货验收', '设备到货', '完成硬件到货验收', '已完成',
             today - timedelta(days=90), today - timedelta(days=45), today - timedelta(days=90), today - timedelta(days=46)),
            ('WBS-002', '交付实施', '加电测试完成', '设备安装', '完成加电测试', '进行中',
             today - timedelta(days=60), today + timedelta(days=20), today - timedelta(days=60), None),
            ('WBS-003', '交付实施', '教师培训完成', '应用培训', '完成教师培训', '进行中',
             today - timedelta(days=20), today + timedelta(days=35), today - timedelta(days=20), None),
            ('WBS-004', '验收移交', '校级验收', '竣工资料', '完成校级验收', '待开始',
             today + timedelta(days=45), today + timedelta(days=135), None, None),
        ]
        for data in milestones_data:
            t = WBSTask(
                task_code=data[0],
                project_phase_l1=data[1],
                sub_phase_l2=data[2],
                task_package_l3=data[3],
                work_content_l4=data[4],
                status=data[5],
                school_id=schools[0].id,
                assignee_id=pm.id if pm else (admin.id if admin else None),
                plan_start_date=data[6],
                plan_end_date=data[7],
                actual_start_date=data[8],
                actual_end_date=data[9],
                construction_year=2024
            )
            db.add(t)
        print(f"[OK] 插入 {len(milestones_data)} 条里程碑任务(L2)")

        # L4工作内容(30条,分布本周/本月,用于待办)
        task_names = [
            '完成A校设备安装验收', '第三批设备采购下单', 'B校竣工资料提交', '审核B校验收材料',
            '提交8月进度周报', '更新风险登记表', 'C校网络环境测试', 'D校教师培训排课',
            'E校智能黑板调试', 'F校VR设备验收', 'G校数据中心巡检', 'H校应用上线准备',
            'I校项目验收会筹备', 'J校资产移交清单', 'K校故障设备维修', 'L校用户培训反馈收集',
            'M校月度进度汇报', 'N校设备入库清点', 'O校网络安全评估', 'P校应用功能测试',
            'Q校数据迁移方案', 'R校竣工报告编写', 'S校变更申请审批', 'T校采购合同签订',
            'U校设备到货验收', 'V校施工图纸审核', 'W校项目例会纪要', 'X校风险应对跟踪',
            'Y校质量检查报告', 'Z校项目收尾工作'
        ]
        for i, name in enumerate(task_names):
            days_offset = (i % 7) - 3  # 本周内分布
            t = WBSTask(
                task_code=f'WBS-T{i+1:03d}',
                project_phase_l1='交付实施',
                sub_phase_l2='硬件交付',
                task_package_l3='设备交付',
                work_content_l4=name,
                school_id=schools[i % len(schools)].id,
                assignee_id=admin.id if i % 2 == 0 else (pm.id if pm else None),
                status=['待开始', '进行中', '已延期'][i % 3],
                plan_start_date=today + timedelta(days=days_offset - 2),
                plan_end_date=today + timedelta(days=days_offset + 3),
                actual_start_date=today + timedelta(days=days_offset - 2) if i % 3 != 0 else None,
                construction_year=2024
            )
            db.add(t)
        print(f"[OK] 插入 {len(task_names)} 条末级任务(L4)")

        # 7. 风险(8条活跃风险)
        risks_data = [
            ('RISK-001', '高', '部分学校施工进度滞后', '项目整体延期1个月', '协调施工单位加快进度,调整计划', pm.id if pm else None, schools[0].id, '应对中', today - timedelta(days=10), today + timedelta(days=20)),
            ('RISK-002', '中', '关键设备供应商交付延迟', '硬件安装推迟2周', '寻找备选供应商,提前采购备件', admin.id if admin else None, schools[1].id, '应对中', today - timedelta(days=15), today + timedelta(days=30)),
            ('RISK-003', '低', '教师培训参与度不足', '应用推广效果打折', '优化培训内容,增加激励机制', pm.id if pm else None, schools[2].id, '已识别', today - timedelta(days=5), today + timedelta(days=60)),
            ('RISK-004', '高', 'A校网络带宽不满足需求', '系统无法正常运行', '紧急协调运营商升级专线', admin.id if admin else None, schools[3].id, '应对中', today - timedelta(days=3), today + timedelta(days=15)),
            ('RISK-005', '中', '软件模块联调接口不稳定', '上线时间推迟1周', '技术攻坚,每日联调', pm.id if pm else None, None, '应对中', today - timedelta(days=8), today + timedelta(days=25)),
            ('RISK-006', '低', '部分学校网络带宽不足', '系统运行体验下降', '协调学校升级专线', admin.id if admin else None, schools[4].id, '已识别', today - timedelta(days=12), today + timedelta(days=40)),
            ('RISK-007', '中', 'B校机房环境不达标', '设备无法按期安装', '协调学校整改机房', pm.id if pm else None, schools[5].id, '应对中', today - timedelta(days=7), today + timedelta(days=18)),
            ('RISK-008', '低', '项目文档管理不规范', '验收资料准备困难', '建立文档模板,定期检查', admin.id if admin else None, None, '已识别', today - timedelta(days=20), today + timedelta(days=50)),
        ]
        for data in risks_data:
            r = Risk(
                risk_desc=data[2],
                impact_description=data[3],
                response_strategy=data[4],
                responsible_person_id=data[5],
                school_id=data[6],
                status=data[7],
                risk_level=data[1],
                probability='中',
                impact='中',
                response_deadline=data[9]
            )
            db.add(r)
        print(f"[OK] 插入 {len(risks_data)} 条风险")

        db.commit()
        print("\n[SUCCESS] 首页演示数据插入完成!")
        print(f"  - 学校: {len(schools)} 所(含 5 所重点)")
        print(f"  - 设备系统: {len(systems)} 个")
        print(f"  - 设备: 1240 台")
        print(f"  - 产线: 3 条")
        print(f"  - 软件模块: 4 个")
        print(f"  - 里程碑(L2): {len(milestones_data)} 条")
        print(f"  - 待办(L3): {len(task_names)} 条")
        print(f"  - 风险: {len(risks_data)} 条")

    except Exception as e:
        print(f"[ERROR] 种子数据插入失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
