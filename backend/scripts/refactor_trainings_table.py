# -*- coding: utf-8 -*-
"""重构培训表：删除 training_schools 关联表，将 school_id 合并到 trainings 表"""
import os
import sys

import pymysql
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    charset='utf8mb4',
)

print('开始执行培训表重构...\n')

try:
    with conn.cursor() as cur:
        # 1. 检查 trainings 表是否已有 school_id
        cur.execute("SHOW COLUMNS FROM trainings LIKE 'school_id'")
        if cur.fetchone():
            print('⚠️  trainings 表已有 school_id 字段，跳过添加')
        else:
            print('[1/4] 添加 trainings.school_id 字段...')
            cur.execute("""
                ALTER TABLE trainings
                ADD COLUMN school_id INT COMMENT '关联学校（区级培训为NULL）' AFTER is_district
            """)
            conn.commit()
            print('  ✅ 成功\n')

        # 2. 添加外键约束
        print('[2/4] 添加外键约束 trainings.school_id → schools.id...')
        cur.execute("""
            SELECT CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA='gx_project_dev'
            AND TABLE_NAME='trainings'
            AND COLUMN_NAME='school_id'
        """)
        if cur.fetchone():
            print('  ⚠️  外键约束已存在，跳过\n')
        else:
            cur.execute("""
                ALTER TABLE trainings
                ADD FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL
            """)
            conn.commit()
            print('  ✅ 成功\n')

        # 3. 检查 training_schools 表是否存在
        cur.execute("SHOW TABLES LIKE 'training_schools'")
        if not cur.fetchone():
            print('[3/4] training_schools 表不存在，跳过删除\n')
        else:
            # 检查是否有数据
            cur.execute("SELECT COUNT(*) FROM training_schools")
            count = cur.fetchone()[0]

            if count > 0:
                print(f'⚠️  training_schools 表有 {count} 条数据，需要先迁移！')
                print('   请手动处理数据迁移后再删除表。')
            else:
                print('[3/4] 删除 training_schools 表（0条数据）...')
                cur.execute("DROP TABLE training_schools")
                conn.commit()
                print('  ✅ 成功\n')

        # 4. 验证
        print('[4/4] 验证表结构...')
        cur.execute("SHOW COLUMNS FROM trainings LIKE 'school_id'")
        school_id_col = cur.fetchone()

        cur.execute("SHOW TABLES LIKE 'training_schools'")
        ts_exists = cur.fetchone()

        if school_id_col and not ts_exists:
            print('  ✅ trainings 表有 school_id 字段')
            print('  ✅ training_schools 表已删除')
            print('\n✅ 重构完成！')
        else:
            print('  ⚠️  验证未完全通过，请检查')

except Exception as e:
    print(f'\n❌ 重构失败: {e}')
    conn.rollback()
    sys.exit(1)

finally:
    conn.close()
