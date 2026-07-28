# -*- coding: utf-8 -*-
"""检查 templates 表在开发库的实际结构与数据量"""
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

with conn.cursor() as cur:
    cur.execute("SHOW TABLES LIKE '%template%'")
    tables = [r[0] for r in cur.fetchall()]
    print('模板相关表:', tables if tables else '无')

    for t in tables:
        print(f'\n===== {t} 结构 =====')
        cur.execute(f'SHOW FULL COLUMNS FROM `{t}`')
        for row in cur.fetchall():
            print(f'  {row[0]:<20} {row[1]:<70} null={row[3]:<4} {row[8]}')
        cur.execute(f'SELECT COUNT(*) FROM `{t}`')
        print(f'  行数: {cur.fetchone()[0]}')

conn.close()
