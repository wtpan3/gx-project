#!/usr/bin/env python3
"""删除device_systems表的数据库迁移脚本"""

import pymysql

DB_CONFIG = {
    'host': '124.222.151.69',
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',
    'charset': 'utf8mb4'
}

def migrate():
    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            print("开始数据库迁移...")

            # 步骤1：添加system_name字段到devices
            print("\n[1/6] 添加devices.system_name字段...")
            cur.execute("""
                ALTER TABLE devices
                ADD COLUMN system_name VARCHAR(100) COMMENT '系统名称'
                AFTER construction_year
            """)
            print("✅ 已添加system_name字段")

            # 步骤2：从device_systems回填system_name到devices
            print("\n[2/6] 从device_systems回填system_name到devices...")
            cur.execute("""
                UPDATE devices d
                INNER JOIN device_systems ds ON d.system_id = ds.id
                SET d.system_name = ds.system_name
            """)
            affected = cur.rowcount
            print(f"✅ 已更新{affected}条devices记录")

            # 步骤3：查找外键名称
            print("\n[3/6] 查找devices.system_id的外键名...")
            cur.execute("""
                SELECT CONSTRAINT_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = 'gx_project_dev'
                AND TABLE_NAME = 'devices'
                AND COLUMN_NAME = 'system_id'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            fk_result = cur.fetchone()

            if fk_result:
                fk_name = fk_result[0]
                print(f"✅ 找到外键: {fk_name}")

                # 步骤4：删除外键约束
                print(f"\n[4/6] 删除外键约束 {fk_name}...")
                cur.execute(f"ALTER TABLE devices DROP FOREIGN KEY {fk_name}")
                print("✅ 已删除外键约束")
            else:
                print("⚠️  未找到外键约束，可能已经不存在")

            # 步骤5：删除system_id列
            print("\n[5/6] 删除devices.system_id列...")
            cur.execute("ALTER TABLE devices DROP COLUMN system_id")
            print("✅ 已删除system_id列")

            # 步骤6：删除device_systems表
            print("\n[6/6] 删除device_systems表...")
            cur.execute("DROP TABLE device_systems")
            print("✅ 已删除device_systems表")

            # 提交事务
            conn.commit()
            print("\n" + "="*60)
            print("✅ 数据库迁移完成！")
            print("="*60)

            # 验证结果
            print("\n验证结果:")
            cur.execute("SHOW TABLES LIKE 'device_systems'")
            if cur.fetchone():
                print("❌ device_systems表仍存在")
            else:
                print("✅ device_systems表已删除")

            cur.execute("SHOW COLUMNS FROM devices LIKE 'system_name'")
            if cur.fetchone():
                print("✅ devices.system_name字段存在")
            else:
                print("❌ devices.system_name字段不存在")

            cur.execute("SHOW COLUMNS FROM devices LIKE 'system_id'")
            if cur.fetchone():
                print("❌ devices.system_id字段仍存在")
            else:
                print("✅ devices.system_id字段已删除")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
