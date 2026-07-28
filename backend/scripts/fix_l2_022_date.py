"""修复 L2-022「完成培训执行」日期倒挂

原值: 2027-09-15 ~ 2026-10-31 (开始晚于结束)
改为: 2026-09-15 ~ 2026-10-31 (开始年份 2027→2026)

依据: 父任务 L1-006「应用培训」范围 2026-08-20~2026-10-31，
      前序 L2-021「完成培训方案制定」2026-08-20~2026-08-31，
      结束日 2026-10-31 与父任务结束日一致，故判定为开始年份笔误。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

with engine.begin() as conn:
    old = conn.execute(text(
        "SELECT plan_start_date, plan_end_date FROM wbs_tasks WHERE task_code='L2-022'"
    )).fetchone()

    conn.execute(text(
        "UPDATE wbs_tasks SET plan_start_date='2026-09-15' WHERE task_code='L2-022'"
    ))

    new = conn.execute(text(
        "SELECT plan_start_date, plan_end_date FROM wbs_tasks WHERE task_code='L2-022'"
    )).fetchone()
    print(f'L2-022: {old[0]} ~ {old[1]}  →  {new[0]} ~ {new[1]}')

    left = conn.execute(text(
        'SELECT COUNT(*) FROM wbs_tasks WHERE plan_end_date < plan_start_date'
    )).scalar()
    print(f'全表剩余日期倒挂: {left} 条')

    # 父子范围复核
    r = conn.execute(text("""
        SELECT c.task_code, c.plan_start_date, c.plan_end_date,
               p.task_code, p.plan_start_date, p.plan_end_date
        FROM wbs_tasks c JOIN wbs_tasks p ON c.parent_id = p.id
        WHERE c.task_code = 'L2-022'
    """)).fetchone()
    ok = r[1] >= r[4] and r[2] <= r[5]
    print(f'父子范围: {r[0]}({r[1]}~{r[2]}) vs {r[3]}({r[4]}~{r[5]}) → {"落在父范围内" if ok else "越界"}')
