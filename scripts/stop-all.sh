#!/bin/bash
echo "=== 停止GX项目所有服务 ==="

# 停止后端
pkill -9 uvicorn 2>/dev/null && echo "✅ 后端已停止" || echo "ℹ️ 后端未运行"

# 停止前端
pkill -9 -f node 2>/dev/null && echo "✅ 前端已停止" || echo "ℹ️ 前端未运行"

# 停止MySQL容器
docker stop gx_mysql 2>/dev/null && echo "✅ MySQL已停止" || echo "ℹ️ MySQL未运行"

# 清理Screen会话
screen -X -S backend quit 2>/dev/null
screen -X -S frontend quit 2>/dev/null

echo ""
echo "所有服务已停止"
