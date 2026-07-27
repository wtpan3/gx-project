#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关联WBS任务的层级关系
将L4/L5叶子任务关联到对应的L2父节点
"""
import pymysql

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
        
        # 1. 获取所有L2节点 (有sub_phase_l2且work_content_l4为空)
        cursor.execute('''
            SELECT id, project_phase_l1, sub_phase_l2 
            FROM wbs_tasks 
            WHERE sub_phase_l2 != '' AND work_content_l4 = ''
        ''')
        l2_nodes = cursor.fetchall()
        print(f'找到 {len(l2_nodes)} 个L2节点')
        
        # 2. 为每个L4/L5叶子任务找到匹配的L2父节点
        cursor.execute('''
            SELECT id, project_phase_l1, sub_phase_l2, work_content_l4 
            FROM wbs_tasks 
            WHERE work_content_l4 != ''
        ''')
        leaf_tasks = cursor.fetchall()
        print(f'找到 {len(leaf_tasks)} 个L4/L5叶子任务')
        
        updated = 0
        not_found = 0
        
        for leaf_id, l1, l2, l4 in leaf_tasks:
            # 查找匹配的L2父节点
            parent_id = None
            for node_id, node_l1, node_l2 in l2_nodes:
                if node_l1 == l1 and node_l2 == l2:
                    parent_id = node_id
                    break
            
            if parent_id:
                cursor.execute(
                    'UPDATE wbs_tasks SET parent_id = %s WHERE id = %s',
                    (parent_id, leaf_id)
                )
                updated += 1
            else:
                not_found += 1
                print(f'  未找到匹配的L2父节点: L1={l1}, L2={l2}, L4={l4}')
        
        conn.commit()
        print(f'\n更新完成:')
        print(f'  成功关联: {updated}条')
        print(f'  未找到父节点: {not_found}条')
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()
