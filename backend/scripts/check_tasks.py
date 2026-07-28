"""清理前影响面核查：外键表关联行 + 正式数据是否依赖测试数据 + 脏数据扫描"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

TEST = "NOT (task_code LIKE 'L1-%' OR task_code LIKE 'L2-0%')"

with engine.connect() as conn:
    print('=== 1. 外键表中指向测试任务的行 ===')
    for tbl, col in [('risk_tasks', 'task_id'), ('task_attachments', 'task_id'),
                     ('trainings', 'related_task_id')]:
        n = conn.execute(text(f"""
            SELECT COUNT(*) FROM {tbl}
            WHERE {col} IN (SELECT id FROM wbs_tasks WHERE {TEST})
        """)).scalar()
        total = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
        print(f'  {tbl}.{col}: 受影响 {n} 行 / 表总计 {total} 行')

    print('\n=== 2. 正式数据(L1-/L2-0)是否有父指向测试任务 ===')
    rows = list(conn.execute(text(f"""
        SELECT id, task_code, parent_id FROM wbs_tasks
        WHERE (task_code LIKE 'L1-%' OR task_code LIKE 'L2-0%')
          AND parent_id IN (SELECT id FROM wbs_tasks WHERE {TEST})
    """)))
    print(f'  {len(rows)} 行' + (f': {rows}' if rows else ' → 无依赖，可安全删除'))

    print('\n=== 3. 正式数据日期倒挂扫描(结束<开始) ===')
    for x in conn.execute(text("""
        SELECT id, task_code, sub_phase_l2, plan_start_date, plan_end_date
        FROM wbs_tasks
        WHERE (task_code LIKE 'L1-%' OR task_code LIKE 'L2-0%')
          AND plan_end_date < plan_start_date
    """)):
        print(f'  ⚠ {x[1]} id={x[0]} {x[2]}: {x[3]} ~ {x[4]}')

    print('\n=== 4. 子任务超出父范围扫描 ===')
    for x in conn.execute(text("""
        SELECT c.task_code, c.plan_start_date, c.plan_end_date,
               p.task_code, p.plan_start_date, p.plan_end_date
        FROM wbs_tasks c JOIN wbs_tasks p ON c.parent_id=p.id
        WHERE (c.task_code LIKE 'L2-0%')
          AND (c.plan_start_date < p.plan_start_date OR c.plan_end_date > p.plan_end_date)
    """)):
        print(f'  ⚠ {x[0]}({x[1]}~{x[2]}) 超出父 {x[3]}({x[4]}~{x[5]})')
