#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""方案A迁移：wbs_tasks 加 parent_id + progress 列，并回填现有数据。

- parent_id: 自关联外键，按 L1-L4 路径前缀匹配现有数据的父任务
- progress:  int 默认0，回填按状态映射(已完成100/进行中50/待补材料60/已延期40/待开始0)
幂等：列已存在则跳过 ADD；回填对 NULL 值执行。
"""
import pymysql
from app.config import config

STATUS_PCT = {'已完成': 100, '进行中': 50, '待补材料': 60, '已延期': 40, '待开始': 0}


def get_conn():
    return pymysql.connect(
        host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER,
        password=config.DB_PASSWORD, database=config.DB_NAME, charset='utf8mb4'
    )


def col_exists(cursor, col):
    cursor.execute("""
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME='wbs_tasks' AND COLUMN_NAME=%s
    """, (config.DB_NAME, col))
    return cursor.fetchone()[0] > 0


def task_level(row):
    """按最深非空层级字段推算 level。row 为 dict。"""
    if row.get('work_detail_l5'):
        return 5
    if row.get('work_content_l4'):
        return 4
    if row.get('task_package_l3'):
        return 3
    if row.get('sub_phase_l2'):
        return 2
    return 1


def task_path(row, level):
    fields = [
        row.get('project_phase_l1') or '',
        row.get('sub_phase_l2') or '',
        row.get('task_package_l3') or '',
        row.get('work_content_l4') or '',
        row.get('work_detail_l5') or '',
    ]
    return tuple(fields[:level])


def main():
    conn = get_conn()
    try:
        cur = conn.cursor()

        # 1. 加列(幂等)
        if not col_exists(cur, 'parent_id'):
            print("[RUN] ADD COLUMN parent_id ...")
            cur.execute("ALTER TABLE wbs_tasks ADD COLUMN parent_id INT NULL")
            cur.execute("ALTER TABLE wbs_tasks ADD CONSTRAINT fk_wbs_parent FOREIGN KEY (parent_id) REFERENCES wbs_tasks(id)")
        else:
            print("[SKIP] parent_id 已存在")

        if not col_exists(cur, 'progress'):
            print("[RUN] ADD COLUMN progress ...")
            cur.execute("ALTER TABLE wbs_tasks ADD COLUMN progress INT NOT NULL DEFAULT 0")
        else:
            print("[SKIP] progress 已存在")
        conn.commit()

        # 2. 读取全部活动任务(dict 游标)
        dcur = conn.cursor(pymysql.cursors.DictCursor)
        dcur.execute("SELECT * FROM wbs_tasks WHERE is_orphan=0")
        rows = dcur.fetchall()
        print(f"[INFO] 活动任务 {len(rows)} 条")

        # 3. 回填 progress(仅当前为0且状态非待开始,避免覆盖真实值)
        prog_updates = 0
        for r in rows:
            pct = STATUS_PCT.get(r['status'], 0)
            if (r.get('progress') or 0) == 0 and pct != 0:
                cur.execute("UPDATE wbs_tasks SET progress=%s WHERE id=%s", (pct, r['id']))
                prog_updates += 1
        print(f"[OK] progress 回填 {prog_updates} 条")

        # 4. 回填 parent_id(路径前缀匹配同建设年份的上一级)
        parent_updates = 0
        for r in rows:
            lvl = task_level(r)
            if lvl <= 1:
                continue  # L1 无父
            parent_path = task_path(r, lvl - 1)
            # 找同年份、level=lvl-1、路径匹配的任务
            for cand in rows:
                if cand['id'] == r['id']:
                    continue
                if cand.get('construction_year') != r.get('construction_year'):
                    continue
                if task_level(cand) == lvl - 1 and task_path(cand, lvl - 1) == parent_path:
                    cur.execute("UPDATE wbs_tasks SET parent_id=%s WHERE id=%s", (cand['id'], r['id']))
                    parent_updates += 1
                    break
        conn.commit()
        print(f"[OK] parent_id 回填 {parent_updates} 条")

        # 5. 验证
        cur.execute("SELECT COUNT(*) FROM wbs_tasks WHERE is_orphan=0 AND parent_id IS NOT NULL")
        print(f"[VERIFY] 有父任务的记录: {cur.fetchone()[0]}")
        cur.execute("SELECT COUNT(*) FROM wbs_tasks WHERE is_orphan=0 AND progress>0")
        print(f"[VERIFY] progress>0 的记录: {cur.fetchone()[0]}")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
