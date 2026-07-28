"""验证 L2-022 修复结果"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    r = conn.execute(text("SELECT plan_start_date, plan_end_date FROM wbs_tasks WHERE task_code='L2-022'")).fetchone()
    print(f'L2-022: {r[0]} ~ {r[1]}')

    n = conn.execute(text('SELECT COUNT(*) FROM wbs_tasks WHERE plan_end_date < plan_start_date')).scalar()
    print(f'全表剩余日期倒挂: {n} 条')

    total = conn.execute(text('SELECT COUNT(*) FROM wbs_tasks')).scalar()
    print(f'总任务数: {total}')
