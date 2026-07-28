# -*- coding: utf-8 -*-
"""
表结构变更（5项）:
1. software_modules 加 project_id
2. production_lines 加 project_id
3. 新建 todos 表（含 project_id）
4. 删除 risk_tasks 表
5. 删除 templates_old_20260728 备份表
"""
import os
import sys

import pymysql
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

DB = os.getenv('DB_NAME')

conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=DB,
    charset='utf8mb4',
)


def has_column(cur, table, column):
    cur.execute(f"SHOW COLUMNS FROM `{table}` LIKE '{column}'")
    return cur.fetchone() is not None


def has_table(cur, table):
    cur.execute(f"SHOW TABLES LIKE '{table}'")
    return cur.fetchone() is not None


def add_project_id(cur, table, count_label):
    """给表加 project_id + 外键 + 索引，存量回填 1"""
    if has_column(cur, table, 'project_id'):
        print(f'  ⚠️  {table}.project_id 已存在，跳过')
        return

    cur.execute(
        f"ALTER TABLE `{table}` "
        f"ADD COLUMN project_id INT NOT NULL DEFAULT 1 COMMENT '所属项目' AFTER id"
    )
    cur.execute(
        f"ALTER TABLE `{table}` "
        f"ADD FOREIGN KEY (project_id) REFERENCES project_info(id)"
    )
    cur.execute(f"ALTER TABLE `{table}` ADD INDEX idx_project (project_id)")
    conn.commit()

    cur.execute(f'SELECT COUNT(*) FROM `{table}` WHERE project_id = 1')
    print(f'  ✅ {table} 已加 project_id，{cur.fetchone()[0]} 条存量回填为 1')


TODOS_DDL = """
CREATE TABLE todos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL DEFAULT 1 COMMENT '所属项目',
    parent_id INT COMMENT '父待办ID，支持多级树形结构，NULL为顶级',
    title VARCHAR(200) NOT NULL COMMENT '任务标题',
    description TEXT COMMENT '任务描述',
    priority ENUM('高','中','低') DEFAULT '中' COMMENT '优先级',
    due_date DATE COMMENT '截止日期',
    status ENUM('待处理','已完成') DEFAULT '待处理' COMMENT '状态',
    assignee_id INT COMMENT '负责人ID',
    creator_id INT COMMENT '创建人ID',
    source_type ENUM('project','wbs','system') DEFAULT 'project' COMMENT '来源类型',
    source_id INT COMMENT '来源记录ID',
    transferred_from_id INT COMMENT '转办来源人ID',
    completed_at DATETIME COMMENT '完成时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project_info(id),
    FOREIGN KEY (parent_id) REFERENCES todos(id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (transferred_from_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_project (project_id),
    INDEX idx_parent (parent_id),
    INDEX idx_assignee (assignee_id),
    INDEX idx_status (status)
) COMMENT='待办表' DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""


def drop_table_safe(cur, table):
    """删表前二次确认为空"""
    if not has_table(cur, table):
        print(f'  ⚠️  {table} 不存在，跳过')
        return

    cur.execute(f'SELECT COUNT(*) FROM `{table}`')
    cnt = cur.fetchone()[0]
    if cnt > 0:
        print(f'  ❌ {table} 有 {cnt} 条数据，拒绝删除！')
        return

    cur.execute(f'DROP TABLE `{table}`')
    conn.commit()
    print(f'  ✅ {table} 已删除（0 条）')


print('开始执行表结构变更...\n')

try:
    with conn.cursor() as cur:
        print('[1/5] software_modules 加 project_id')
        add_project_id(cur, 'software_modules', '4')

        print('\n[2/5] production_lines 加 project_id')
        add_project_id(cur, 'production_lines', '3')

        print('\n[3/5] 新建 todos 表')
        if has_table(cur, 'todos'):
            print('  ⚠️  todos 表已存在，跳过')
        else:
            cur.execute(TODOS_DDL)
            conn.commit()
            print('  ✅ todos 表已创建')

        print('\n[4/5] 删除 risk_tasks 表')
        drop_table_safe(cur, 'risk_tasks')

        print('\n[5/5] 删除 templates_old_20260728 备份表')
        drop_table_safe(cur, 'templates_old_20260728')

        # 验证
        print('\n===== 验证 =====')
        for t in ['software_modules', 'production_lines', 'todos']:
            ok = has_column(cur, t, 'project_id') if has_table(cur, t) else False
            print(f'  {t:<22} project_id: {"✅" if ok else "❌"}')
        for t in ['risk_tasks', 'templates_old_20260728']:
            gone = not has_table(cur, t)
            print(f'  {t:<22} 已删除: {"✅" if gone else "❌"}')

    print('\n✅ 全部变更完成！')

except Exception as e:
    print(f'\n❌ 变更失败: {e}')
    conn.rollback()
    sys.exit(1)

finally:
    conn.close()
