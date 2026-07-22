#!/usr/bin/env python3
"""
问题登记脚本 - 快速登记问题到问题登记簿
用法: python scripts/log_issue.py
"""
import csv
import datetime
import os

# CSV文件路径
CSV_PATH = "docs/09-项目复盘/问题登记簿.csv"

def get_next_id():
    """获取下一个问题编号"""
    if not os.path.exists(CSV_PATH):
        return "P001"

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            return "P001"

        # 提取最后一个编号的数字部分
        last_id = rows[-1]['问题编号']
        num = int(last_id[1:]) + 1
        return f"P{num:03d}"

def main():
    print("=== GX项目问题登记 ===\n")

    # 收集信息
    问题描述 = input("问题描述(一句话): ").strip()
    if not 问题描述:
        print("❌ 问题描述不能为空")
        return

    print("\n严重度:")
    print("  0 - P0严重(生产不可用)")
    print("  1 - P1重要(功能受限)")
    print("  2 - P2一般(潜在风险)")
    print("  3 - P3轻微(优化建议)")
    严重度_input = input("选择(0-3): ").strip()
    严重度_map = {"0": "P0", "1": "P1", "2": "P2", "3": "P3"}
    严重度 = 严重度_map.get(严重度_input, "P2")

    print("\n问题类型:")
    print("  1 - 验证不足")
    print("  2 - 数据不一致")
    print("  3 - 演示代码问题")
    print("  4 - 编码问题")
    print("  5 - 配置错误")
    print("  6 - 其他")
    类型_input = input("选择(1-6): ").strip()
    类型_map = {
        "1": "验证不足",
        "2": "数据不一致",
        "3": "演示代码问题",
        "4": "编码问题",
        "5": "配置错误",
        "6": "其他"
    }
    类型 = 类型_map.get(类型_input, "其他")

    根因 = input("\n根因分析(为什么会发生): ").strip()
    是否重复 = input("是否重复问题?(y/N): ").strip().lower() == 'y'

    # 生成编号和日期
    问题编号 = get_next_id()
    日期 = datetime.date.today().strftime("%Y-%m-%d")

    # 写入CSV
    with open(CSV_PATH, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            日期,
            问题编号,
            问题描述,
            严重度,
            类型,
            根因 or "(待补充)",
            "",  # 修复时间
            "",  # 修复PR
            "待修复",
            "是" if 是否重复 else "否"
        ])

    print(f"\n✅ 已登记问题 {问题编号}")
    print(f"   日期: {日期}")
    print(f"   描述: {问题描述}")
    print(f"   严重度: {严重度}")
    print(f"   类型: {类型}")
    print(f"\n💡 后续操作:")
    print(f"   1. 修复问题后,更新CSV中的修复时间、PR、状态")
    print(f"   2. 补充根因分析和预防措施")
    print(f"   3. 每周五自动生成复盘报告")

if __name__ == "__main__":
    main()
