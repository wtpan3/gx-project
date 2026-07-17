# GX教育项目交付管理系统 - 问题排查SOP

## 一、端口占用排查
### 如何判断端口被占用？
```bash
sudo lsof -i :8000
```
### 解决方法
```bash
sudo kill -9 <PID>
# 或强制释放端口
sudo fuser -k 8000/tcp
```

## 二、进程停止（Tl状态）处理
### 如何判断进程停止？
```bash
ps aux | grep uvicorn
# 状态列显示 T 或 Tl 表示停止
```
### 恢复方法
```bash
kill -CONT <PID>
# 如无效则强制重启
sudo kill -9 <PID>
```

## 三、后端 Internal Server Error 排查
1. 进入 backend screen 查看错误堆栈
2. 常见原因：密码哈希格式错误
### 修复密码哈希
```bash
# 生成新哈希
python3 -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('Admin@2026'))"
# 更新数据库
docker exec -i gx_mysql mysql -uroot -pGX2026\!root gx_project -e "UPDATE users SET password_hash = '新哈希' WHERE username = 'admin';"
```

## 四、前端代理404
### 排查方法
查看浏览器 Network 请求URL是否包含 /api
### 解决方案
前端直接调用后端绝对地址（绕过代理）
```typescript
axios.post('http://124.222.151.69:8000/api/...')
```

## 五、Screen 会话管理
```bash
screen -ls              # 查看所有会话
screen -r <会话名>       # 进入会话
# 脱离：Ctrl+A 然后 D
# 强制脱离：screen -d <PID>
# 删除会话：screen -X -S <PID> quit
```

## 六、安全组排查
- 内部 curl 正常但外网不通 → 安全组未放行端口
- 解决方案：腾讯云控制台 → 安全组 → 添加入站规则 TCP:8000/8080
