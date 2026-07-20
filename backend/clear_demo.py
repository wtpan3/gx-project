"""清空演示数据(保留用户表)"""
import pymysql
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_CONFIG = {
    'host': '124.222.151.69',
    'port': 3306,
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

try:
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    tables = ['risks', 'wbs_tasks', 'devices', 'software_modules',
              'production_lines', 'device_systems', 'schools']
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table}")
        print(f"[OK] 已清空 {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    print("\n[SUCCESS] 演示数据已清空")
except Exception as e:
    print(f"[ERROR] {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
