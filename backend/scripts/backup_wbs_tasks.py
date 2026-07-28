"""备份 wbs_tasks 全表为可回灌的 INSERT 语句（mysqldump 不可用时的替代）"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine
from sqlalchemy import text

OUT = Path(__file__).parent.parent.parent / 'ai_workspace' / 'backup_wbs_tasks_20260728.sql'


def lit(v):
    if v is None:
        return 'NULL'
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace('\\', '\\\\').replace("'", "\\'")
    return f"'{s}'"


with engine.connect() as conn:
    cols = [r[0] for r in conn.execute(text('SHOW COLUMNS FROM wbs_tasks'))]
    rows = list(conn.execute(text('SELECT * FROM wbs_tasks ORDER BY id')))

    lines = [
        '-- wbs_tasks 全表备份 2026-07-28 (清理测试数据前)',
        f'-- 共 {len(rows)} 行  库=gx_project_dev',
        'SET NAMES utf8mb4;',
        'SET FOREIGN_KEY_CHECKS=0;',
        '',
    ]
    for r in rows:
        vals = ', '.join(lit(v) for v in r)
        lines.append(f"INSERT INTO wbs_tasks ({', '.join(cols)}) VALUES ({vals});")
    lines += ['', 'SET FOREIGN_KEY_CHECKS=1;']

    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'已备份 {len(rows)} 行 → {OUT}')
