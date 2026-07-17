# GX教育项目交付管理系统 - 常见问题FAQ

### Q1: 前端无法访问？
1. 检查进程：ps aux | grep node
2. 检查端口：sudo netstat -tlnp | grep 8080
3. 检查安全组是否放行8080

### Q2: 登录返回 Internal Server Error？
- 查看后端日志：screen -r backend
- 最常见原因：密码哈希无效，按SOP重新生成

### Q3: 如何查看后端实时日志？
- 进入 backend screen：screen -r backend
- 或使用 tail -f 配合日志文件

### Q4: 数据库连接失败？
- 检查容器状态：docker ps | grep mysql
- 查看错误日志：docker logs gx_mysql

### Q5: 如何更新管理员密码？
- 按SOP中的修复密码哈希步骤操作

### Q6: 前端修改代码不生效？
- 检查是否热更新：终端应显示 webpack compiled successfully
- 强制刷新浏览器（Ctrl+Shift+R）

### Q7: 如何重启整个系统？
```bash
# 停止
pkill -9 uvicorn && pkill -9 -f node
# 启动
cd ~/gx-project/backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 &
cd ~/gx-project/frontend && PORT=8080 npm start &
```
