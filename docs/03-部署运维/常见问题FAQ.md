```markdown
# GX教育项目交付管理系统 - 常见问题FAQ

**版本**：V1.0
**日期**：2026年7月


### Q1: 前端页面无法访问？

**现象**：浏览器打开 `http://124.222.151.69/` 无响应或超时

**排查步骤**：
1. 检查前端进程：`ps aux | grep node`（开发模式）或检查 Nginx（生产模式）
2. 检查端口监听：`sudo netstat -tlnp | grep 80`
3. 检查腾讯云安全组是否放行 80 端口
4. 检查 Nginx 状态：`sudo systemctl status nginx`

**解决方案**：
- 生产环境：`sudo systemctl restart nginx`
- 开发环境：进入 frontend 目录执行 `npm start`

### Q2: 登录返回 `Internal Server Error`？

**现象**：输入用户名密码后报错 500

**排查步骤**：
1. 查看后端日志：`sudo journalctl -u gx-backend -f`
2. 常见原因：密码哈希无效、数据库连接失败

**解决方案**：
- 密码哈希问题：按 SOP 重新生成 bcrypt 哈希并更新数据库
- 数据库问题：检查 MySQL 容器状态 `docker ps | grep gx_mysql`

### Q3: 登录提示 `用户名或密码错误`？

**现象**：输入正确的 admin/Admin@2026 仍然报错

**排查步骤**：
1. 确认用户名是否存在：`docker exec -it gx_mysql mysql -uroot -pGX2026\!root -e "USE gx_project; SELECT username FROM users;"`
2. 确认密码哈希是否正确

**解决方案**：
- 如果 admin 不存在，执行插入 SQL
- 如果哈希不对，重新生成并更新

### Q4: 后端启动报端口占用（Address already in use）？

**现象**：`ERROR: [Errno 98] Address already in use`

**解决方案**：
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
sudo systemctl start gx-backend
```

### Q5: MySQL 容器无法启动或反复重启？

**现象**：`docker ps` 显示 `gx_mysql` 状态为 `Restarting`

**排查步骤**：
1. 查看日志：`docker logs gx_mysql`
2. 常见原因：数据目录权限问题、环境变量错误

**解决方案**：
```bash
# 检查数据目录权限
sudo chown -R 999:999 ~/gx-project/mysql-data

# 重新创建容器
docker stop gx_mysql && docker rm gx_mysql
# 使用部署手册中的 docker run 命令重新创建
```

### Q6: 前端 API 请求返回 404？

**现象**：浏览器 Network 中看到 `/api/xxx` 返回 404

**排查步骤**：
1. 查看请求 URL 是发到前端端口还是后端端口
2. 检查 Nginx 代理配置

**解决方案**：
- 生产环境：检查 `/etc/nginx/sites-available/gx-project` 中的 `/api/` 代理配置
- 开发环境：确保后端已启动，或直接调用 `http://127.0.0.1:8000/api/`

### Q7: 如何查看后端实时日志？

**生产环境（systemd）**：
```bash
sudo journalctl -u gx-backend -f
```

**开发环境（Screen）**：
```bash
screen -r backend
```

### Q8: 如何更新管理员密码？

1. 生成新密码的 bcrypt 哈希：
```bash
cd ~/gx-project/backend
source venv/bin/activate
python3 -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('新密码'))"
```
2. 更新数据库：
```bash
docker exec -i gx_mysql mysql -uroot -pGX2026\!root gx_project -e "UPDATE users SET password_hash = '粘贴哈希' WHERE username = 'admin';"
```

### Q9: 数据库连接失败（Can't connect to MySQL）？

**排查步骤**：
1. 检查容器是否运行：`docker ps | grep gx_mysql`
2. 检查日志：`docker logs gx_mysql`
3. 检查 `.env` 中的 `DB_HOST` 配置

**解决方案**：
- 容器未运行：`docker start gx_mysql`
- 配置错误：修改 `.env` 中的 `DB_HOST=localhost`（容器内）或 `DB_HOST=127.0.0.1`（宿主机）

### Q10: 修改代码后不生效？

**前端（开发模式）**：
- 保存文件后自动重新编译（热更新）
- 如不生效，强制刷新浏览器（Ctrl+Shift+R）
- 或重启前端：`npm start`

**前端（生产模式）**：
- 需要重新构建：`cd ~/gx-project/frontend && npm run build`（Nginx 直接读 build 目录，无需复制）
- 重启 Nginx：`sudo systemctl reload nginx`

**后端**：
- 如果使用 `--reload` 参数启动，代码修改会自动重启
- 否则需要手动重启：`sudo systemctl restart gx-backend`

### Q11: 如何重启整个系统？

**使用脚本**（如已配置）：
```bash
~/gx-project/scripts/stop-all.sh
~/gx-project/scripts/start-all.sh
```

**手动重启**：
```bash
# 停止
sudo systemctl stop gx-backend
docker stop gx_mysql
sudo systemctl stop nginx

# 启动
docker start gx_mysql
sudo systemctl start gx-backend
sudo systemctl start nginx
```

### Q12: 默认管理员账号是什么？

| 字段   | 值           |
| ------ | ------------ |
| 用户名 | `admin`      |
| 密码   | `Admin@2026` |

### Q13: 安全组需要开放哪些端口？

| 端口 | 用途     | 建议                             |
| ---- | -------- | -------------------------------- |
| 22   | SSH登录  | 必须开放                         |
| 80   | 前端页面(Nginx) | 对外开放                  |
| 8000 | 后端API  | 内网访问即可（前端走Nginx反代）  |
| 3306 | MySQL    | **不建议对外开放**（仅内网访问） |

### Q14: 如何备份数据库？

```bash
# 备份生产库
docker exec gx_mysql mysqldump -uroot -pGX2026\!root gx_project > ~/backup/gx_project_$(date +%Y%m%d).sql

# 备份开发库
docker exec gx_mysql mysqldump -uroot -pGX2026\!root gx_project_dev > ~/backup/gx_project_dev_$(date +%Y%m%d).sql
```

### Q15: 如何确认所有服务正常运行？

```bash
# 一键健康检查
~/gx-project/scripts/health-check.sh
```

或手动检查：
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1/ | head -5
docker ps | grep gx_mysql
```


## 版本信息

| 项目     | 版本       |
| -------- | ---------- |
| 文档版本 | V1.0       |
| 最后更新 | 2026-07-17 |
