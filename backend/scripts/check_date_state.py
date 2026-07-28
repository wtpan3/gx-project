"""确认当前日期倒挂状态"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    rows = list(conn.execute(text("""
        SELECT task_code, project_phase_l1, sub_phase_l2, plan_start_date, plan_end_date
        FROM wbs_tasks WHERE plan_end_date < plan_start_date ORDER BY task_code
    """)))
    print(f'全表日期倒挂共 {len(rows)} 条:')
    for r in rows:
        print(f'  {r[0]:<15} {r[1]}/{r[2]}: {r[3]} ~ {r[4]}')

    r = conn.execute(text("""
        SELECT plan_start_date, plan_end_date FROM wbs_tasks WHERE task_code='L2-022'
    """)).fetchone()
    print(f'\nL2-022 当前: {r[0]} ~ {r[1]}')

    print('\n[应用培训 L1-006 及其子任务]')
    for r in conn.execute(text("""
        SELECT task_code, sub_phase_l2, plan_start_date, plan_end_date
        FROM wbs_tasks WHERE id=52 OR parent_id=52 ORDER BY id
    """)):
        print(f'  {r[0]:<10} {r[1]:<16} {r[2]} ~ {r[3]}')
