# -*- coding: utf-8 -*-
"""备份待删除表的结构与数据（risk_tasks / templates_old_20260728）"""
import os
import sys
from datetime import datetime

import pymysql
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    charset='utf8mb4',
)

TABLES = ['risk_tasks', 'templates_old_20260728']
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
out = os.path.join(
    os.path.dirname(__file__), '..', '..', 'ai_workspace',
    f'backup_before_drop_{ts}.sql'
)

lines = [
    '-- 删表前备份',
    f'-- 生成时间: {datetime.now():%Y-%m-%d %H:%M:%S}',
    f'-- 数据库: {os.getenv("DB_NAME")}',
    '',
    'SET NAMES utf8mb4;',
    '',
]

with conn.cursor() as cur:
    for t in TABLES:
        cur.execute(f"SHOW TABLES LIKE '{t}'")
        if not cur.fetchone():
            print(f'⚠️  {t} 不存在，跳过')
            continue

        cur.execute(f'SHOW CREATE TABLE `{t}`')
        ddl = cur.fetchone()[1]
        lines += [f'-- ===== {t} =====', f'{ddl};', '']

        cur.execute(f'SELECT COUNT(*) FROM `{t}`')
        cnt = cur.fetchone()[0]
        lines.append(f'-- 数据行数: {cnt}')

        if cnt:
            cur.execute(f'SHOW COLUMNS FROM `{t}`')
            cols = [r[0] for r in cur.fetchall()]
            cur.execute(f'SELECT * FROM `{t}`')
            for row in cur.fetchall():
                vals = []
                for v in row:
                    if v is None:
                        vals.append('NULL')
                    elif isinstance(v, (int, float)):
                        vals.append(str(v))
                    else:
                        vals.append("'" + str(v).replace("'", "''") + "'")
                lines.append(
                    f'INSERT INTO `{t}` ({", ".join(cols)}) VALUES ({", ".join(vals)});'
                )
        lines.append('')
        print(f'✅ {t} 已备份（{cnt} 条）')

with open(out, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

conn.close()
print(f'\n✅ 备份文件: {os.path.abspath(out)}')
