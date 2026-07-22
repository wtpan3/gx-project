#!/usr/bin/env python3
"""
问题分析脚本 - 自动分析问题登记簿并生成复盘报告
用法: python scripts/analyze_issues.py [--days 7]
"""
import csv
import datetime
import argparse
from collections import Counter, defaultdict

CSV_PATH = "docs/09-项目复盘/问题登记簿.csv"
TEMPLATE_PATH = "docs/09-项目复盘/复盘模板.md"

def load_issues(days=7):
    """加载指定天数内的问题"""
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_issues = list(reader)

    # 筛选时间范围
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days)

    period_issues = []
    for issue in all_issues:
        issue_date = datetime.datetime.strptime(issue['日期'], '%Y-%m-%d').date()
        if issue_date >= start_date:
            period_issues.append(issue)

    return period_issues, all_issues

def analyze_issues(issues):
    """分析问题统计"""
    总数 = len(issues)

    # 类型统计
    类型统计 = Counter(i['类型'] for i in issues)

    # 严重度统计
    严重度统计 = Counter(i['严重度'] for i in issues)

    # 重复问题统计
    重复问题数 = sum(1 for i in issues if i['是否重复'] == '是')

    # 修复时间统计
    修复时间列表 = []
    for i in issues:
        if i['修复时间(h)'] and i['修复时间(h)'].strip():
            try:
                修复时间列表.append(float(i['修复时间(h)']))
            except:
                pass

    平均修复时间 = sum(修复时间列表) / len(修复时间列表) if 修复时间列表 else 0

    # 识别重复类型(同类型>=2次)
    重复类型 = {k: v for k, v in 类型统计.items() if v >= 2}

    return {
        '总数': 总数,
        '类型统计': dict(类型统计),
        '严重度统计': dict(严重度统计),
        '重复问题数': 重复问题数,
        '重复问题比例': f"{重复问题数/总数*100:.1f}%" if 总数 > 0 else "0%",
        '重复类型': 重复类型,
        '平均修复时间': f"{平均修复时间:.1f}h" if 平均修复时间 > 0 else "未知"
    }

