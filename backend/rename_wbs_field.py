#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重命名wbs_tasks表的assignee_id字段为responsible_person_id"""

import pymysql

# 数据库配置
DB_CONFIG = {
    'host': '124.222.151.69',
    'port': 3306,
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',
    'charset': 'utf8mb4'
}

def rename_field():
    """重命名字段"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = """
        ALTER TABLE wbs_tasks
        CHANGE COLUMN assignee_id responsible_person_id INT
        """

        print("执行SQL:", sql)
        cursor.execute(sql)
        conn.commit()

        print("✅ assignee_id → responsible_person_id 重命名成功")

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    rename_field()
