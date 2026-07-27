#!/bin/bash
# GX项目 - MySQL SQL导入脚本（强制utf8mb4字符集）
# 用途: 防止导入SQL时忘记指定字符集导致中文双重编码
# 作者: GX-PM Team
# 日期: 2026-07-23

set -e  # 遇错即停

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 使用说明
usage() {
    echo "用法: $0 <SQL文件路径> [数据库名]"
    echo ""
    echo "示例:"
    echo "  $0 ddl.sql                    # 导入到默认数据库 gx_project_dev"
    echo "  $0 migration.sql gx_project   # 导入到指定数据库"
    echo ""
    echo "说明:"
    echo "  - 自动使用 --default-character-set=utf8mb4"
    echo "  - 防止中文ENUM值双重编码"
    echo "  - 默认连接本地Docker容器 gx_mysql"
    exit 1
}

# 检查参数
if [ $# -lt 1 ]; then
    echo -e "${RED}错误: 缺少SQL文件参数${NC}"
    usage
fi

SQL_FILE="$1"
DB_NAME="${2:-gx_project_dev}"  # 默认数据库

# 检查文件是否存在
if [ ! -f "$SQL_FILE" ]; then
    echo -e "${RED}错误: 文件不存在: $SQL_FILE${NC}"
    exit 1
fi

# MySQL连接配置
MYSQL_HOST="gx_mysql"          # Docker容器名
MYSQL_USER="root"
MYSQL_PASSWORD="GX2026!root"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}GX项目 SQL导入工具${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "SQL文件: ${GREEN}$SQL_FILE${NC}"
echo -e "目标数据库: ${GREEN}$DB_NAME${NC}"
echo -e "字符集: ${GREEN}utf8mb4${NC} (强制)"
echo -e "${YELLOW}========================================${NC}"
echo ""

# 确认导入
read -p "确认导入? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消导入${NC}"
    exit 0
fi

# 执行导入
echo -e "${YELLOW}正在导入...${NC}"

docker exec -i "$MYSQL_HOST" mysql \
    -u"$MYSQL_USER" \
    -p"$MYSQL_PASSWORD" \
    --default-character-set=utf8mb4 \
    "$DB_NAME" < "$SQL_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 导入成功！${NC}"
    echo ""
    echo -e "${YELLOW}建议执行验证:${NC}"
    echo "docker exec -it $MYSQL_HOST mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $DB_NAME"
    echo "然后执行: SHOW TABLES; 或 SELECT * FROM <表名> LIMIT 1;"
else
    echo -e "${RED}✗ 导入失败${NC}"
    exit 1
fi
