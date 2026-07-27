"""
风险管理轻量级模型迁移 - V2.3
删除probability/impact/response_deadline，新增progress_note
保留risk_level（手工评定）
状态枚举保持为：已识别/应对中/已关闭
"""

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
    cursor = conn.cursor()

    try:
        print("=" * 60)
        print("  风险管理轻量级模型迁移 - V2.3")
        print("=" * 60)

        # 1. 删除字段
        print("\n[1/3] 删除 probability、impact、response_deadline 字段...")

        for col in ['probability', 'impact', 'response_deadline']:
            try:
                cursor.execute(f"ALTER TABLE risks DROP COLUMN {col}")
                print(f"  * 删除 {col}")
            except Exception as e:
                if 'Unknown column' in str(e) or "Can't DROP" in str(e):
                    print(f"  - {col} 已不存在，跳过")
                else:
                    raise

        # 2. response_strategy可能叫response_measure，统一改名
        print("\n[2/3] 统一字段名 response_strategy...")

        cursor.execute("SHOW COLUMNS FROM risks LIKE 'response%'")
        response_cols = [row[0] for row in cursor.fetchall()]

        if 'response_measure' in response_cols:
            cursor.execute("ALTER TABLE risks CHANGE response_measure response_strategy TEXT COMMENT '应对措施'")
            print("  * response_measure -> response_strategy")
        elif 'response_strategy' in response_cols:
            print("  - response_strategy 已存在，跳过")

        # 3. 新增 progress_note 字段
        print("\n[3/3] 新增 progress_note 字段...")

        try:
            cursor.execute("""
                ALTER TABLE risks
                ADD COLUMN progress_note TEXT COMMENT '进展说明（自由文本）'
                AFTER response_strategy
            """)
            print("  * 新增 progress_note")
        except Exception as e:
            if 'Duplicate column' in str(e):
                print("  - progress_note 已存在，跳过")
            else:
                raise

        conn.commit()

        print("\n" + "=" * 60)
        print("  迁移完成")
        print("=" * 60)

        # 验证
        print("\n验证表结构...")
        cursor.execute("DESCRIBE risks")
        fields = cursor.fetchall()

        print("\n当前字段列表：")
        for field in fields:
            field_name = field[0]
            field_type = field[1]
            print(f"  - {field_name}: {field_type}")

        print("\n迁移成功完成")

    except Exception as e:
        conn.rollback()
        print(f"\n迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    migrate()
