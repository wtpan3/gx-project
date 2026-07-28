# -*- coding: utf-8 -*-
"""执行 project_id 迁移SQL脚本"""
import os
import sys

import pymysql
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

sql_file = 'F:/claude code/Projectmanage/gx-project/ai_workspace/migrate_add_project_id.sql'

with open(sql_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    charset='utf8mb4',
)

print('开始执行迁移SQL...\n')

try:
    with conn.cursor() as cur:
        # 分号分割，逐条执行
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]

        total = len(statements)
        for i, stmt in enumerate(statements, 1):
            # 跳过纯注释行
            if not stmt or all(line.startswith('--') for line in stmt.split('\n') if line.strip()):
                continue

            print(f'[{i}/{total}] 执行: {stmt[:80]}...' if len(stmt) > 80 else f'[{i}/{total}] 执行: {stmt}')

            try:
                cur.execute(stmt)
                conn.commit()
                print(f'  ✅ 成功')
            except Exception as e:
                print(f'  ❌ 失败: {e}')
                raise

    print('\n✅ 迁移完成！')

except Exception as e:
    print(f'\n❌ 迁移失败: {e}')
    conn.rollback()
    sys.exit(1)

finally:
    conn.close()
