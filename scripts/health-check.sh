#!/bin/bash
echo "=== 健康检查 ==="
curl -s http://127.0.0.1:8000/health >/dev/null && echo "✅ 后端OK" || echo "❌ 后端异常"
curl -s http://127.0.0.1:8080 | head -1 | grep -q "<!DOCTYPE" && echo "✅ 前端OK" || echo "❌ 前端异常"
docker ps | grep gx_mysql >/dev/null && echo "✅ MySQL OK" || echo "❌ MySQL异常"
