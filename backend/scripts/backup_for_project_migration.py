# -*- coding: utf-8 -*-
"""备份即将修改的9张表 + templates表"""
import os
import sys
from datetime import datetime

import pymysql
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

tables_to_backup = [
    'schools',
    'dict_items',
    'wbs_tasks',
    'devices',
    'trainings',
    'risks',
    'reports',
    'files',
    'operation_logs',
    'templates'
]

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = f'F:/claude code/Projectmanage/gx-project/ai_workspace/backup_project_migration_{timestamp}.sql'

conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    charset='utf8mb4',
)

with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(f'-- 备份时间: {datetime.now()}\n')
    f.write(f'-- 数据库: {os.getenv("DB_NAME")}\n')
    f.write(f'-- 备份内容: project_id 迁移前的10张表\n\n')
    f.write('SET FOREIGN_KEY_CHECKS=0;\n\n')

    with conn.cursor() as cur:
        for table in tables_to_backup:
            # 表结构
            cur.execute(f'SHOW CREATE TABLE `{table}`')
            create_sql = cur.fetchone()[1]
            f.write(f'-- ============================================================\n')
            f.write(f'-- {table}\n')
            f.write(f'-- ============================================================\n')
            f.write(f'DROP TABLE IF EXISTS `{table}_backup_{timestamp}`;\n')
            f.write(f'{create_sql};\n\n')

            # 数据
            cur.execute(f'SELECT COUNT(*) FROM `{table}`')
            count = cur.fetchone()[0]

            if count > 0:
                cur.execute(f'SELECT * FROM `{table}`')
                columns = [desc[0] for desc in cur.description]

                f.write(f'-- {count} 条数据\n')
                f.write(f'INSERT INTO `{table}` ({", ".join([f"`{c}`" for c in columns])}) VALUES\n')

                rows = cur.fetchall()
                for i, row in enumerate(rows):
                    values = []
                    for val in row:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        elif isinstance(val, datetime):
                            values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                        else:
                            # 转义单引号
                            escaped = str(val).replace("'", "''")
                            values.append(f"'{escaped}'")

                    comma = ',' if i < len(rows) - 1 else ';'
                    f.write(f'({", ".join(values)}){comma}\n')

                f.write('\n')
            else:
                f.write(f'-- 无数据\n\n')

    f.write('SET FOREIGN_KEY_CHECKS=1;\n')

conn.close()

print(f'✅ 备份完成: {backup_file}')
print(f'   共备份 {len(tables_to_backup)} 张表')
