#!/bin/bash
# SQL导入封装脚本 - 自动添加utf8mb4字符集参数
# 用法: ./import_sql.sh <sql_file> [database_name]

set -e

SQL_FILE="$1"
DATABASE="${2:-gx_project_dev}"

if [ -z "$SQL_FILE" ]; then
    echo "用法: $0 <sql_file> [database_name]"
    echo "示例: $0 ddl.sql"
    echo "示例: $0 migration.sql gx_project"
    exit 1
fi

if [ ! -f "$SQL_FILE" ]; then
    echo "错误: 文件不存在 - $SQL_FILE"
    exit 1
fi

echo "================================================"
echo "  SQL导入工具（自动添加utf8mb4字符集）"
echo "================================================"
echo "文件: $SQL_FILE"
echo "目标库: $DATABASE"
echo "字符集: utf8mb4 (强制)"
echo ""
echo "执行中..."

# 自动添加 --default-character-set=utf8mb4
docker exec -i gx_mysql mysql \
    -uroot \
    -pGX2026!root \
    --default-character-set=utf8mb4 \
    "$DATABASE" < "$SQL_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 导入成功"
    echo ""
    echo "验证方法:"
    echo "  docker exec gx_mysql mysql -uroot -pGX2026!root $DATABASE -e 'SHOW TABLES;'"
else
    echo ""
    echo "✗ 导入失败"
    exit 1
fi
