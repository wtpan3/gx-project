"""
GX项目交付管理系统 V2.1 - 数据初始化脚本
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from main import get_db, hash_password
from datetime import datetime

def init_data():
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 检查是否已有数据
    user_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count > 0:
        print("数据库已有数据，跳过初始化")
        conn.close()
        return

    # 1. 初始化用户 (密码: 123456)
    users = [
        ("admin", "管理员", "admin", "13800000001", "admin@example.com"),
        ("pm001", "张项目经理", "project_manager", "13800000002", "pm@example.com"),
        ("cm001", "李校园经理", "campus_manager", "13800000003", "cm1@example.com"),
        ("cm002", "王校园经理", "campus_manager", "13800000004", "cm2@example.com"),
    ]

    for username, real_name, role, phone, email in users:
        password_hash = hash_password("123456")
        c.execute("""INSERT INTO users(username, password_hash, real_name, role, phone, email, status, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?)""",
            (username, password_hash, real_name, role, phone, email, "启用", now, now))

    conn.commit()
    print(f"已创建 {len(users)} 个用户")

    # 2. 初始化学校
    schools = [
        ("GX-2026-001", "高新一中", "四川省成都市高新区", "成都市高新区天府大道1号", "张校长", "13800138001"),
        ("GX-2026-002", "高新二中", "四川省成都市高新区", "成都市高新区天府大道2号", "李校长", "13800138002"),
        ("GX-2026-003", "高新三中", "四川省成都市高新区", "成都市高新区天府大道3号", "王校长", "13800138003"),
    ]

    for i, (code, full_name, region, address, contact, phone) in enumerate(schools):
        c.execute("""INSERT INTO schools(code, full_name, region, address, campus_manager_id, contact_person, contact_phone, project_status, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (code, full_name, region, address, 3 + (i % 2), contact, phone, "实施中", now, now))

    conn.commit()
    print(f"已创建 {len(schools)} 个学校")

    # 3. 初始化设备系统字典
    device_systems = [
        ("GX智慧教育", "2026", "AI英语听说系统", "听说考试专用耳机", "讯飞", "iFLYTEK-001", "蓝牙5.0", "硬件", "台", 100),
        ("GX智慧教育", "2026", "AI英语听说系统", "音频采集器", "讯飞", "iFLYTEK-002", "32路", "硬件", "台", 10),
        ("GX智慧教育", "2026", "智慧教室系统", "智慧黑板", "希沃", "Seewo-E86EA", "86寸", "硬件", "块", 50),
        ("GX智慧教育", "2026", "智慧教室系统", "高清投影仪", "爱普生", "CB-2255U", "5000流明", "硬件", "台", 30),
        ("GX智慧教育", "2026", "智慧教室系统", "实物展台", "鸿合", "HV-85A", "1200万像素", "硬件", "台", 30),
        ("GX智慧教育", "2026", "校园网络系统", "核心交换机", "华为", "S5735S-L48T4S-A1", "48口", "硬件", "台", 5),
        ("GX智慧教育", "2026", "校园网络系统", "接入交换机", "华为", "S1730S-L24T-A", "24口", "硬件", "台", 20),
        ("GX智慧教育", "2026", "校园安防系统", "监控摄像头", "海康威视", "DS-2CD3T46FWDV2-I3S", "400万", "硬件", "台", 100),
        ("GX智慧教育", "2026", "校园安防系统", "硬盘录像机", "海康威视", "DS-8632N-I8", "32路", "硬件", "台", 5),
    ]

    for project_name, construction_year, system_name, device_name, brand, model, params, device_type, unit, plan_quantity in device_systems:
        c.execute("""INSERT INTO device_systems(project_name, construction_year, system_name, device_name, brand, model, params, device_type, unit, plan_quantity, is_enabled, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (project_name, construction_year, system_name, device_name, brand, model, params, device_type, unit, plan_quantity, 1, now, now))

    conn.commit()
    print(f"已创建 {len(device_systems)} 个设备字典")

    # 4. 初始化供应商
    suppliers = [
        ("科大讯飞股份有限公司", "王经理", "13800138010", "wang@iflytek.com"),
        ("希沃（seewo）", "李经理", "13800138011", "li@seewo.com"),
        ("华为技术有限公司", "张经理", "13800138012", "zhang@huawei.com"),
        ("海康威视数字技术股份有限公司", "赵经理", "13800138013", "zhao@hikvision.com"),
    ]

    for name, contact, phone, email in suppliers:
        c.execute("""INSERT INTO suppliers(name, contact_person, contact_phone, contact_email, created_at, updated_at)
            VALUES(?,?,?,?,?,?)""", (name, contact, phone, email, now, now))

    conn.commit()
    print(f"已创建 {len(suppliers)} 个供应商")

    # 5. 初始化数据字典
    dict_items = [
        # 项目名称
        ("项目名称", "GX智慧教育", "GX智慧教育", 1),
        # 建设年份
        ("建设年份", "2026年", "2026", 1),
        ("建设年份", "2027年", "2027", 2),
        ("建设年份", "2028年", "2028", 3),
        # 关联阶段
        ("关联阶段", "到货验收", "到货验收", 1),
        ("关联阶段", "加电测试", "加电测试", 2),
        ("关联阶段", "校级验收", "校级验收", 3),
        ("关联阶段", "培训", "培训", 4),
        ("关联阶段", "无", "无", 5),
        # WBS状态
        ("WBS状态", "待开始", "待开始", 1),
        ("WBS状态", "进行中", "进行中", 2),
        ("WBS状态", "已完成", "已完成", 3),
        ("WBS状态", "已延期", "已延期", 4),
        ("WBS状态", "待补材料", "待补材料", 5),
        # 设备来源
        ("设备来源", "库存发货", "库存发货", 1),
        ("设备来源", "外部采购", "外部采购", 2),
        # 设备状态
        ("设备状态", "待发货", "待发货", 1),
        ("设备状态", "已发货", "已发货", 2),
        ("设备状态", "已到货", "已到货", 3),
        ("设备状态", "已安装", "已安装", 4),
        ("设备状态", "已调试", "已调试", 5),
        ("设备状态", "已验收", "已验收", 6),
        # 培训类型
        ("培训类型", "集中培训", "集中培训", 1),
        ("培训类型", "现场培训", "现场培训", 2),
        ("培训类型", "线上培训", "线上培训", 3),
        ("培训类型", "区级培训", "区级培训", 4),
        # 培训方式
        ("培训方式", "理论讲授", "理论讲授", 1),
        ("培训方式", "实操演练", "实操演练", 2),
        ("培训方式", "考核测评", "考核测评", 3),
        # 风险概率/影响
        ("风险等级选项", "高", "高", 1),
        ("风险等级选项", "中", "中", 2),
        ("风险等级选项", "低", "低", 3),
        # 项目状态
        ("项目状态", "未启动", "未启动", 1),
        ("项目状态", "进行中", "进行中", 2),
        ("项目状态", "试运行", "试运行", 3),
        ("项目状态", "已验收", "已验收", 4),
        ("项目状态", "已结项", "已结项", 5),
        # 学校状态
        ("学校状态", "未启动", "未启动", 1),
        ("学校状态", "实施中", "实施中", 2),
        ("学校状态", "试运行", "试运行", 3),
        ("学校状态", "已验收", "已验收", 4),
        ("学校状态", "维保中", "维保中", 5),
        # 用户状态
        ("用户状态", "启用", "启用", 1),
        ("用户状态", "停用", "停用", 2),
        # 模板类型
        ("模板类型", "到货验收表", "到货验收表", 1),
        ("模板类型", "加电测试表", "加电测试表", 2),
        ("模板类型", "校级验收单", "校级验收单", 3),
        ("模板类型", "培训确认表", "培训确认表", 4),
        ("模板类型", "培训签到表", "培训签到表", 5),
        ("模板类型", "培训反馈表", "培训反馈表", 6),
        ("模板类型", "其他", "其他", 7),
    ]

    for category, label, value, sort_order in dict_items:
        c.execute("""INSERT INTO dict_items(category, label, value, sort_order, is_enabled, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?)""", (category, label, value, sort_order, 1, now, now))

    conn.commit()
    print(f"已创建 {len(dict_items)} 个字典项")

    # 6. 初始化项目信息
    c.execute("""INSERT INTO project_info(project_name, project_code, start_date, end_date, overall_status, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?)""",
        ("GX智慧教育项目", "GX-2026-001", "2026-01-01", "2026-12-31", "进行中", now, now))

    conn.commit()
    print("已创建项目信息")

    # 7. 初始化WBS任务（示例）
    wbs_tasks = [
        ("启动规划", "项目启动", "完成项目启动", "完成项目立项", None, "到货验收", "2026-01-01", "2026-01-15", "待开始", 1, 1),
        ("交付实施", "硬件交付", "完成AI英语听说系统交付", "完成设备到货", None, "到货验收", "2026-02-01", "2026-02-28", "进行中", 1, 1),
        ("交付实施", "硬件交付", "完成AI英语听说系统交付", "完成设备安装", None, "加电测试", "2026-03-01", "2026-03-15", "待开始", 1, 1),
        ("交付实施", "硬件交付", "完成AI英语听说系统交付", "完成设备调试", None, "加电测试", "2026-03-16", "2026-03-31", "待开始", 1, 1),
        ("交付实施", "应用培训", "完成教师培训", "完成教师培训", None, "培训", "2026-04-01", "2026-04-15", "待开始", 2, 1),
        ("验收移交", "竣工资料提交", "提交竣工资料", "整理并提交竣工资料", None, "校级验收", "2026-05-01", "2026-05-15", "待开始", 1, 1),
        ("验收移交", "业主验收会", "组织验收会", "完成校级验收", None, "校级验收", "2026-05-16", "2026-05-31", "待开始", 1, 1),
    ]

    for phase_l1, phase_l2, task_package_l3, work_content_l4, work_detail_l5, stage_type, plan_start, plan_end, status, assignee_id, school_id in wbs_tasks:
        c.execute("""INSERT INTO wbs_tasks(phase_l1, phase_l2, task_package_l3, work_content_l4, work_detail_l5, stage_type, plan_start_date, plan_end_date, status, assignee_id, school_id, construction_year, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (phase_l1, phase_l2, task_package_l3, work_content_l4, work_detail_l5, stage_type, plan_start, plan_end, status, assignee_id, school_id, "2026", now, now))

    conn.commit()
    print(f"已创建 {len(wbs_tasks)} 个WBS任务")

    # 8. 初始化设备（示例）
    devices = [
        (1, "听说考试专用耳机", 50, "库存发货", 1, "2026-02-15", "已发货"),
        (1, "听说考试专用耳机", 30, "库存发货", 2, "2026-02-20", "待发货"),
        (3, "智慧黑板", 20, "外部采购", 1, "2026-03-01", "待发货"),
    ]

    for system_id, device_name, quantity, source, school_id, plan_arrival, status in devices:
        ds = conn.execute("SELECT * FROM device_systems WHERE id=?", (system_id,)).fetchone()
        c.execute("""INSERT INTO devices(project_name, construction_year, system_id, system_name, device_name, brand, model, params, device_type, unit, source, quantity, school_id, plan_arrival_date, status, created_at, updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (ds["project_name"], ds["construction_year"], system_id, ds["system_name"], device_name, ds["brand"], ds["model"], ds["params"], ds["device_type"], ds["unit"], source, quantity, school_id, plan_arrival, status, now, now))

    conn.commit()
    print(f"已创建 {len(devices)} 个设备记录")

    conn.close()
    print("\n初始化完成！")
    print("默认账号密码：")
    print("  管理员: admin / 123456")
    print("  项目经理: pm001 / 123456")
    print("  校园经理: cm001, cm002 / 123456")

if __name__ == "__main__":
    init_data()
