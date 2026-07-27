#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为原有叶子任务创建缺失的L2父节点
"""
import pymysql
from datetime import date

def main():
    conn = pymysql.connect(
        host='124.222.151.69',
        user='root',
        password='GX2026!root',
        database='gx_project_dev',
        charset='utf8mb4'
    )
    
    try:
        cursor = conn.cursor()
        
        # 1. 获取所有叶子任务的唯一L1/L2组合
        cursor.execute('''
            SELECT DISTINCT project_phase_l1, sub_phase_l2 
            FROM wbs_tasks 
            WHERE work_content_l4 != ''
            ORDER BY project_phase_l1, sub_phase_l2
        ''')
        l1_l2_combinations = cursor.fetchall()
        print(f'找到 {len(l1_l2_combinations)} 个需要创建L2父节点的组合')
        
        # 2. 检查哪些L2节点已存在
        existing_l2 = set()
        cursor.execute('''
            SELECT project_phase_l1, sub_phase_l2 
            FROM wbs_tasks 
            WHERE sub_phase_l2 != '' AND work_content_l4 = ''
        ''')
        for row in cursor.fetchall():
            existing_l2.add((row[0], row[1]))
        
        # 3. 为每个缺失的L2组合创建父节点
        created = 0
        for l1, l2 in l1_l2_combinations:
            if (l1, l2) in existing_l2:
                print(f'  跳过已存在: L1={l1}, L2={l2}')
                continue
            
            # 获取该L1/L2下所有叶子任务的日期范围
            cursor.execute('''
                SELECT MIN(plan_start_date), MAX(plan_end_date)
                FROM wbs_tasks
                WHERE project_phase_l1 = %s AND sub_phase_l2 = %s AND work_content_l4 != ''
            ''', (l1, l2))
            date_range = cursor.fetchone()
            min_start = date_range[0] if date_range[0] else date.today()
            max_end = date_range[1] if date_range[1] else date.today()
            
            # 生成task_code
            task_code = f'L2-OLD-{created+1:03d}'
            
            # 插入L2父节点
            cursor.execute('''
                INSERT INTO wbs_tasks (
                    task_code, construction_year,
                    project_phase_l1, sub_phase_l2, task_package_l3, work_content_l4,
                    priority, status,
                    plan_start_date, plan_end_date,
                    progress, is_orphan
                ) VALUES (
                    %s, '2026',
                    %s, %s, '', '',
                    '中', '待开始',
                    %s, %s,
                    0, 0
                )
            ''', (task_code, l1, l2, min_start, max_end))
            
            created += 1
            print(f'  创建L2节点: {task_code}, L1={l1}, L2={l2}')
        
        conn.commit()
        print(f'\n创建完成: {created} 个L2父节点')
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()
