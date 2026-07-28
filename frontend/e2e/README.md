# Playwright E2E 测试使用指南

## 安装状态

- ✅ Playwright 已安装（v1.48.2）
- 🔄 Chromium 浏览器下载中（后台进行，140.4 MB）

## 测试覆盖

### 1. dashboard.spec.ts（Dashboard 基础功能）
- 登录成功并跳转
- Dashboard 总览卡片显示（进度/风险/待办/学校状态）
- 待办列表切换（项目待办 ↔ 我的待办）

### 2. project-plan.spec.ts（项目计划核心功能）
- 三视图切换（甘特图 / 列表 / 看板）
- 新增任务 - 日期倒挂拦截（结束早于开始 → 400）
- 新增任务 - 父子范围校验（子任务越界 → 409 二选一弹窗）
- 行内编辑 - 修改任务状态

## 执行前准备

### 1. 启动后端服务
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 启动前端服务（另一个终端）
```powershell
cd frontend
$env:BROWSER='none'
npm start
# 等待 "Compiled successfully" 出现
```

### 3. 确认服务就绪
- 后端：http://127.0.0.1:8000/health 返回 200
- 前端：http://localhost:3000 可访问

## 执行测试

### 方式1：命令行执行（推荐）
```powershell
cd frontend
npm run test:e2e
```

### 方式2：UI模式（交互式调试）
```powershell
cd frontend
npm run test:e2e:ui
```

### 方式3：调试模式（逐步执行）
```powershell
cd frontend
npm run test:e2e:debug
```

## 测试报告

测试完成后查看 HTML 报告：
```powershell
cd frontend
npx playwright show-report e2e-report
```

## 常见问题

### Q1: Chromium 未下载完成
**现象**：执行测试报错 "Executable doesn't exist"

**解决**：
```powershell
cd frontend
npx playwright install chromium
```

### Q2: 前端未启动或端口占用
**现象**：测试报错 "net::ERR_CONNECTION_REFUSED"

**解决**：
1. 确认 http://localhost:3000 可访问
2. 检查 3000 端口是否被占用：`netstat -ano | findstr :3000`

### Q3: 后端未启动
**现象**：登录后 API 调用 500/404

**解决**：
1. 确认后端健康：`curl http://127.0.0.1:8000/health`
2. 检查 8000 端口：`netstat -ano | findstr :8000`

### Q4: 测试超时
**现象**：Test timeout of 30000ms exceeded

**解决**：
- 检查网络连接
- 增加 playwright.config.ts 中的 `timeout` 值
- 或单独运行失败的测试：`npx playwright test dashboard.spec.ts`

## 下次优化方向

1. 增加风险管理 E2E 测试
2. 增加导入导出功能测试
3. 集成到 CI/CD（GitHub Actions / GitLab CI）
4. 配置 webServer 自动启动前端
5. 增加视觉回归测试（截图对比）

---

**当前状态**：Chromium 下载中，完成后即可执行测试
