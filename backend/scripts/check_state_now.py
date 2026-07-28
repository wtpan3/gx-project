"""恢复后完整性校验：行数/编码/父子链/孤儿/中文"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

BACKUP = Path(__file__).parent.parent.parent / 'ai_workspace' / 'backup_wbs_tasks_20260728.sql'

with engine.connect() as conn:
    r = conn.execute(text("""
        SELECT COUNT(*), SUM(task_code LIKE 'L1-%'), SUM(task_code LIKE 'L2-0%'),
               SUM(NOT (task_code LIKE 'L1-%' OR task_code LIKE 'L2-0%'))
        FROM wbs_tasks
    """)).fetchone()
    print(f'总数={r[0]}  L1={r[1]}  L2正式={r[2]}  测试数据={r[3]}')

    db_ids = {x[0] for x in conn.execute(text('SELECT id FROM wbs_tasks'))}
    bak_ids = {int(m) for m in re.findall(r'VALUES \((\d+),', BACKUP.read_text(encoding='utf-8'))}
    print(f'与备份差异: 缺失={sorted(bak_ids - db_ids)}  多余={sorted(db_ids - bak_ids)}')

    n = conn.execute(text("""
        SELECT COUNT(*) FROM wbs_tasks c WHERE c.parent_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM (SELECT id FROM wbs_tasks) p WHERE p.id=c.parent_id)
    """)).scalar()
    print(f'孤儿(父不存在)={n}')

    print('\n[抽样中文校验]')
    for x in conn.execute(text("""
        SELECT task_code, project_phase_l1, sub_phase_l2, work_content_l4, status, priority
        FROM wbs_tasks WHERE task_code IN ('WBS-T001','L2-OLD-003','WBS-AUTO-0007','TEST-001','L2-022')
        ORDER BY task_code
    """)):
        print(f'  {x[0]:<15} {x[1]}/{x[2]}/{x[3]} | {x[4]} | {x[5]}')

    print('\n[父子链抽样]')
    for x in conn.execute(text("""
        SELECT c.task_code, p.task_code FROM wbs_tasks c JOIN wbs_tasks p ON c.parent_id=p.id
        WHERE c.task_code IN ('WBS-T001','WBS-AUTO-0007','L2-OLD-003','L2-001')
        ORDER BY c.task_code
    """)):
        print(f'  {x[0]} → 父 {x[1]}')
