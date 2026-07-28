#!/usr/bin/env python3
"""检查schools表中实际使用的project_status值"""

import pymysql
from collections import Counter

# 数据库配置
DB_CONFIG = {
    'host': '124.222.151.69',
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',
    'charset': 'utf8mb4'
}

def check_school_status():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            # 查询所有学校的状态
            cursor.execute("SELECT id, full_name, project_status FROM schools ORDER BY id")
            schools = cursor.fetchall()

            # 统计状态分布
            status_counter = Counter()
            print("\n=== 学校状态明细 ===")
            print(f"{'ID':<5} {'学校名称':<30} {'当前状态':<10}")
            print("-" * 50)
            for school_id, name, status in schools:
                status_display = status if status else 'NULL'
                print(f"{school_id:<5} {name:<30} {status_display:<10}")
                status_counter[status_display] += 1

            print("\n=== 状态统计 ===")
            for status, count in status_counter.items():
                print(f"{status}: {count}所学校")

            print(f"\n总计: {len(schools)}所学校")

    finally:
        conn.close()

if __name__ == '__main__':
    check_school_status()
