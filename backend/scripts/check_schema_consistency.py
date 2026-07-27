#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema一致性检查脚本
比对数据库实际结构 vs SQLAlchemy Models定义
目标：预防"数据不一致"问题（ddl.sql与models.py独立演化）
"""

import pymysql
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.user import User
from app.models.school import School
from app.models.device_system import DeviceSystem
from app.models.device import Device
from app.models.wbs_task import WbsTask
from app.models.risk import Risk
from app.models.production_line import ProductionLine
from app.models.software_module import SoftwareModule

DB_CONFIG = {
    'host': '124.222.151.69',
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',
    'charset': 'utf8mb4'
}

# SQLAlchemy Models清单
MODELS = [
    User, School, DeviceSystem, Device, WbsTask, Risk, 
    ProductionLine, SoftwareModule
]

def get_db_columns(conn, table_name):
    """从数据库获取表的列定义"""
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    columns = {}
    for row in cursor.fetchall():
        col_name = row[0]
        col_type = row[1].decode('utf-8') if isinstance(row[1], bytes) else row[1]
        columns[col_name] = col_type
    cursor.close()
    return columns

def get_model_columns(model):
    """从SQLAlchemy Model获取列定义"""
    inspector = inspect(model)
    columns = {}
    for col in inspector.columns:
        # 简化类型显示
        col_type = str(col.type)
        columns[col.name] = col_type
    return columns

def compare_schemas():
    """比对所有Model与数据库表结构"""
    print("=" * 80)
    print("  Schema一致性检查")
    print("=" * 80)
    print(f"数据库: {DB_CONFIG['host']}/{DB_CONFIG['database']}")
    print()

    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)

    issues_found = 0
    tables_checked = 0

    try:
        for model in MODELS:
            table_name = model.__tablename__
            tables_checked += 1

            print(f"[{tables_checked}/{len(MODELS)}] 检查表: {table_name}")

            # 获取数据库和Model的列定义
            try:
                db_columns = get_db_columns(conn, table_name)
            except Exception as e:
                print(f"  ✗ 表不存在或无法访问: {e}")
                issues_found += 1
                print()
                continue

            model_columns = get_model_columns(model)

            # 比对列
            db_cols_set = set(db_columns.keys())
            model_cols_set = set(model_columns.keys())

            # 找出差异
            only_in_db = db_cols_set - model_cols_set
            only_in_model = model_cols_set - db_cols_set

            if only_in_db:
                print(f"  ✗ 数据库有但Model缺失的列: {', '.join(only_in_db)}")
                issues_found += 1

            if only_in_model:
                print(f"  ✗ Model有但数据库缺失的列: {', '.join(only_in_model)}")
                issues_found += 1

            # 检查共同列的类型
            common_cols = db_cols_set & model_cols_set
            type_mismatches = []

            for col_name in common_cols:
                db_type = db_columns[col_name].lower()
                model_type = model_columns[col_name].lower()

                # 简化类型匹配（忽略长度、精度等细节）
                # 只检查基本类型是否一致
                if not _types_compatible(db_type, model_type):
                    type_mismatches.append(f"{col_name}: DB({db_type}) vs Model({model_type})")

            if type_mismatches:
                print(f"  ⚠ 类型可能不匹配（需人工确认）:")
                for mismatch in type_mismatches[:3]:  # 最多显示3个
                    print(f"    - {mismatch}")
                if len(type_mismatches) > 3:
                    print(f"    ... 还有 {len(type_mismatches) - 3} 个")

            if not only_in_db and not only_in_model and not type_mismatches:
                print(f"  ✓ 一致")

            print()

    finally:
        conn.close()

    # 汇总结果
    print("=" * 80)
    print("  检查结果汇总")
    print("=" * 80)
    print(f"检查表数: {tables_checked}")
    print(f"发现问题: {issues_found}")

    if issues_found == 0:
        print("\n✓ 所有表结构一致\n")
        return 0
    else:
        print(f"\n✗ 发现 {issues_found} 个不一致项，建议修复\n")
        return 1

def _types_compatible(db_type, model_type):
    """判断数据库类型和Model类型是否兼容"""
    # 标准化类型字符串
    db_base = db_type.lower().split('(')[0].strip()
    model_base = model_type.lower().split('(')[0].strip()

    # SQLAlchemy的Enum在str()时渲染为VARCHAR(N)，而数据库存储为enum(...)
    # 这是ORM的正常映射，不算不一致
    if db_base == 'enum' and model_base == 'varchar':
        return True

    # tinyint(1)在MySQL中常用作布尔，SQLAlchemy可能映射为Integer或Boolean
    if db_base == 'tinyint' and model_base in ('integer', 'int', 'boolean', 'tinyint'):
        return True

    # 类型映射表
    type_map = {
        'int': ['integer', 'int'],
        'varchar': ['varchar', 'string'],
        'text': ['text', 'string'],
        'datetime': ['datetime'],
        'date': ['date'],
        'enum': ['enum'],
    }

    # 查找兼容组
    for group in type_map.values():
        if db_base in group and model_base in group:
            return True

    # 严格匹配
    return db_base == model_base

if __name__ == '__main__':
    exit_code = compare_schemas()
    sys.exit(exit_code)
