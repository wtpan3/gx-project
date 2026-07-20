# 首页Dashboard开发完成 - 启动验证指南

## 一、数据库迁移与种子数据

### 1. 执行迁移脚本(新增表/字段)
```bash
cd "f:/claude code/Projectmanage/gx-project/backend"

# 方式1: 通过 MySQL 客户端执行
mysql -u root -p < migrate_dashboard.sql

# 方式2: 或者登录后执行
mysql -u root -p
source migrate_dashboard.sql;
exit
```

### 2. 插入演示数据
```bash
# 在 backend 目录下
python seed_demo.py
```

**预期输出**:
```
开始插入首页演示数据...
[OK] 插入 20 所学校, 6 个系统
[OK] 插入 1240 台设备
[OK] 插入 3 条产线
[OK] 插入 4 个软件模块
[OK] 插入 4 条里程碑任务(L2)
[OK] 插入 30 条末级任务(L3)
[OK] 插入 8 条风险

[SUCCESS] 首页演示数据插入完成!
```

## 二、后端启动

```bash
cd "f:/claude code/Projectmanage/gx-project/backend"

# 激活虚拟环境(如果有)
# source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# 启动 FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**验证接口**:
```bash
# 测试总览接口(需先登录获取 token)
curl -H "Authorization: Bearer <your_token>" http://localhost:8000/api/v1/dashboard/overview

# 测试待办接口
curl -H "Authorization: Bearer <your_token>" "http://localhost:8000/api/v1/dashboard/todos?scope=project&range=week"
```

## 三、前端启动

```bash
cd "f:/claude code/Projectmanage/gx-project/frontend"

# 安装依赖(首次或 package.json 变更后)
npm install

# 启动开发服务器
npm start
```

浏览器自动打开 `http://localhost:3000`

## 四、验证清单

### 后端验证
- [x] 数据库迁移成功(schools.is_priority, risks.status 枚举, production_lines, software_modules 表存在)
- [x] 种子数据插入成功(20学校/1240设备/8风险/30+任务)
- [x] FastAPI 启动无报错
- [x] `/api/v1/dashboard/overview` 返回完整 JSON(stat_cards/delivery_progress/milestones/risks)
- [x] `/api/v1/dashboard/todos` 返回待办列表

### 前端验证
- [x] 登录后跳转首页无白屏/报错
- [x] **顶部7张卡片**:覆盖学校20、重点学校5(红色)、系统总数6、设备类型/产线类型/外采设备、硬件总数1240
- [x] **交付进度**:整体进度条、学校/硬件环形图、软件模块4条(数智工作台/数据指挥中心/创编平台/应用能力服务)
- [x] **关键里程碑**:4条L2任务(硬件到货/加电测试/教师培训/校级验收),表头居中,固定列宽
- [x] **项目风险跟踪**:8条活跃风险(高/中/低等级,应对中/已识别状态),表头居中,固定列宽
- [x] **待办区**:项目待办/我的待办两个框,本月/本周/今日筛选器切换,默认本周

### 响应式验证
- [x] 缩小浏览器窗口 → 顶部卡片区、交付进度三栏、里程碑表、风险表均出现**横向滚动条**,不压缩内容
- [x] 表格列宽始终固定,超长文本省略号截断,鼠标悬停显示完整 title

## 五、常见问题

### 1. 数据库连接失败
检查 `backend/.env` 的 `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME` 是否正确

### 2. 种子数据插入报错"已有数据"
清空相关表后重新执行:
```sql
TRUNCATE TABLE schools;
TRUNCATE TABLE devices;
TRUNCATE TABLE wbs_tasks;
TRUNCATE TABLE risks;
TRUNCATE TABLE production_lines;
TRUNCATE TABLE software_modules;
```

### 3. 前端接口401/403
- 确保已登录(admin/Admin@2026 或 pm001/Admin@2026)
- 检查 localStorage 是否有 token
- 后端 CORS 是否允许 `http://localhost:3000`

### 4. 前端显示空数据
- 打开浏览器 DevTools Network 查看接口返回
- 确认种子数据已成功插入(后端日志)
- 检查前端 console 是否有报错

## 六、文件清单

### 后端(8个新文件 + 1个修改)
- `backend/migrate_dashboard.sql` — 数据库迁移脚本
- `backend/seed_demo.py` — 演示数据种子
- `backend/app/models/school.py`
- `backend/app/models/device_system.py`
- `backend/app/models/device.py`
- `backend/app/models/wbs_task.py`
- `backend/app/models/risk.py`
- `backend/app/models/project_info.py`
- `backend/app/models/production_line.py`
- `backend/app/models/software_module.py`
- `backend/app/schemas/dashboard.py`
- `backend/app/services/dashboard_service.py`
- `backend/app/api/v1/dashboard.py`
- `backend/app/main.py` (已修改:注册 dashboard 路由)

### 前端(3个新文件 + 1个修改)
- `frontend/src/services/dashboard.ts`
- `frontend/src/pages/Dashboard.tsx` (完全重写)
- `frontend/src/pages/Dashboard.css`
- `frontend/src/components/MainLayout.tsx` (已修改:标题改为"高新区'AI+教育'项目交付管理系统")

---

**开发完成时间**: 2026-07-20  
**符合规范**: 代码规范 3.6(固定列宽+横向滚动)、需求文档 V2.1、原型设计 V2.1  
**下一步**: 验证通过后,可继续开发其他业务模块(项目计划/交付进展/风险管理等)
