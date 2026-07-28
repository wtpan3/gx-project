"""清理测试数据 + 修复L2-022日期倒挂（已备份 ai_workspace/backup_wbs_tasks_20260728.sql）"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

TEST = "NOT (task_code LIKE 'L1-%' OR task_code LIKE 'L2-0%')"

with engine.begin() as conn:
    before = conn.execute(text('SELECT COUNT(*) FROM wbs_tasks')).scalar()

    # 临时关闭外键检查（测试数据间有父子关系）
    conn.execute(text('SET FOREIGN_KEY_CHECKS=0'))

    result = conn.execute(text(f'DELETE FROM wbs_tasks WHERE {TEST}'))
    deleted = result.rowcount

    conn.execute(text('SET FOREIGN_KEY_CHECKS=1'))

    after = conn.execute(text('SELECT COUNT(*) FROM wbs_tasks')).scalar()
    print(f'删除完成: {before} → {after} 行 (实删 {deleted})')

    # 修复 L2-022 日期倒挂：开始年份 2027 → 2026（结束 2026-10-31 保留）
    old = conn.execute(text(
        "SELECT plan_start_date, plan_end_date FROM wbs_tasks WHERE task_code='L2-022'")).fetchone()
    conn.execute(text("""
        UPDATE wbs_tasks SET plan_start_date='2026-09-15'
        WHERE task_code='L2-022'
    """))
    new = conn.execute(text(
        "SELECT plan_start_date, plan_end_date FROM wbs_tasks WHERE task_code='L2-022'")).fetchone()
    print(f'L2-022 修复: {old[0]}~{old[1]} → {new[0]}~{new[1]}')
