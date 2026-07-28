# -*- coding: utf-8 -*-
"""验证 project_id 迁移结果"""
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

print('===== 验证迁移结果 =====\n')

with conn.cursor() as cur:
    # 1. 检查各表 project_id 分布
    print('1. 各表 project_id 数据分布：\n')
    tables = ['schools', 'dict_items', 'wbs_tasks', 'devices', 'trainings', 'risks', 'reports', 'files', 'operation_logs']

    for table in tables:
        cur.execute(f'SELECT COUNT(*) AS total, COUNT(DISTINCT project_id) AS projects FROM `{table}`')
        row = cur.fetchone()
        print(f'  {table:<20} 总数={row[0]:>4}  项目数={row[1]:>2}')

    # 2. 检查新表结构
    print('\n2. 新建表验证：\n')

    cur.execute("SHOW TABLES LIKE 'templates'")
    if cur.fetchone():
        cur.execute('SELECT COUNT(*) FROM templates')
        print(f'  templates 表存在，行数={cur.fetchone()[0]}')

        cur.execute('SHOW COLUMNS FROM templates')
        cols = [row[0] for row in cur.fetchall()]
        print(f'  字段数={len(cols)}，包含: {", ".join(cols[:8])}...')

    cur.execute("SHOW TABLES LIKE 'template_wbs_stages'")
    if cur.fetchone():
        cur.execute('SELECT COUNT(*) FROM template_wbs_stages')
        print(f'  template_wbs_stages 表存在，行数={cur.fetchone()[0]}')

    cur.execute("SHOW TABLES LIKE 'templates_old_20260728'")
    if cur.fetchone():
        print(f'  templates_old_20260728 备份表存在')

    # 3. 检查 wbs_tasks 新增字段
    print('\n3. wbs_tasks 材料字段验证：\n')
    cur.execute('SHOW COLUMNS FROM wbs_tasks LIKE "%material%"')
    for row in cur.fetchall():
        print(f'  {row[0]}: {row[1]}')

    # 4. 检查 files 表新增字段
    print('\n4. files 表新增字段验证：\n')
    cur.execute('SHOW COLUMNS FROM files')
    cols = [row[0] for row in cur.fetchall()]
    if 'wbs_task_id' in cols and 'template_id' in cols:
        print(f'  ✅ wbs_task_id, template_id 已添加')

    # 5. 检查数据字典
    print('\n5. 数据字典新增验证：\n')
    cur.execute("SELECT COUNT(*) FROM dict_items WHERE category='模板类型'")
    count = cur.fetchone()[0]
    print(f'  模板类型字典：{count} 条')

    cur.execute("SELECT label FROM dict_items WHERE category='模板类型' ORDER BY sort_order")
    types = [row[0] for row in cur.fetchall()]
    print(f'  包含: {", ".join(types)}')

    # 6. 检查外键约束
    print('\n6. 外键约束验证：\n')
    cur.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA='gx_project_dev'
        AND COLUMN_NAME='project_id'
        ORDER BY TABLE_NAME
    """)
    fks = cur.fetchall()
    print(f'  project_id 外键数量: {len(fks)}')
    for fk in fks:
        print(f'    {fk[0]}.{fk[1]} → {fk[2]}')

print('\n✅ 验证完成！')
conn.close()
