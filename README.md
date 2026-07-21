# GX教育项目交付管理系统

**版本**: V2.1  
**更新日期**: 2026-07-20  
**仓库**: git@github.com:wtpan3/gx-project.git (Private)

---

## 📋 目录

- [项目简介](#项目简介)
- [快速启动](#快速启动)
- [核心约定](#核心约定)
- [架构决策](#架构决策)
- [数据库表结构](#数据库表结构)
- [核心业务规则](#核心业务规则)
- [API接口规范](#api接口规范)
- [前端路由规划](#前端路由规划)
- [开发进度](#开发进度)
- [重要踩坑记录](#重要踩坑记录)
- [Git工作流](#git工作流)
- [文档索引](#文档索引)

---

## 项目简介

教育信息化项目全生命周期管理平台，涵盖设备管理、任务计划、交付跟踪、培训管理、风险管理、报告生成等核心功能。

### 技术栈

- **前端**: React 18 + TypeScript + Ant Design 5.x
- **后端**: Python 3.11+ + FastAPI + SQLAlchemy ORM
- **数据库**: MySQL 8.0（服务器Docker容器）
- **认证**: JWT Token
- **进程管理**: Screen（开发）/ systemd（生产）
- **Web服务器**: Nginx（生产环境，端口8080）

### 默认账号

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | Admin@2026 | 管理员 |
| pm001 | Admin@2026 | 项目经理 |

---

## 快速启动

### 环境要求
- **Node.js**: 18.x LTS（**不支持20+**）
- **Python**: 3.11+
- **数据库**: 远程MySQL (124.222.151.69)

### 启动命令

#### 后端（必须绑定127.0.0.1）
```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 前端（必须用PowerShell + 手动添加Node到PATH）
```powershell
cd frontend
$env:PATH = "C:\Program Files\nodejs;$env:PATH"
$env:BROWSER='none'
npm start
```

**⚠️ 关键**: bash工具找不到node（PATH缓存问题），必须用PowerShell并手动添加Node到PATH！

### 访问

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| 后端 | http://127.0.0.1:8000 |
| API文档 | http://127.0.0.1:8000/docs |
| 健康检查 | http://127.0.0.1:8000/health |

**登录**: admin / Admin@2026

---

## 核心约定

### 数据库枚举值约定

以下枚举值已与产品原型完全对齐，**开发时必须严格遵守**：

#### 设备来源（devices.source）
```sql
ENUM('三方外采', '库存设备')
```
- `三方外采`：从第三方供应商采购的设备
- `库存设备`：从自有库存调拨的设备

#### 风险状态（risks.status）
```sql
ENUM('已识别', '应对中', '已关闭')
```
- `已识别`：风险已发现，尚未采取措施
- `应对中`：正在采取措施应对
- `已关闭`：风险已解决或消除（首页不显示）

#### 软件模块阶段（software_modules.phase）
```sql
ENUM('需求收集', '需求确认', '软件开发', '软件测试', '软件部署', '上线运行')
```

#### 硬件设备状态（devices.status）
```sql
ENUM('待发货', '已到货', '已安装', '已调试', '运行中')
```

### 菜单顺序（左侧导航栏）

| 序号 | 菜单项 | 说明 |
|------|--------|------|
| 1 | 首页 | 项目概览Dashboard |
| 2 | 项目计划 | WBS任务管理 |
| 3 | 交付进展 | 各学校交付状态 |
| 4 | 风险管理 | 风险列表与跟踪 |
| 5 | 设备信息 | 设备台账 |
| 6 | 学校看板 | 单校全景视图 |
| 7 | 培训管理 | 培训计划与材料 |
| 8 | 报告管理 | 周报/月报生成 |
| 9 | 交付材料库 | 文件统一管理 |
| 10 | 项目复盘 | 验收后复盘 |
| 11 | **系统管理** | **置底**（配置类功能） |

系统管理子菜单：用户管理、学校管理、设备字典、供应商管理、产线类型管理、模板管理、数据字典、项目信息、操作日志

### 数据可下钻（全局交互规范）

**所有列表、统计数字、卡片、图表等数据内容都必须支持下钻**：

| 元素类型 | 下钻行为 | 目标 |
|----------|----------|------|
| 统计卡片 | 点击跳转 | 对应列表页 |
| 环形图扇区 | 点击弹出 | 该状态下的明细列表 |
| 列表行 | 点击行任意区域 | 详情抽屉（Drawer） |
| 甘特图/风险/待办/里程碑行 | 点击行 | 详情抽屉 |

---

## 架构决策

### 前后端通信
- **前端直接调用后端** `http://127.0.0.1:8000`，**无代理**
- 环境变量: `REACT_APP_API_URL`
- 前端统一API客户端: `src/services/api.ts`（自动注入token、401跳转）

### 数据库配置
- **服务器**: 124.222.151.69:3306
- **开发库**: gx_project_dev
- **生产库**: gx_project
- **Root密码**: GX2026!root
- **表数量**: 16张（以 ddl.sql 为准）

### 环境变量

**后端 `.env`**:
```env
DB_HOST=124.222.151.69
DB_PORT=3306
DB_USER=root
DB_PASSWORD=GX2026!root
DB_NAME=gx_project_dev
```

**前端 `.env.development`**:
```env
REACT_APP_API_URL=http://127.0.0.1:8000
```

**前端 `.env.production`**:
```env
REACT_APP_API_URL=http://124.222.151.69:8000
```

### Node 版本要求
- **必须**: Node 18.x LTS（**不支持 20+**）
- **验证**: `node -v` 应显示 v18.x.x

---

## 数据库表结构

### 核心表清单（16张）

| 表名 | 说明 |
|------|------|
| users | 用户表 |
| schools | 学校表 |
| device_systems | 设备系统字典表 |
| suppliers | 供应商表 |
| templates | 模板表 |
| dict_items | 数据字典表 |
| project_info | 项目信息表 |
| operation_logs | 操作日志表 |
| wbs_tasks | WBS任务表 |
| devices | 设备信息表 |
| trainings | 培训计划表 |
| training_schools | 培训学校关联表 |
| risks | 风险管理表 |
| risk_tasks | 风险应对任务关联表 |
| reports | 报告管理表 |
| files | 交付材料库表 |

### Dashboard新增表

**production_lines**（产线类型字典表）
```sql
CREATE TABLE production_lines (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    is_enabled TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**software_modules**（软件模块交付进度表）
```sql
CREATE TABLE software_modules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phase ENUM('需求收集','需求确认','软件开发','软件测试','软件部署','上线运行'),
    progress INT DEFAULT 0,
    expected_completion_date DATE,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**todos**（待办任务表）
```sql
CREATE TABLE todos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority ENUM('高','中','低') DEFAULT '中',
    due_date DATE,
    status ENUM('待处理','已完成') DEFAULT '待处理',
    assignee_id INT,
    creator_id INT,
    source_type ENUM('project','wbs','system') DEFAULT 'project',
    source_id INT,
    transferred_from INT,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 关键字段差异

**schools表**: 使用`full_name`（非name）、`region`（非district）、`campus_manager_id`（非principal）、`is_key`（是否重点学校）

**devices表**: `source` ENUM('三方外采','库存设备')、`status` ENUM('待发货','已到货','已安装','已调试','运行中')

**risks表**: `risk_desc`（非description）、`trigger_condition`、`impact_description`（非impact）、`response_strategy`（非response_plan）、`responsible_person_id`（非owner_id）、`status` ENUM('已识别','应对中','已关闭')

**wbs_tasks表**: 无priority字段、`status` ENUM('未开始','进行中','已完成','已延期','已取消')

---

## 核心业务规则

### 整体进度计算
```
整体进度 = 学校维度30% × 学校完成率 + 硬件维度40% × 硬件完成率 + 软件维度30% × 软件完成率
```

### 首页状态判断

| 状态 | 条件 |
|------|------|
| 正常🟢 | 无延期>7天任务 AND 无高风险项 AND 进度≥计划80% |
| 关注🟡 | 存在延期3-7天任务 OR 存在中风险项 OR 进度<计划80% |
| 异常🔴 | 存在延期>7天任务 OR 存在≥2个高风险项 OR 进度严重滞后 |

### 待办联动规则
- 末级待办全部完成后，上级待办自动标记为"已完成"
- 项目经理可指定负责人、编辑待办信息
- 校园经理可转办自己的待办任务

### WBS自动生成规则
- 设备信息新增时，自动在"交付实施"阶段生成对应WBS任务
- 仅生成建设年份≤当前年份的设备任务
- 设备编辑后：已有任务更新计划时间，新增L4任务，不再需要的标记为孤儿任务

---

## API接口规范

### 统一响应格式
```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```

### 认证方式
- **Header**: `Authorization: Bearer <token>`
- Token有效期: 1440分钟

### 核心API路径

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 认证 | `/api/v1/auth` | 登录/登出/修改密码 |
| 用户 | `/api/v1/users` | 用户CRUD |
| 学校 | `/api/v1/schools` | 学校CRUD |
| Dashboard | `/api/v1/dashboard` | 首页数据 |
| 设备字典 | `/api/v1/device-systems` | 设备规格管理 |
| WBS | `/api/v1/wbs-tasks` | 任务管理 |
| 设备信息 | `/api/v1/devices` | 设备台账 |

---

## 前端路由规划

| 路径 | 页面 | 权限 |
|------|------|------|
| `/login` | 登录页 | 公开 |
| `/dashboard` | 首页概览 | 所有用户 |
| `/project-plan` | 项目计划 | 所有用户 |
| `/delivery-progress` | 交付进展 | 所有用户 |
| `/risk-management` | 风险管理 | 所有用户 |
| `/device-info` | 设备信息 | 所有用户 |
| `/school-dashboard` | 学校看板 | 所有用户 |
| `/training-management` | 培训管理 | 所有用户 |
| `/report-management` | 报告管理 | 所有用户 |
| `/material-library` | 交付材料库 | 所有用户 |
| `/project-review` | 项目复盘 | 所有用户 |
| `/my-todos` | 我的待办 | 所有用户 |
| `/users` | 用户管理 | 管理员/项目经理 |
| `/schools` | 学校管理 | 管理员/项目经理 |
| `/device-systems` | 设备字典 | 管理员/项目经理 |
| `/suppliers` | 供应商管理 | 管理员/项目经理 |
| `/production-lines` | 产线类型 | 管理员/项目经理 |
| `/templates` | 模板管理 | 管理员/项目经理 |
| `/dict-items` | 数据字典 | 管理员/项目经理 |
| `/project-info` | 项目信息 | 管理员/项目经理 |
| `/operation-logs` | 操作日志 | 管理员 |

---

## 开发进度

### ✅ 已完成（截至2026-07-20）

| 模块 | 完成日期 | 说明 |
|------|----------|------|
| 1-1 数据库初始化 | 2026-07-17 | 16张表，admin账号，数据字典 |
| 1-2 用户认证 | 2026-07-17 | JWT Token，登录/登出/改密码 |
| 1-3 用户管理 | 2026-07-17 | CRUD + 重置密码 + 前端页面 |
| Dashboard 首页 | 2026-07-20 | 7卡片 + 3环形图 + 里程碑 + 风险 + 待办 |

### 🔄 进行中

| 模块 | 状态 | 说明 |
|------|------|------|
| 学校管理 | 待开发 | 列表/新增/编辑/删除 + 重点学校标记 |
| 设备字典 | 待开发 | 列表/新增/编辑/删除 + 四字段唯一校验 |

### 📅 待开发

| 模块 | 优先级 | 说明 |
|------|--------|------|
| 1-4 供应商/模板/数据字典/项目信息 | P0 | 系统管理基础模块 |
| 项目计划（WBS） | P1 | 含自动生成逻辑 |
| 设备信息 | P1 | 设备台账 |
| 交付进展 | P2 | 各学校交付状态 |
| 培训管理 | P2 | 培训计划与材料 |
| 风险管理 | P2 | 风险列表与跟踪 |
| 报告管理 | P3 | 周报/月报 |
| 学校看板 | P3 | 单校全景 |
| 交付材料库 | P3 | 文件管理 |
| 项目复盘 | P3 | 验收后复盘 |

---

## 重要踩坑记录

### MySQL中文双重编码
```bash
# 必须指定字符集，否则中文乱码
docker exec -i gx_mysql mysql -uroot -pGX2026!root \
  --default-character-set=utf8mb4 gx_project_dev < ddl.sql
```

### CORS配置
```python
# 不能同时使用 allow_origins=["*"] 和 allow_credentials=True
allow_origins=['http://localhost:3000', 'http://127.0.0.1:3000']
allow_credentials=True
```

### uvicorn --reload 不可靠
改完后端代码若行为没变，手动kill所有python进程重启，别信reload。

### Node环境变量
前端启动必须用PowerShell并手动添加Node到PATH：
```powershell
$env:PATH = "C:\Program Files\nodejs;$env:PATH"
```

### JWT Token格式
JWT的`sub`字段使用**user.id**（不是username）。

---

## Git工作流

### 配置
```bash
user.name: GX-PM
user.email: gx@project.local
origin: git@github.com:wtpan3/gx-project.git
```

### 提交规范
```
<type>(<scope>): <subject>
```

**Type类型**: feat, fix, docs, style, refactor, perf, test, chore, ci

**示例**: `feat(dashboard): 完成首页数据展示`

### 推送流程
```bash
# Claude执行提交
git add .
git commit -m "..."

# 用户手动推送（Claude无GCM认证）
git push origin main
```

### 最近提交
```
d173bd6 fix(auth): 修复CORS配置、旧token兼容与antd警告
ac75939 feat(user): 完成用户管理模块（CRUD + 重置密码）
3a5bc27 chore: 项目架构规范化与环境配置
```

---

## 文档索引

| 文档 | 位置 |
|------|------|
| 需求文档 | [docs/01-需求文档/](docs/01-需求文档/) |
| 技术架构 | [docs/02-架构设计/](docs/02-架构设计/) |
| 部署运维 | [docs/03-部署运维/](docs/03-部署运维/) |
| └ 部署手册 V2.1 | [docs/03-部署运维/部署手册.md](docs/03-部署运维/部署手册.md) |
| └ 生产环境更新流程 SOP | [docs/03-部署运维/更新流程.md](docs/03-部署运维/更新流程.md) |
| 开发规范 | [docs/04-开发规范/](docs/04-开发规范/) |
| 性能优化 | [docs/05-性能优化/](docs/05-性能优化/) |
| 原型设计 | [docs/06-原型设计/](docs/06-原型设计/) |

---

## 快速检查清单

### 启动前
- [ ] Node 版本是 18.x（`node -v`）
- [ ] 后端 `.env` 配置正确（DB_HOST=124.222.151.69）
- [ ] 前端 `.env.development` 存在

### 验证
- [ ] `curl http://127.0.0.1:8000/health` → `{"status":"ok"}`
- [ ] 浏览器访问 http://localhost:3000
- [ ] 登录测试: admin / Admin@2026

---

## 技术支持

- **服务器**: ssh root@124.222.151.69
- **MySQL**: mysql -h 124.222.151.69 -u root -pGX2026!root gx_project_dev

---

**维护者**: GX-PM Team  
**最后更新**: 2026-07-20  
**版本**: V2.1
