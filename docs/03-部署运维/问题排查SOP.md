---

```markdown
# GX教育项目交付管理系统 - 问题排查SOP

**版本**：V1.0
**日期**：2026年7月


## 一、排查方法论

### 1.1 问题定位四步法

1. **确认现象**：什么功能不可用？报错信息是什么？
2. **缩小范围**：是前端问题、后端问题还是数据库问题？
3. **查看日志**：从日志中获取详细错误信息
4. **定位根因**：找到问题根源并修复

### 1.2 常用排查命令速查

| 用途 | 命令 |
|------|------|
| 查看服务状态 | `sudo systemctl status gx-backend` |
| 查看后端日志 | `sudo journalctl -u gx-backend -f` |
| 查看Nginx日志 | `sudo tail -f /var/log/nginx/error.log` |
| 查看Docker容器状态 | `docker ps -a` |
| 查看Docker日志 | `docker logs gx_mysql` |
| 检查端口占用 | `sudo lsof -i :8000` |
| 检查进程状态 | `ps aux | grep uvicorn` |
| 测试后端健康 | `curl http://127.0.0.1:8000/health` |
| 测试MySQL连接 | `telnet 127.0.0.1 3306` |


## 二、端口与进程问题

### 2.1 端口被占用（Address already in use）

**现象**：启动后端时报错 `ERROR: [Errno 98] Address already in use`

**排查步骤**：
```bash
# 1. 查看占用端口的进程
sudo lsof -i :8000

# 2. 根据PID杀掉进程
sudo kill -9 <PID>

# 3. 确认端口已释放
sudo netstat -tlnp | grep 8000

# 4. 重启服务
sudo systemctl start gx-backend
```

### 2.2 进程停止（Tl状态）

**现象**：服务无响应，`ps aux | grep uvicorn` 显示状态为 `T` 或 `Tl`

**排查步骤**：
```bash
# 1. 查看进程状态
ps aux | grep uvicorn

# 2. 尝试恢复进程
kill -CONT <PID>

# 3. 如无效，强制杀掉并重启
sudo kill -9 <PID>
sudo systemctl start gx-backend
```

### 2.3 端口无法访问（安全组拦截）

**现象**：内部 `curl` 正常，外部浏览器无法访问

**排查步骤**：
```bash
# 1. 确认服务监听所有接口
netstat -tlnp | grep 8000
# 应显示 0.0.0.0:8000，而非 127.0.0.1:8000

# 2. 测试本地访问
curl http://127.0.0.1:8000/health

# 3. 测试公网访问
curl http://<公网IP>:8000/health
```

**解决方案**：
- 登录腾讯云控制台 → 安全组 → 入站规则
- 添加规则：TCP:8000 和 TCP:8080，来源 `0.0.0.0/0`


## 三、后端问题

### 3.1 Internal Server Error（500）

**现象**：API返回 `Internal Server Error`，状态码500

**排查步骤**：
```bash
# 1. 查看后端日志
sudo journalctl -u gx-backend -n 50

# 2. 或进入项目目录测试
cd ~/gx-project/backend
source venv/bin/activate
python -c "
import requests
r = requests.post('http://127.0.0.1:8000/api/v1/auth/login', 
    data={'username':'admin','password':'Admin@2026'})
print(r.status_code, r.text)
"
```

**常见原因及解决方案**：

| 原因           | 解决方案                       |
| -------------- | ------------------------------ |
| 密码哈希无效   | 重新生成bcrypt哈希，更新数据库 |
| 数据库连接失败 | 检查MySQL容器状态、网络连通性  |
| 依赖缺失       | 重新安装 `requirements.txt`    |
| 环境变量错误   | 检查 `.env` 配置               |

### 3.2 数据库连接失败

**现象**：错误信息包含 `Can't connect to MySQL server`

**排查步骤**：
```bash
# 1. 检查MySQL容器状态
docker ps | grep gx_mysql

# 2. 检查MySQL日志
docker logs gx_mysql --tail 30

# 3. 测试数据库连接
docker exec -it gx_mysql mysql -uroot -pGX2026\!root -e "SELECT 1;"

# 4. 检查网络连通性
telnet localhost 3306
```

