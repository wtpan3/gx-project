#!/usr/bin/env python3
"""对比device_systems和devices表的字段重复情况"""

import pymysql

DB_CONFIG = {
    'host': '124.222.151.69',
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',
    'charset': 'utf8mb4'
}

def compare_tables():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # device_systems字段
            print("=" * 60)
            print("device_systems 表结构（6条数据）:")
            print("=" * 60)
            cur.execute("SHOW COLUMNS FROM device_systems")
            ds_cols = [row[0] for row in cur.fetchall()]
            print(f"字段: {', '.join(ds_cols)}\n")

            cur.execute("SELECT * FROM device_systems LIMIT 3")
            print("前3条数据:")
            for row in cur.fetchall():
                print(row)

            # devices字段
            print("\n" + "=" * 60)
            print("devices 表结构（1240条数据）:")
            print("=" * 60)
            cur.execute("SHOW COLUMNS FROM devices")
            d_cols = [row[0] for row in cur.fetchall()]
            print(f"字段: {', '.join(d_cols)}\n")

            cur.execute("SELECT id, project_name, device_name, brand, model, type, unit, school_id, status FROM devices LIMIT 3")
            print("前3条数据（部分字段）:")
            for row in cur.fetchall():
                print(row)

            # 字段对比
            print("\n" + "=" * 60)
            print("字段对比分析:")
            print("=" * 60)

            ds_set = set(ds_cols)
            d_set = set(d_cols)

            common = ds_set & d_set
            print(f"\n重复字段（{len(common)}个）:")
            print(', '.join(sorted(common)))

            ds_only = ds_set - d_set
            print(f"\ndevice_systems独有（{len(ds_only)}个）:")
            print(', '.join(sorted(ds_only)))

            d_only = d_set - ds_set
            print(f"\ndevices独有（{len(d_only)}个）:")
            print(', '.join(sorted(d_only)))

            # 核心问题分析
            print("\n" + "=" * 60)
            print("核心问题:")
            print("=" * 60)
            print("1. devices有system_id外键指向device_systems")
            print("2. 两表都有：project_name, construction_year, device_name, brand, model, params, type, unit")
            print("3. devices的这些字段是从device_systems复制的快照")
            print("4. 如果删device_systems，devices的system_id外键需要删除")

    finally:
        conn.close()

if __name__ == '__main__':
    compare_tables()
