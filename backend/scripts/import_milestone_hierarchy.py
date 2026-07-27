#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Excel导入项目里程碑计划，填充L1/L2层级记录
输入：F:/claude code/项目里程碑计划.xlsx
输出：往wbs_tasks插入L1父记录和L2子记录
"""

import pymysql
import openpyxl
from datetime import datetime

DB_CONFIG = {
    'host': '124.222.151.69',
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',
    'charset': 'utf8mb4'
}

EXCEL_PATH = r'F:/claude code/项目里程碑计划.xlsx'

def import_milestones():
    # 1. 读取Excel
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb.active
    
    rows = list(ws.iter_rows(min_row=2, values_only=True))  # 跳过表头
    
    print(f'读取到 {len(rows)} 行数据')
    
    # 2. 解析数据，去重L1
    l1_set = set()
    l2_records = []
    
    for row in rows:
        if not row[0] or not row[1] or not row[2]:  # 跳过空行
            continue
        
        phase_group, l1, l2, start, end = row[:5]
        l1_set.add((phase_group, l1))
        
        l2_records.append({
            'phase_group': phase_group,
            'l1': l1,
            'l2': l2,
            'start': start.date() if isinstance(start, datetime) else start,
            'end': end.date() if isinstance(end, datetime) else end
        })
    
    print(f'唯一L1数: {len(l1_set)}, L2记录数: {len(l2_records)}')
    
    # 3. 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 先删除现有的L1/L2虚拟记录（work_content_l4为空的）
        cursor.execute('DELETE FROM wbs_tasks WHERE work_content_l4 = ""')
        deleted = cursor.rowcount
        print(f'清理旧L1/L2记录: {deleted}条')
        
        # 4. 插入L1记录
        l1_insert_sql = '''
            INSERT INTO wbs_tasks (
                task_code, construction_year,
                project_phase_l1, sub_phase_l2, task_package_l3, work_content_l4,
                priority, status,
                plan_start_date, plan_end_date,
                progress, is_orphan
            ) VALUES (
                %s, %s,
                %s, '', '', '',
                '中', '待开始',
                %s, %s,
                0, 0
            )
        '''
        
        l1_list = sorted(l1_set, key=lambda x: (x[0], x[1]))
        for idx, (phase_group, l1) in enumerate(l1_list, start=1):
            # 该L1下所有L2的日期范围
            l2_dates = [r for r in l2_records if r['l1'] == l1]
            min_start = min(r['start'] for r in l2_dates)
            max_end = max(r['end'] for r in l2_dates)
            
            task_code = f'L1-{idx:03d}'
            cursor.execute(l1_insert_sql, (
                task_code, '2026',
                l1, 
                min_start, max_end
            ))
        
        print(f'插入 {len(l1_list)} 条L1记录')

        # 5. 插入L2记录
        l2_insert_sql = '''
            INSERT INTO wbs_tasks (
                task_code, construction_year,
                project_phase_l1, sub_phase_l2, task_package_l3, work_content_l4,
                priority, status,
                plan_start_date, plan_end_date,
                progress, is_orphan
            ) VALUES (
                %s, %s,
                %s, %s, '', '',
                '中', '待开始',
                %s, %s,
                0, 0
            )
        '''


        for idx, rec in enumerate(l2_records, start=1):
            task_code = f'L2-{idx:03d}'
            cursor.execute(l2_insert_sql, (
                task_code, '2026',
                rec['l1'], rec['l2'],
                rec['start'], rec['end']
            ))
        
        print(f'插入 {len(l2_records)} 条L2记录')
        
        conn.commit()
        print('\n导入成功')
        
        # 验证
        cursor.execute('SELECT COUNT(*) FROM wbs_tasks WHERE work_content_l4 = ""')
        virtual_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM wbs_tasks WHERE work_content_l4 != ""')
        leaf_count = cursor.fetchone()[0]
        
        print(f'\n当前wbs_tasks统计:')
        print(f'  L1/L2虚拟记录: {virtual_count}条')
        print(f'  L4/L5叶子任务: {leaf_count}条')
        print(f'  总计: {virtual_count + leaf_count}条')
        
    except Exception as e:
        conn.rollback()
        print(f'\n导入失败: {e}')
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    import_milestones()