def generate_report(period_issues, all_issues, stats, days):
    """生成复盘报告"""
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days)

    report = f"""# GX项目复盘报告 - {today}

**复盘周期**: {start_date} 至 {today} ({days}天)
**复盘范围**: 问题登记簿分析
**参与人**: GX-PM Team + Claude
**报告版本**: 自动生成 V1.0

---

## 一、执行摘要

### 问题总览
本周期共发现 **{stats['总数']}个问题**,其中:
- **重复出现问题**: {stats['重复问题数']}个(占比{stats['重复问题比例']})
- **严重问题(P0)**: {stats['严重度统计'].get('P0', 0)}个
- **重要问题(P1)**: {stats['严重度统计'].get('P1', 0)}个
- **一般问题(P2)**: {stats['严重度统计'].get('P2', 0)}个
- **轻微问题(P3)**: {stats['严重度统计'].get('P3', 0)}个

### 核心数据
- **平均修复时间**: {stats['平均修复时间']}
- **重复类型**: {', '.join(f"{k}({v}次)" for k, v in stats['重复类型'].items()) or '无'}

---

## 二、问题分类统计

### 按类型分类

| 类型 | 数量 | 占比 |
|------|------|------|
"""

    # 添加类型统计表
    for 类型, 数量 in sorted(stats['类型统计'].items(), key=lambda x: x[1], reverse=True):
        占比 = f"{数量/stats['总数']*100:.1f}%" if stats['总数'] > 0 else "0%"
        report += f"| {类型} | {数量} | {占比} |\n"

    report += f"""
### 按严重程度分类

| 严重程度 | 数量 | 占比 |
|---------|------|------|
"""

    # 添加严重度统计表
    for 级别 in ['P0', 'P1', 'P2', 'P3']:
        数量 = stats['严重度统计'].get(级别, 0)
        占比 = f"{数量/stats['总数']*100:.1f}%" if stats['总数'] > 0 else "0%"
        report += f"| {级别} | {数量} | {占比} |\n"

    report += """
---

## 三、重复问题分析(★重点)

"""

    # 按类型分组显示重复问题
    if stats['重复类型']:
        类型分组 = defaultdict(list)
        for issue in period_issues:
            if issue['是否重复'] == '是':
                类型分组[issue['类型']].append(issue)

        for 类型, 问题列表 in 类型分组.items():
            report += f"### 🔴 {类型}类问题(出现{len(问题列表)}次)\n\n"
            report += "**具体案例**:\n"
            for idx, issue in enumerate(问题列表, 1):
                report += f"{idx}. [{issue['问题编号']}] {issue['问题描述']} ({issue['日期']})\n"

            # 显示根因(取第一个非空的)
            根因 = next((i['根因'] for i in 问题列表 if i['根因'] and i['根因'] != '(待补充)'), '待分析')
            report += f"\n**共同根因**: {根因}\n\n"
            report += "**优化建议**: (需人工补充具体措施)\n\n"
            report += "---\n\n"
    else:
        report += "✅ 本周期无重复问题\n\n---\n\n"

    report += """
## 四、全部问题清单(按时间线)

| 编号 | 日期 | 问题描述 | 严重度 | 类型 | 状态 |
|------|------|---------|--------|------|------|
"""

    # 添加问题清单
    for issue in sorted(period_issues, key=lambda x: x['日期']):
        report += f"| {issue['问题编号']} | {issue['日期']} | {issue['问题描述']} | {issue['严重度']} | {issue['类型']} | {issue['状态']} |\n"

    report += f"""
---

## 五、待办行动项

### 待修复问题

"""

    # 列出待修复问题
    待修复 = [i for i in period_issues if i['状态'] == '待修复']
    if 待修复:
        for issue in 待修复:
            report += f"- [ ] [{issue['问题编号']}] {issue['问题描述']} ({issue['严重度']})\n"
    else:
        report += "✅ 无待修复问题\n"

    report += """
---

## 六、数据统计

### 问题来源
(需人工补充)

### 修复时间分布
"""

    # 修复时间分布
    修复时间范围 = defaultdict(int)
    for issue in period_issues:
        if issue['修复时间(h)'] and issue['修复时间(h)'].strip():
            try:
                时间 = float(issue['修复时间(h)'])
                if 时间 < 1:
                    修复时间范围['<1小时'] += 1
                elif 时间 < 3:
                    修复时间范围['1-3小时'] += 1
                elif 时间 < 8:
                    修复时间范围['3-8小时'] += 1
                else:
                    修复时间范围['>8小时'] += 1
            except:
                pass

    for 范围, 数量 in 修复时间范围.items():
        report += f"- {范围}: {数量}个\n"

    report += f"""
---

**报告结束**

*本报告由 scripts/analyze_issues.py 自动生成*
*生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return report

def main():
    parser = argparse.ArgumentParser(description='分析问题登记簿并生成复盘报告')
    parser.add_argument('--days', type=int, default=7, help='分析最近N天的问题(默认7天)')
    args = parser.parse_args()

    print(f"=== 分析最近{args.days}天的问题 ===\n")

    # 加载和分析
    period_issues, all_issues = load_issues(args.days)
    stats = analyze_issues(period_issues)

    # 输出统计
    print(f"问题总数: {stats['总数']}")
    print(f"类型分布: {stats['类型统计']}")
    print(f"严重度分布: {stats['严重度统计']}")
    print(f"重复问题: {stats['重复问题数']}个({stats['重复问题比例']})")
    print(f"平均修复时间: {stats['平均修复时间']}")

    # 生成报告
    report = generate_report(period_issues, all_issues, stats, args.days)

    # 保存报告
    today = datetime.date.today().strftime('%Y-%m-%d')
    report_path = f"docs/09-项目复盘/复盘报告-{today}-自动生成.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ 复盘报告已生成: {report_path}")
    print(f"\n💡 后续操作:")
    print(f"   1. 人工审阅报告,补充根因分析和优化建议")
    print(f"   2. 重点关注重复问题章节")
    print(f"   3. 制定具体行动项和责任人")

if __name__ == "__main__":
    main()
