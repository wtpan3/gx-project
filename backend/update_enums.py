"""更新数据库枚举值以匹配文档要求"""
import pymysql
import sys

# 强制使用UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 数据库连接配置
DB_CONFIG = {
    'host': '124.222.151.69',
    'port': 3306,
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',
    'charset': 'utf8mb4'
}

def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        print("开始更新数据库枚举值...")

        # 1. 更新 devices 表的枚举值
        print("\n1. 更新 devices 表...")

        # 先更新现有数据
        cursor.execute("UPDATE devices SET source = '三方外采' WHERE source = '外部采购'")
        print(f"   更新设备来源: {cursor.rowcount} 条")

        cursor.execute("UPDATE devices SET source = '库存设备' WHERE source = '自主研发'")
        print(f"   更新设备来源: {cursor.rowcount} 条")

        cursor.execute("UPDATE devices SET status = '待发货' WHERE status = '待采购'")
        print(f"   更新设备状态: {cursor.rowcount} 条")

        cursor.execute("UPDATE devices SET status = '运行中' WHERE status = '已验收'")
        print(f"   更新设备状态: {cursor.rowcount} 条")

        # 修改列定义
        cursor.execute("""
            ALTER TABLE devices
            MODIFY COLUMN source ENUM('三方外采', '库存设备'),
            MODIFY COLUMN status ENUM('待发货', '已到货', '已安装', '已调试', '运行中')
        """)
        print("   [OK] 已更新 devices 表枚举定义")

        # 2. 更新 risks 表
        print("\n2. 更新 risks 表...")
        cursor.execute("UPDATE risks SET status = '已识别' WHERE status = '未处理'")
        print(f"   更新风险状态: {cursor.rowcount} 条")

        cursor.execute("UPDATE risks SET status = '应对中' WHERE status = '处理中'")
        print(f"   更新风险状态: {cursor.rowcount} 条")

        cursor.execute("""
            ALTER TABLE risks
            MODIFY COLUMN status ENUM('已识别', '应对中', '已关闭')
        """)
        print("   [OK] 已更新 risks 表枚举定义")

        # 3. 更新 schools 表字段名（检查是否需要）
        print("\n3. 检查 schools 表...")
        cursor.execute("SHOW COLUMNS FROM schools LIKE 'is_priority'")
        if cursor.fetchone():
            cursor.execute("""
                ALTER TABLE schools
                CHANGE COLUMN is_priority is_key TINYINT DEFAULT 0
            """)
            print("   [OK] 已将 is_priority 改为 is_key")
        else:
            print("   [SKIP] 字段已经是 is_key，无需修改")

        # 4. 更新 software_modules 表
        print("\n4. 更新 software_modules 表...")
        cursor.execute("SHOW COLUMNS FROM software_modules LIKE 'online_status'")
        if cursor.fetchone():
            cursor.execute("""
                ALTER TABLE software_modules
                CHANGE COLUMN online_status phase ENUM('需求收集', '需求确认', '软件开发', '软件测试', '软件部署', '上线运行') NOT NULL
            """)
            print("   [OK] 已将 online_status 改为 phase")
        else:
            print("   [SKIP] 字段已经是 phase")

        # 检查并添加 expected_completion_date 字段
        cursor.execute("SHOW COLUMNS FROM software_modules LIKE 'expected_completion_date'")
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE software_modules
                ADD COLUMN expected_completion_date DATE AFTER progress
            """)
            print("   [OK] 已新增 expected_completion_date 字段")
        else:
            print("   [SKIP] expected_completion_date 字段已存在")

        conn.commit()
        print("\n[SUCCESS] 所有更新完成！")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] 错误: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
