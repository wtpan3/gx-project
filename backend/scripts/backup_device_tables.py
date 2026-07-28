#!/usr/bin/env python3
"""备份device_systems和devices表"""

import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': '124.222.151.69',
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',
    'charset': 'utf8mb4'
}

def backup_tables():
    conn = pymysql.connect(**DB_CONFIG)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'F:/claude code/Projectmanage/gx-project/ai_workspace/backup_device_tables_{timestamp}.sql'

    try:
        with conn.cursor() as cur:
            # 备份device_systems
            cur.execute("SELECT * FROM device_systems")
            ds_data = cur.fetchall()

            # 备份devices的system_id列（即将删除）
            cur.execute("SELECT id, system_id, device_name FROM devices WHERE system_id IS NOT NULL LIMIT 10")
            d_system_refs = cur.fetchall()

            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(f"-- 备份时间: {timestamp}\n")
                f.write(f"-- device_systems表: {len(ds_data)}条\n")
                f.write(f"-- devices.system_id引用: 前10条样本\n\n")

                f.write("-- device_systems数据:\n")
                for row in ds_data:
                    f.write(f"{row}\n")

                f.write("\n-- devices.system_id样本:\n")
                for row in d_system_refs:
                    f.write(f"{row}\n")

            print(f"✅ 备份完成: {backup_file}")
            print(f"   device_systems: {len(ds_data)}条")
            print(f"   devices.system_id样本: {len(d_system_refs)}条")

    finally:
        conn.close()

if __name__ == '__main__':
    backup_tables()
