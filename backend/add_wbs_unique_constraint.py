#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为wbs_tasks表的task_code字段添加唯一索引"""

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

def add_unique_constraint():
    """为task_code添加唯一索引"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 先检查是否有重复数据
        check_sql = """
        SELECT task_code, COUNT(*) as cnt
        FROM wbs_tasks
        WHERE task_code IS NOT NULL AND task_code != ''
        GROUP BY task_code
        HAVING cnt > 1
        """

        cursor.execute(check_sql)
        duplicates = cursor.fetchall()

        if duplicates:
            print(f"⚠️  发现 {len(duplicates)} 个重复的task_code:")
            for task_code, count in duplicates:
                print(f"   - {task_code}: {count}条")

            # 清理重复数据：保留ID最小的，删除其他
            print("\n🔧 开始清理重复数据...")
            for task_code, _ in duplicates:
                delete_sql = """
                DELETE FROM wbs_tasks
                WHERE task_code = %s
                AND id NOT IN (
                    SELECT min_id FROM (
                        SELECT MIN(id) as min_id
                        FROM wbs_tasks
                        WHERE task_code = %s
                    ) AS tmp
                )
                """
                cursor.execute(delete_sql, (task_code, task_code))
                print(f"   ✓ 清理 {task_code} 的重复数据")

            conn.commit()
            print("✅ 重复数据清理完成\n")

        # 添加唯一索引
        add_index_sql = """
        ALTER TABLE wbs_tasks
        ADD UNIQUE INDEX idx_task_code (task_code)
        """

        print("执行SQL:", add_index_sql)
        cursor.execute(add_index_sql)
        conn.commit()

        print("✅ wbs_tasks.task_code 唯一索引添加成功")

    except pymysql.err.OperationalError as e:
        if "Duplicate key name" in str(e):
            print("ℹ️  索引已存在，无需重复创建")
        else:
            print(f"❌ 执行失败: {e}")
            if conn:
                conn.rollback()
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    add_unique_constraint()