**解决方案**：
```bash
# 如果容器未运行
docker start gx_mysql

# 如果容器需要重建
docker stop gx_mysql && docker rm gx_mysql
# 重新执行部署手册中的 docker run 命令
```

### 3.3 密码哈希错误

**现象**：`passlib.exc.UnknownHashError: hash could not be identified`

**解决方案**：
```bash
# 1. 生成正确的bcrypt哈希
cd ~/gx-project/backend
source venv/bin/activate
python3 -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('Admin@2026'))"

# 2. 复制输出的哈希值，更新数据库
docker exec -i gx_mysql mysql -uroot -pGX2026\!root gx_project -e "UPDATE users SET password_hash = '粘贴哈希' WHERE username = 'admin';"

# 3. 重启后端
sudo systemctl restart gx-backend
```


## 四、前端问题

### 4.1 前端页面无法访问

**排查步骤**：
```bash
# 1. 检查前端静态文件是否存在
ls -la /var/www/gx/

# 2. 检查Nginx状态
sudo systemctl status nginx

# 3. 检查Nginx配置
sudo nginx -t

# 4. 检查端口监听
netstat -tlnp | grep 8080
```

### 4.2 API请求404（代理未生效）

**现象**：前端请求 `/api/xxx` 返回404

**排查步骤**：
1. 打开浏览器开发者工具（F12）→ Network标签
2. 查看请求的完整URL
3. 确认Nginx配置中包含 `/api/` 的代理规则

**解决方案**：检查 `/etc/nginx/sites-available/gx-project` 中是否存在以下配置：
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    ...
}
```

### 4.3 CORS跨域问题

**现象**：浏览器控制台报 `CORS` 或 `Cross-Origin` 错误

**排查步骤**：
- 确认后端 `main.py` 中已配置 CORS 中间件
- 确认 `allow_origins=["*"]` 或包含前端地址

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```


## 五、数据库问题

### 5.1 表不存在

**现象**：`ERROR 1146 (42S02): Table 'xxx' doesn't exist`

**排查步骤**：
```bash
# 查看当前库的所有表
docker exec -it gx_mysql mysql -uroot -pGX2026\!root -e "USE gx_project; SHOW TABLES;"
```

**解决方案**：执行 `~/gx-project/ddl.sql` 建表
```bash
docker exec -i gx_mysql mysql -uroot -pGX2026\!root gx_project < ~/gx-project/ddl.sql
```

### 5.2 用户不存在

**现象**：`username=admin` 不存在，登录返回 `用户名或密码错误`

**排查步骤**：
```bash
docker exec -it gx_mysql mysql -uroot -pGX2026\!root -e "USE gx_project; SELECT username FROM users;"
```

**解决方案**：
```sql
INSERT INTO users (username, password_hash, real_name, role, phone, email, status)
VALUES ('admin', '$2b$12$...', '系统管理员', 'admin', '13800000000', 'admin@gx.com', '启用');
```


## 六、排查流程图

```
┌─────────────────────────────────────────────────────────┐
│                     用户反馈问题                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              判断问题类型                               │
│  前端问题（页面/样式/交互） │ 后端问题（API/数据）      │
└─────────────────────────────────────────────────────────┘
        │                           │
        ▼                           ▼
┌─────────────────────┐   ┌─────────────────────────────┐
│   前端排查           │   │   后端排查                  │
│ 1. 浏览器F12控制台   │   │ 1. 查看服务状态             │
│ 2. Network标签查看   │   │ 2. 查看journalctl日志       │
│ 3. 检查Nginx配置     │   │ 3. 测试API接口              │
└─────────────────────┘   └─────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────────┐
                    │         数据库排查                  │
                    │ 1. 检查MySQL容器状态                │
                    │ 2. 查看docker logs                 │
                    │ 3. 连接数据库验证数据              │
                    └─────────────────────────────────────┘
```


## 七、版本信息

| 项目     | 版本       |
| -------- | ---------- |
| 文档版本 | V1.0       |
| 最后更新 | 2026-07-17 |
