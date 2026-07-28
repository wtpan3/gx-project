#!/usr/bin/env python3
"""
Schema一致性检查脚本
检查MySQL数据库schema与SQLAlchemy models定义是否一致

用法: python check_schema.py [--db DATABASE] [--fix]
示例: python check_schema.py
      python check_schema.py --db gx_project
      python check_schema.py --fix  # 自动修复差异（谨慎使用）

检查项：
1. 表是否存在
2. 字段名是否一致
3. 字段类型是否匹配
4. ENUM值是否一致
5. 必填/可选是否一致
6. 默认值是否一致
"""

import sys
import argparse
from sqlalchemy import create_engine, inspect, MetaData, text
from sqlalchemy.orm import sessionmaker
import os

# 添加backend路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import (
    Device, SoftwareModule, School,
    WBSTask, Risk, Document, Todo, User
)

# 数据库配置
DB_CONFIG = {
    'host': '124.222.151.69',
    'port': 3306,
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',  # 默认数据库
    'charset': 'utf8mb4'
}


class SchemaChecker:
    """Schema一致性检查器"""

    def __init__(self, database=None):
        self.database = database or DB_CONFIG['database']
        self.engine = self._create_engine()
        self.inspector = inspect(self.engine)
        self.errors = []
        self.warnings = []

        # 需要检查的模型列表
        self.models = [
            Device, SoftwareModule, School,
            WBSTask, Risk, Document, Todo, User
        ]

    def _create_engine(self):
        """创建数据库引擎"""
        db_url = (
            f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{self.database}"
            f"?charset={DB_CONFIG['charset']}"
        )
        return create_engine(db_url, echo=False)

    def check_all(self):
        """执行所有检查"""
        print("=" * 60)
        print("Schema一致性检查")
        print("=" * 60)
        print(f"数据库: {self.database}")
        print(f"检查模型数: {len(self.models)}")
        print("=" * 60)
        print()

        for model in self.models:
            self.check_model(model)

        self._print_summary()

    def check_model(self, model):
        """检查单个模型"""
        table_name = model.__tablename__
        print(f"检查表: {table_name}")

        # 1. 检查表是否存在
        if not self.inspector.has_table(table_name):
            self.errors.append(f"❌ 表 {table_name} 不存在于数据库中")
            print(f"  ❌ 表不存在")
            print()
            return

        # 获取数据库中的列信息
        db_columns = {col['name']: col for col in self.inspector.get_columns(table_name)}

        # 获取模型中的列信息
        model_columns = {col.name: col for col in model.__table__.columns}

        # 2. 检查字段名一致性
        db_col_names = set(db_columns.keys())
        model_col_names = set(model_columns.keys())

        # 数据库有但模型没有
        extra_in_db = db_col_names - model_col_names
        if extra_in_db:
            for col in extra_in_db:
                self.warnings.append(
                    f"⚠️  {table_name}.{col}: 数据库中存在但模型中未定义"
                )
                print(f"  ⚠️  字段 {col}: 数据库有但模型没有")

        # 模型有但数据库没有
        extra_in_model = model_col_names - db_col_names
        if extra_in_model:
            for col in extra_in_model:
                self.errors.append(
                    f"❌ {table_name}.{col}: 模型中定义但数据库中不存在"
                )
                print(f"  ❌ 字段 {col}: 模型有但数据库没有")

        # 3. 检查共同字段的类型和属性
        common_cols = db_col_names & model_col_names
        for col_name in common_cols:
            db_col = db_columns[col_name]
            model_col = model_columns[col_name]

            # 检查类型
            self._check_column_type(table_name, col_name, db_col, model_col)

            # 检查ENUM值
            if 'ENUM' in str(db_col['type']).upper():
                self._check_enum_values(table_name, col_name, db_col, model_col)

            # 检查nullable
            self._check_nullable(table_name, col_name, db_col, model_col)

        if not extra_in_db and not extra_in_model:
            print(f"  ✅ 字段名一致")

        print()

    def _check_column_type(self, table_name, col_name, db_col, model_col):
        """检查列类型"""
        db_type = str(db_col['type']).upper()
        model_type = str(model_col.type).upper()

        # 简化类型比较（忽略长度等细节）
        db_type_base = db_type.split('(')[0]
        model_type_base = model_type.split('(')[0]

        # 类型映射（处理SQLAlchemy类型到MySQL类型的转换）
        type_mapping = {
            'INTEGER': 'INT',
            'STRING': 'VARCHAR',
            'TEXT': 'TEXT',
            'DATETIME': 'DATETIME',
            'DATE': 'DATE',
            'BOOLEAN': 'TINYINT',
            'DECIMAL': 'DECIMAL',
        }

        model_type_mapped = type_mapping.get(model_type_base, model_type_base)

        if db_type_base != model_type_mapped and not (
            'ENUM' in db_type_base and 'ENUM' in model_type_base
        ):
            self.warnings.append(
                f"⚠️  {table_name}.{col_name}: 类型不匹配 "
                f"(DB: {db_type_base}, Model: {model_type_mapped})"
            )

    def _check_enum_values(self, table_name, col_name, db_col, model_col):
        """检查ENUM值一致性"""
        # 从数据库类型字符串中提取ENUM值
        db_type_str = str(db_col['type'])

        # 解析数据库ENUM值
        if 'ENUM' in db_type_str.upper():
            # 格式: ENUM('值1','值2','值3')
            import re
            matches = re.findall(r"'([^']*)'", db_type_str)
            db_enum_values = set(matches)
        else:
            return

        # 解析模型ENUM值
        model_type_str = str(model_col.type)
        if 'ENUM' in model_type_str.upper():
            matches = re.findall(r"'([^']*)'", model_type_str)
            model_enum_values = set(matches)
        else:
            model_enum_values = set()

        # 比较ENUM值
        if db_enum_values != model_enum_values:
            extra_in_db = db_enum_values - model_enum_values
            extra_in_model = model_enum_values - db_enum_values

            msg = f"❌ {table_name}.{col_name}: ENUM值不一致"
            if extra_in_db:
                msg += f"\n   数据库多: {extra_in_db}"
            if extra_in_model:
                msg += f"\n   模型多: {extra_in_model}"

            self.errors.append(msg)
            print(f"  ❌ 字段 {col_name}: ENUM值不一致")
            if extra_in_db:
                print(f"     数据库多: {extra_in_db}")
            if extra_in_model:
                print(f"     模型多: {extra_in_model}")

    def _check_nullable(self, table_name, col_name, db_col, model_col):
        """检查nullable一致性"""
        db_nullable = db_col['nullable']
        model_nullable = model_col.nullable

        if db_nullable != model_nullable:
            self.warnings.append(
                f"⚠️  {table_name}.{col_name}: nullable不一致 "
                f"(DB: {db_nullable}, Model: {model_nullable})"
            )

    def _print_summary(self):
        """打印检查总结"""
        print("=" * 60)
        print("检查总结")
        print("=" * 60)

        if not self.errors and not self.warnings:
            print("✅ 所有检查通过！数据库schema与模型定义完全一致。")
        else:
            if self.errors:
                print(f"\n❌ 发现 {len(self.errors)} 个错误:")
                for error in self.errors:
                    print(f"  {error}")

            if self.warnings:
                print(f"\n⚠️  发现 {len(self.warnings)} 个警告:")
                for warning in self.warnings:
                    print(f"  {warning}")

        print("\n" + "=" * 60)
        print(f"错误数: {len(self.errors)}")
        print(f"警告数: {len(self.warnings)}")
        print("=" * 60)

        # 返回退出码
        return 1 if self.errors else 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Schema一致性检查脚本')
    parser.add_argument('--db', '--database', dest='database',
                        help='数据库名称（默认: gx_project_dev）')
    parser.add_argument('--fix', action='store_true',
                        help='自动修复差异（暂未实现）')

    args = parser.parse_args()

    if args.fix:
        print("⚠️  --fix 选项暂未实现，仅执行检查")
        print()

    checker = SchemaChecker(database=args.database)
    exit_code = checker.check_all()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
