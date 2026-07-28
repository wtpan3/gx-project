# -*- coding: utf-8 -*-
"""从开发库导出完整 ddl.sql"""
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

output_file = 'F:/claude code/Projectmanage/gx-project/ddl_new.sql'

# 表的顺序（按依赖关系排序）
tables_order = [
    'users',
    'project_info',
    'schools',
    'suppliers',
    'templates',
    'template_wbs_stages',
    'dict_items',
    'wbs_tasks',
    'devices',
    'trainings',
    'training_schools',
    'risks',
    'risk_tasks',
    'reports',
    'files',
    'operation_logs',
    'production_lines',
    'software_modules',
    'todos'
]

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('-- ============================================================\n')
    f.write('-- GX教育项目交付管理系统 - 数据库结构定义\n')
    f.write('-- 生成时间: 2026-07-28\n')
    f.write('-- 数据库: gx_project_dev\n')
    f.write('-- 字符集: utf8mb4\n')
    f.write('-- ============================================================\n\n')
    f.write('SET NAMES utf8mb4;\n')
    f.write('SET FOREIGN_KEY_CHECKS = 0;\n\n')

    with conn.cursor() as cur:
        for i, table in enumerate(tables_order, 1):
            # 检查表是否存在
            cur.execute(f"SHOW TABLES LIKE '{table}'")
            if not cur.fetchone():
                print(f'⚠️  表 {table} 不存在，跳过')
                continue

            # 获取表结构
            cur.execute(f'SHOW CREATE TABLE `{table}`')
            row = cur.fetchone()
            create_sql = row[1]

            # 获取表注释
            cur.execute(f"SELECT TABLE_COMMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA='{os.getenv('DB_NAME')}' AND TABLE_NAME='{table}'")
            comment_row = cur.fetchone()
            comment = comment_row[0] if comment_row else ''

            f.write(f'-- ============================================================\n')
            f.write(f'-- {i}. {table}')
            if comment:
                f.write(f' - {comment}')
            f.write('\n')
            f.write(f'-- ============================================================\n')
            f.write(f'{create_sql};\n\n')

            print(f'✅ [{i}/{len(tables_order)}] {table}')

    f.write('SET FOREIGN_KEY_CHECKS = 1;\n\n')

    # 追加初始化数据部分
    f.write('-- ============================================================\n')
    f.write('-- 初始化数据\n')
    f.write('-- ============================================================\n\n')

    with conn.cursor() as cur:
        # 1. 默认管理员
        f.write('-- 1. 默认管理员账号（密码：Admin@2026）\n')
        cur.execute("SELECT * FROM users WHERE username='admin'")
        admin = cur.fetchone()
        if admin:
            cur.execute('SHOW COLUMNS FROM users')
            cols = [row[0] for row in cur.fetchall()]
            values = []
            for val in admin:
                if val is None:
                    values.append('NULL')
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                else:
                    escaped = str(val).replace("'", "''")
                    values.append(f"'{escaped}'")

            f.write(f"INSERT INTO users ({', '.join(cols)}) VALUES\n")
            f.write(f"({', '.join(values)});\n\n")

        # 2. 默认项目
        f.write('-- 2. 默认项目信息\n')
        cur.execute('SELECT * FROM project_info')
        projects = cur.fetchall()
        if projects:
            cur.execute('SHOW COLUMNS FROM project_info')
            cols = [row[0] for row in cur.fetchall()]
            f.write(f"INSERT INTO project_info ({', '.join(cols)}) VALUES\n")

            for i, proj in enumerate(projects):
                values = []
                for val in proj:
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    else:
                        escaped = str(val).replace("'", "''")
                        values.append(f"'{escaped}'")

                comma = ',' if i < len(projects) - 1 else ';'
                f.write(f"({', '.join(values)}){comma}\n")

            f.write('\n')

        # 3. 数据字典
        f.write('-- 3. 数据字典 - 关联阶段\n')
        cur.execute("SELECT * FROM dict_items WHERE category='关联阶段' ORDER BY sort_order")
        items = cur.fetchall()
        if items:
            cur.execute('SHOW COLUMNS FROM dict_items')
            cols = [row[0] for row in cur.fetchall()]
            f.write(f"INSERT INTO dict_items ({', '.join(cols)}) VALUES\n")

            for i, item in enumerate(items):
                values = []
                for val in item:
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    else:
                        escaped = str(val).replace("'", "''")
                        values.append(f"'{escaped}'")

                comma = ',' if i < len(items) - 1 else ';'
                f.write(f"({', '.join(values)}){comma}\n")

            f.write('\n')

        # 继续其他字典分类...
        categories = ['建设年份', 'WBS状态', 'L1阶段', '模板类型']
        for j, cat in enumerate(categories, 4):
            f.write(f'-- {j}. 数据字典 - {cat}\n')
            cur.execute(f"SELECT * FROM dict_items WHERE category='{cat}' ORDER BY sort_order")
            items = cur.fetchall()
            if items:
                cur.execute('SHOW COLUMNS FROM dict_items')
                cols = [row[0] for row in cur.fetchall()]
                f.write(f"INSERT INTO dict_items ({', '.join(cols)}) VALUES\n")

                for i, item in enumerate(items):
                    values = []
                    for val in item:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            escaped = str(val).replace("'", "''")
                            values.append(f"'{escaped}'")

                    comma = ',' if i < len(items) - 1 else ';'
                    f.write(f"({', '.join(values)}){comma}\n")

                f.write('\n')

        # L2子阶段分组
        l2_groups = [
            ('L2阶段-启动规划', 8),
            ('L2阶段-交付实施', 9),
            ('L2阶段-验收移交', 10),
            ('L2阶段-运营维护', 11)
        ]

        for cat, num in l2_groups:
            f.write(f'-- {num}. 数据字典 - {cat}\n')
            cur.execute(f"SELECT * FROM dict_items WHERE category='{cat}' ORDER BY sort_order")
            items = cur.fetchall()
            if items:
                cur.execute('SHOW COLUMNS FROM dict_items')
                cols = [row[0] for row in cur.fetchall()]
                f.write(f"INSERT INTO dict_items ({', '.join(cols)}) VALUES\n")

                for i, item in enumerate(items):
                    values = []
                    for val in item:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            escaped = str(val).replace("'", "''")
                            values.append(f"'{escaped}'")

                    comma = ',' if i < len(items) - 1 else ';'
                    f.write(f"({', '.join(values)}){comma}\n")

                f.write('\n')

conn.close()

print(f'\n✅ DDL 导出完成: {output_file}')
print(f'   共导出 {len(tables_order)} 张表')
