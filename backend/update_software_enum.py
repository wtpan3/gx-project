#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新software_modules表的phase字段枚举值"""

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

def update_software_enum():
    """修改software_modules.phase字段枚举"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = """
        ALTER TABLE software_modules
        MODIFY phase ENUM('需求收集','需求确认','软件开发','软件测试','软件部署','上线运行') NOT NULL
        """

        print("执行SQL:", sql)
        cursor.execute(sql)
        conn.commit()

        print("✅ software_modules.phase 枚举值更新成功")

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    update_software_enum()
