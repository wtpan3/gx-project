#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创建task_attachments表（任务佐证材料）— 全新空表,可逆(DROP即回滚)"""

import pymysql

DB_CONFIG = {
    'host': '124.222.151.69',
    'port': 3306,
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',
    'charset': 'utf8mb4'
}


def create_table():
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 检查表是否已存在
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = 'gx_project_dev' AND TABLE_NAME = 'task_attachments'
        """)
        if cursor.fetchone()[0] > 0:
            print("ℹ️  task_attachments 表已存在，跳过创建")
            return

        create_sql = """
        CREATE TABLE task_attachments (
            id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
            task_id INT NOT NULL COMMENT '关联任务ID',
            file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
            file_path VARCHAR(500) NOT NULL COMMENT '存储路径(相对uploads)',
            file_size INT COMMENT '文件大小(字节)',
            description VARCHAR(500) COMMENT '材料说明',
            uploaded_by INT COMMENT '上传人ID',
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
            INDEX idx_task_id (task_id),
            FOREIGN KEY (task_id) REFERENCES wbs_tasks(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务佐证材料'
        """
        print("执行SQL:\n", create_sql)
        cursor.execute(create_sql)
        conn.commit()
        print("✅ task_attachments 表创建成功")

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    create_table()
