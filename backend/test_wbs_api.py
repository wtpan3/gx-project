#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WBS模块完整功能测试脚本"""

import requests
import json
from datetime import date

API_BASE = 'http://127.0.0.1:8000/api/v1'

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_list():
    """测试1: 任务列表"""
    print_section("测试1: 任务列表查询")

    response = requests.get(f"{API_BASE}/wbs-tasks", params={'page': 1, 'page_size': 5})
    data = response.json()

    print(f"✓ 状态码: {response.status_code}")
    print(f"✓ 总数: {data['total']}")
    print(f"✓ 返回条数: {len(data['items'])}")

    if data['items']:
        first = data['items'][0]
        print(f"✓ 第一条: {first['task_code']} - {first['work_content_l4']}")

def test_filter_status():
    """测试2: 状态筛选"""
    print_section("测试2: 状态筛选")

    statuses = ['待开始', '进行中', '已完成', '已暂停']
    for status in statuses:
        response = requests.get(f"{API_BASE}/wbs-tasks", params={'status': status, 'page_size': 100})
        data = response.json()
        print(f"✓ {status}: {data['total']}条")

def test_search():
    """测试3: 关键词搜索"""
    print_section("测试3: 关键词搜索")

    response = requests.get(f"{API_BASE}/wbs-tasks", params={'keyword': '验收'})
    data = response.json()

    print(f"✓ 搜索'验收': {data['total']}条")
    for item in data['items'][:3]:
        print(f"  - {item['task_code']}: {item['work_content_l4']}")

def test_detail():
    """测试4: 详情查询"""
    print_section("测试4: 详情查询")

    response = requests.get(f"{API_BASE}/wbs-tasks/34")
    task = response.json()

    print(f"✓ 状态码: {response.status_code}")
    print(f"✓ 任务编码: {task['task_code']}")
    print(f"✓ 工作内容: {task['work_content_l4']}")
    print(f"✓ 状态: {task['status']}")
    print(f"✓ 责任人: {task.get('assignee_name', '-')}")

def test_create():
    """测试5: 创建任务"""
    print_section("测试5: 创建任务")

    new_task = {
        "construction_year": "2026",
        "project_phase_l1": "功能测试",
        "sub_phase_l2": "API测试",
        "task_package_l3": "后端验证",
        "work_content_l4": "完整功能测试",
        "work_detail_l5": "验证所有API端点",
        "task_code": f"TEST-{date.today().strftime('%Y%m%d')}-001",
        "priority": "高",
        "status": "待开始",
        "plan_start_date": "2026-07-21",
        "plan_end_date": "2026-07-25",
        "responsible_person_id": 1,
        "school_id": 1,
        "progress_note": "自动化测试创建"
    }

    response = requests.post(
        f"{API_BASE}/wbs-tasks",
        json=new_task,
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )

    if response.status_code == 200:
        task = response.json()
        print(f"✓ 创建成功! ID: {task['id']}")
        print(f"✓ 任务编码: {task['task_code']}")
        return task['id']
    else:
        print(f"✗ 创建失败: {response.text}")
        return None

def test_duplicate_code():
    """测试6: 唯一性约束"""
    print_section("测试6: task_code唯一性约束")

    duplicate_task = {
        "construction_year": "2026",
        "project_phase_l1": "测试",
        "sub_phase_l2": "测试",
        "task_package_l3": "测试",
        "work_content_l4": "测试重复编码",
        "task_code": "WBS-T001",
        "priority": "中",
        "status": "待开始",
        "responsible_person_id": 1,
        "school_id": 1
    }

    response = requests.post(
        f"{API_BASE}/wbs-tasks",
        json=duplicate_task,
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )

    if response.status_code == 400:
        print(f"✓ 正确拦截重复编码: {response.json()['detail']}")
    else:
        print(f"✗ 未拦截重复编码")

def test_update(task_id):
    """测试7: 更新任务"""
    print_section(f"测试7: 更新任务 (ID={task_id})")

    update_data = {
        "status": "进行中",
        "priority": "中",
        "progress_note": "测试更新功能 - 已修改"
    }

    response = requests.put(
        f"{API_BASE}/wbs-tasks/{task_id}",
        json=update_data,
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )

    if response.status_code == 200:
        task = response.json()
        print(f"✓ 更新成功!")
        print(f"✓ 状态: {task['status']}")
        print(f"✓ 优先级: {task['priority']}")
        print(f"✓ 进度说明: {task.get('progress_note', '-')}")
    else:
        print(f"✗ 更新失败: {response.text}")

def test_delete(task_id):
    """测试8: 软删除"""
    print_section(f"测试8: 软删除任务 (ID={task_id})")

    response = requests.delete(f"{API_BASE}/wbs-tasks/{task_id}")

    if response.status_code == 204:
        print(f"✓ 删除成功 (HTTP 204)")

        # 验证无法再查询
        verify = requests.get(f"{API_BASE}/wbs-tasks/{task_id}")
        if verify.status_code == 404:
            print(f"✓ 验证通过: 已删除任务无法查询 (HTTP 404)")
        else:
            print(f"✗ 验证失败: 已删除任务仍可查询")
    else:
        print(f"✗ 删除失败: {response.text}")

def test_combination():
    """测试9: 组合查询"""
    print_section("测试9: 组合查询 (状态+关键词)")

    response = requests.get(f"{API_BASE}/wbs-tasks", params={
        'status': '已完成',
        'keyword': '验收',
        'page_size': 10
    })
    data = response.json()

    print(f"✓ 组合查询 (状态=已完成 AND 关键词=验收): {data['total']}条")
    for item in data['items'][:3]:
        print(f"  - {item['task_code']}: {item['work_content_l4']} [{item['status']}]")

def main():
    print("\n" + "🧪 WBS模块完整功能测试".center(60, "="))

    try:
        # 基础查询测试
        test_list()
        test_filter_status()
        test_search()
        test_detail()

        # 创建和唯一性测试
        task_id = test_create()
        test_duplicate_code()

        # 更新和删除测试
        if task_id:
            test_update(task_id)
            test_delete(task_id)

        # 组合查询测试
        test_combination()

        print("\n" + "="*60)
        print("  ✅ 所有测试完成!".center(60))
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
