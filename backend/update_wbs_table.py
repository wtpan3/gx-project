#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新wbs_tasks表结构，添加priority字段"""

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

def update_wbs_table():
    """更新wbs_tasks表结构"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 检查priority字段是否存在
        check_sql = """
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'gx_project_dev'
        AND TABLE_NAME = 'wbs_tasks'
        AND COLUMN_NAME = 'priority'
        """
        cursor.execute(check_sql)
        exists = cursor.fetchone()[0] > 0

        if not exists:
            # 添加priority字段
            add_priority_sql = """
            ALTER TABLE wbs_tasks
            ADD COLUMN priority ENUM('高','中','低') NOT NULL DEFAULT '中'
            AFTER work_detail_l5
            """
            print("执行SQL:", add_priority_sql)
            cursor.execute(add_priority_sql)
            print("✅ 添加priority字段成功")
        else:
            print("ℹ️  priority字段已存在")

        # 检查并修改status字段枚举值
        check_status_sql = """
        SELECT COLUMN_TYPE FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'gx_project_dev'
        AND TABLE_NAME = 'wbs_tasks'
        AND COLUMN_NAME = 'status'
        """
        cursor.execute(check_status_sql)
        current_type = cursor.fetchone()[0]

        if '待暂停' not in current_type or '已延期' in current_type:
            modify_status_sql = """
            ALTER TABLE wbs_tasks
            MODIFY COLUMN status ENUM('待开始','进行中','已完成','已暂停') NOT NULL DEFAULT '待开始'
            """
            print("执行SQL:", modify_status_sql)
            cursor.execute(modify_status_sql)
            print("✅ 修改status枚举值成功")
        else:
            print("ℹ️  status枚举值已是最新")

        conn.commit()
        print("\n✅ wbs_tasks表结构更新完成")

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    update_wbs_table()
