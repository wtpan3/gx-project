#!/bin/bash
echo "=== 启动GX项目所有服务 ==="

# 启动MySQL
docker start gx_mysql 2>/dev/null && echo "✅ MySQL已启动" || echo "⚠️ MySQL容器不存在或启动失败"

# 启动后端
screen -dmS backend bash -c "cd ~/gx-project/backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
sleep 2
echo "✅ 后端服务已启动"

# 启动前端
screen -dmS frontend bash -c "cd ~/gx-project/frontend && PORT=8080 npm start"
sleep 2
echo "✅ 前端服务已启动"

echo ""
echo "服务已启动，查看状态：screen -ls"
