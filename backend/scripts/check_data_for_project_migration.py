# -*- coding: utf-8 -*-
"""检查需要回填 project_id 的表的现有数据量"""
import os
import sys

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

tables_to_check = [
    'schools',
    'dict_items',
    'wbs_tasks',
    'devices',
    'trainings',
    'risks',
    'reports',
    'files',
    'operation_logs'
]

print('===== 需要添加 project_id 的表 数据量核查 =====\n')

with conn.cursor() as cur:
    # 先查 project_info
    cur.execute('SELECT id, project_name, project_code FROM project_info')
    projects = cur.fetchall()
    print(f'project_info 表现有项目: {len(projects)} 个')
    for p in projects:
        print(f'  id={p[0]}, name={p[1]}, code={p[2]}')

    print('\n需要回填的表:\n')
    total = 0
    for table in tables_to_check:
        cur.execute(f'SELECT COUNT(*) FROM `{table}`')
        count = cur.fetchone()[0]
        total += count
        print(f'  {table:<20} {count:>6} 条')

    print(f'\n总计: {total} 条记录需要回填 project_id')

conn.close()
