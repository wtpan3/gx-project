# GX教育项目交付管理系统

**版本**: V2.1  
**更新日期**: 2026-07-20  
**仓库**: git@github.com:wtpan3/gx-project.git (Private)

---

## 📋 目录

- [完成的定义（必读）](#完成的定义definition-of-done必读)
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

## 完成的定义（Definition of Done，必读）

> 这是本项目所有开发、修改、部署工作的**总原则**，优先级高于一切其他约定。

**任何工作，必须用「真实使用场景」验证通过，才能称为"完成"。**

### 什么不算"完成"

- ❌ "代码写完了" —— 那只是写完，不是完成
- ❌ "接口 curl 返回 200 了" —— curl 绕过浏览器的 CORS/JS/连锁请求，测不出真实问题
- ❌ "服务起来了 / 编译过了" —— 进程在跑 ≠ 用户能用

### 什么才算"完成"

**用真实场景走通**：像真实用户那样，在浏览器里操作完整路径，确认无误。

| 场景 | "完成"的验证标准 |
|------|----------------|
| 开发环境改了某功能 | 浏览器打开对应页面，实际操作该功能走通，F12 无报错 |
| 部署到生产 | 浏览器打开生产地址，登录 → 进首页 → 点核心页面全部走通 |
| 改了接口 | 不只测该接口，还要测**调用它的前端页面**在浏览器里正常 |

### 铁律

1. **区分并如实报告验证级别**：进程存活(L1) / 接口可达(L2) / 浏览器端到端(L3)。只有 L3 通过才可说"完成、可使用"。
2. **禁止用 L1/L2 冒充 L3**：不得在只做了 curl 的情况下宣布"可以用了"。
3. **有未验证项必须明说**："X 已验证，Y 未验证"，不含糊。
4. 详细规范见 [测试规范.md](docs/07-测试规范/测试规范.md)、[更新流程.md](docs/03-部署运维/更新流程.md)。

---

## 项目简介

教育信息化项目全生命周期管理平台，涵盖设备管理、任务计划、交付跟踪、培训管理、风险管理、报告生成等核心功能。

### 技术栈

- **前端**: React 18 + TypeScript + Ant Design 5.x
- **后端**: Python 3.11+ + FastAPI + SQLAlchemy ORM
- **数据库**: MySQL 8.0（服务器Docker容器）
- **认证**: JWT Token
- **AI模型**: MiniMax-M系列（M3/M2.7/M2.5及highspeed版本）
- **向量数据库**: FAISS（本地）/ Milvus（生产可选）
- **RAG框架**: LangChain
- **微信接入**: 普通微信公众号 + OpenClaw
- **进程管理**: Screen（开发）/ systemd（生产）
- **Web服务器**: Nginx（生产环境，端口80，反代 /api 到后端8000）

### 默认账号

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | Admin@2026 | 管理员 |
| pm001 | Admin@2026 | 项目经理 |

---

## 快速启动

**后端**:
```bash
cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**前端** (PowerShell):
```powershell
cd frontend; $env:PATH="C:\Program Files\nodejs;$env:PATH"; $env:BROWSER='none'; npm start
```

**访问**: http://localhost:3000 (前端) | http://127.0.0.1:8000 (后端API) | 登录: admin / Admin@2026

**完整启动流程**（环境要求、依赖安装、常见报错处理）详见 **[本地启动手册.md](本地启动手册.md)**。

---

## 核心约定

### 数据库枚举值约定

> ⚠️ **枚举值权威来源已统一到 [CLAUDE.md](CLAUDE.md) 的"数据库枚举值"章节**（与 ddl.sql 对齐）。
> 开发时以 CLAUDE.md / ddl.sql 为准，本处不再重复维护，避免两处不一致。

涉及：devices.source/status、risks.status、software_modules.phase、
wbs_tasks.status/priority、todos.priority。

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

系统管理子菜单：用户管理、学校管理、设备字典、供应商管理、产线类型管理、模板管理、数据字典、项目信息、AI配置、微信对话、问答机器人、操作日志

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
- **开发环境**：前端直接调后端 `http://127.0.0.1:8000`（`.env.development` 配置）
- **生产环境**：前端用**相对路径**（`REACT_APP_API_URL` 置空），请求经 **Nginx 反代**到后端（同源，无 CORS）
- 前端统一API客户端: `src/services/api.ts`、`src/services/wbsService.ts`，勿硬编码地址

> ⚠️ 关键约束（生产留空、CORS、Node 18）已收录到 [CLAUDE.md](CLAUDE.md) 的"架构约定"章节，此处仅作背景说明。
> 历史更正：早期"前端直连后端:8000、无代理"曾导致生产 CORS 拦截登录失败，现改为生产走 Nginx 反代。

### 数据库配置
- **服务器**: 124.222.151.69:3306
- **开发库**: gx_project_dev
- **生产库**: gx_project
- **Root密码**: GX2026!root
- **表数量**: 19张（核心15张 + Dashboard新增4张：production_lines + systems + software_modules + todos）

### 环境变量

**后端 `.env`**:
```env
DB_HOST=124.222.151.69
DB_PORT=3306
DB_USER=root
DB_PASSWORD=GX2026!root
DB_NAME=gx_project_dev
```

**前端**: 开发 `.env.development` 填 `REACT_APP_API_URL=http://127.0.0.1:8000`；
生产 `.env.production` **留空**（相对路径走 Nginx 反代，切勿填回后端地址——详见 CLAUDE.md）。

### Python 环境
- **生产环境**: systemd 直接用系统 `/usr/bin/python3`，**无虚拟环境 venv**
- **本地开发**: 可选用 venv 隔离依赖（非必须）

---

## 数据库表结构

### 核心表清单（15张）

| 表名 | 说明 |
|------|------|
| users | 用户表 |
| schools | 学校表 |
| suppliers | 供应商表 |
| templates | 模板表 |
| template_wbs_stages | 模板关联WBS阶段表 |
| dict_items | 数据字典表 |
| project_info | 项目信息表 |
| operation_logs | 操作日志表 |
| wbs_tasks | WBS任务表 |
| task_attachments | 任务佐证材料表 |
| devices | 设备信息表 |
| trainings | 培训计划表 |
| risks | 风险管理表 |
| reports | 报告管理表 |
| files | 交付材料库表 |

> 已删除表（勿引用）：`risk_tasks`（风险轻量模型取消）、`device_systems`、`training_schools`、`templates_old_20260728`。

### Dashboard新增表（4张）

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

> 现有9条真实产品线（2026-07-28 定稿）：PL-CLASSROOM 大课堂、PL-DAXUEQING 大学情、PL-PLATFORM 平台产品线、PL-STEAM 科创教育、PL-EXAM-LANG 考试与语言学习产品线、PL-SPORT 智慧体育产品线、PL-MENTAL 智慧心育产品线、PL-SCIPOP 科普研究院、PL-READING 读写科技。

**systems**（系统字典表，2026-07-28 新增）
```sql
CREATE TABLE systems (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL DEFAULT 1,
    name VARCHAR(100) NOT NULL,
    production_line_id INT,          -- FK→production_lines.id ON DELETE SET NULL
    description VARCHAR(500),
    sort_order INT DEFAULT 0,
    is_enabled TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_systems_project_name (project_id, name)
);
```
> 层级链路：**产线 → 系统 → 设备**（`systems.production_line_id` + `devices.system_id`）。现有21个系统，产线↔系统对应关系为运行期可维护数据（改字典即改关系，非代码写死），完整清单见 `docs/01-需求文档/需求文档-GX教育项目交付管理系统V2.3.md` §6.11.3。
> `devices.system_name`（文本）保留兼容，权威归属字段为 `devices.system_id`；当前828条设备已回填，412条为NULL待设备清单重新维护时补齐。

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

> ⚠️ **易错字段名（full_name≠name 等）权威列表见 [CLAUDE.md](CLAUDE.md) "易错字段名"章节**。
> 字段名一律以 `ddl.sql` 与代码模型为准（三方已对齐）。

涉及：schools(full_name/region/campus_manager_id/is_key)、
devices(source/status)、risks(risk_desc/impact_description/response_strategy/responsible_person_id)、
wbs_tasks(task_code/priority/responsible_person_id/status/parent_id)。

---

## 核心业务规则

> 本章是业务规则的**详细权威版**；CLAUDE.md 只保留速记摘要，改动时以本章为准。

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

### 产线 → 系统 → 设备 层级规则（2026-07-28 建立）

```
production_lines (9条产品线)
    └── systems (21个系统, systems.production_line_id → production_lines.id)
            └── devices (devices.system_id → systems.id)
```

- **权威归属字段**：`devices.system_id`（非 `devices.system_name`）。`system_name` 为历史文本字段，保留兼容，不作为归属判断依据。
- **对应关系可运行期维护**：产线↔系统关系是 `systems` 表的数据，改字典即改关系，**未在代码中写死**；新增/调整系统只需增改 `systems` 行。
- **统计口径**：首页"系统总数"卡片取 `systems` 表 `is_enabled=1` 计数（=21），"产线类型"取 `production_lines` 计数（=9）。**已废弃**原口径 `COUNT(DISTINCT devices.system_name)`。
- **已知数据缺口**：412条设备 `system_id` 为 NULL（原 `system_name` 为「AI算力中心」「智能交互终端」，经确认这两个系统不存在，故不建字典项），待设备清单重新维护时逐条归属；828条已回填。
- 9条产线与21个系统的完整对应清单见 `docs/01-需求文档/需求文档-GX教育项目交付管理系统V2.3.md` §6.11.3。

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

> 高频踩坑（MySQL中文编码、uvicorn reload、CORS、Node）的**速记版在 [CLAUDE.md](CLAUDE.md)**；本章为含复现/排查的详细版。

### MySQL中文双重编码问题 ⚠️

**问题根因**：导入SQL时未指定字符集，导致ENUM中文值被双重编码（UTF-8套UTF-8）。

**受影响字段清单**（已在2026-07-22修复）：
| 表名 | 字段 | 原ENUM值(双重编码) | 修复后 |
|------|------|-------------------|--------|
| software_modules | phase | 乱码6个phase值 | '需求收集','需求确认','软件开发','软件测试','软件部署','上线运行' |
| todos | priority | 乱码 | '高','中','低' |
| todos | status | 乱码 | '待开始','进行中','已完成' |

**预防方法 - MySQL操作规范** ⭐:

> **强制规则**: 任何涉及中文数据的MySQL操作，必须遵循本节规范。违反将导致数据损坏。

#### 1. 导入SQL文件（必须指定字符集）— CRITICAL ⭐

**推荐方式: 使用封装脚本（自动加字符集参数）**

```bash
# Bash (Git Bash / WSL)
./scripts/import_sql.sh ddl.sql                    # 导入到默认数据库 gx_project_dev
./scripts/import_sql.sh migration.sql gx_project   # 导入到指定数据库

# PowerShell
.\scripts\import_sql.ps1 ddl.sql                   # 导入到默认数据库
.\scripts\import_sql.ps1 migration.sql gx_project  # 导入到指定数据库
```

**封装脚本位置**: 
- Bash: `backend/scripts/import_sql.sh` ✅
- PowerShell: `backend/scripts/import_sql.ps1` ✅
- 功能：自动添加 `--default-character-set=utf8mb4` 参数，防止中文双重编码

**手动导入（必须加字符集参数）**

```bash
# ✅ 正确做法 - 必须加 --default-character-set=utf8mb4
docker exec -i gx_mysql mysql -uroot -pGX2026!root \
  --default-character-set=utf8mb4 gx_project_dev < ddl.sql

# ❌ 错误做法 - 不加字符集参数会导致中文双重编码
docker exec -i gx_mysql mysql -uroot -pGX2026!root \
  gx_project_dev < ddl.sql  # 会出现乱码！
```

**为什么必须加这个参数？**
- MySQL客户端默认字符集可能是latin1
- 不指定utf8mb4会把UTF-8中文当作latin1再转一次UTF-8
- 结果：`'硬件'` 变成 `0xc3a7c2a1...` 乱码hex

**历史血泪教训**（来自问题登记簿）:
- P008: software_modules.phase 双重编码
- P009: todos.priority 双重编码
- P010: todos.status 双重编码
- **共同根因**: 导入SQL时忘记加 `--default-character-set=utf8mb4`

#### 2. 创建表时的字符集规范

```sql
-- ✅ 建表必须指定表级字符集
CREATE TABLE devices (
  id INT PRIMARY KEY,
  type ENUM('硬件','软件','其他') NOT NULL
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ✅ ENUM字段包含中文时，表必须是utf8mb4
CREATE TABLE todos (
  priority ENUM('高','中','低')
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 3. 修改表结构时保持字符集一致

```sql
-- ✅ 修改ENUM前先检查表字符集
SHOW CREATE TABLE software_modules;

-- ✅ 修改时保持字符集
ALTER TABLE software_modules 
  MODIFY phase ENUM('需求收集','需求确认','软件开发','软件测试','软件部署','上线运行') 
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**排查方法**（检查是否还有双重编码）：
```sql
-- 查看ENUM定义,如果显示乱码/hex则有问题
SHOW COLUMNS FROM software_modules LIKE 'phase';
SHOW COLUMNS FROM todos LIKE 'priority';

-- 查看表字符集
SHOW CREATE TABLE software_modules;
```

**历史问题记录**：
- 2026-07-22: 3个字段(software_modules.phase/todos.priority/todos.status)发生双重编码
- 根因: 导入ddl.sql时未加 --default-character-set=utf8mb4
- 修复: 逐表ALTER MODIFY重新定义ENUM
- 预防: 本节规范写入README，强制执行

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

> 提交格式与 push 前确认约束的**速记版在 [CLAUDE.md](CLAUDE.md)**；本章为完整说明。

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

`git add` / `git commit` / `git push` **均由 Claude 直接执行**（本地与服务器均已配置 GitHub SSH 认证，push 可正常工作）。

```bash
git add <files>
git commit -m "type(scope): subject"
git push origin main
```

**唯一约束：push 前必须先向用户说明将推送的提交内容并获得确认**（push 是对外、影响远程仓库的不可逆操作）。

> ⚠️ 历史更正：早期文档曾写"用户手动推送（Claude 无 GCM 认证）"——此假设**错误且从未验证**，已作废。Claude 具备 push 能力，改为"执行前确认"模式。

### 最近提交
```
d173bd6 fix(auth): 修复CORS配置、旧token兼容与antd警告
ac75939 feat(user): 完成用户管理模块（CRUD + 重置密码）
3a5bc27 chore: 项目架构规范化与环境配置
```

---

## 文档索引

> **本 README 是基准文档，先读它。** 下表按"场景"告诉你接着该读哪个文档。

### 按场景查文档（What to read When）

| 我要做什么 | 先读这个文档 |
|-----------|-------------|
| 了解项目全貌、约定、踩坑 | 本 README（基准，必读） |
| 开发新功能前，看需求 | [需求文档](docs/01-需求文档/) |
| 设计表结构 / 查字段 | [数据库设计](docs/02-架构设计/) + `ddl.sql`（以 ddl.sql 为准） |
| 理解系统架构、技术选型 | [技术架构说明](docs/02-架构设计/技术架构说明.md) |
| **提交/推送代码** | [Git提交规范](docs/04-开发规范/Git提交规范.md)（含 push 执行约定） |
| 写代码前看编码规范 | [代码规范](docs/04-开发规范/代码规范.md) |
| **开发完成后做测试** | [测试规范](docs/07-测试规范/测试规范.md)（含真实场景端到端） |
| **部署/更新到生产** | [更新流程 SOP](docs/03-部署运维/更新流程.md)（含部署后验证清单） |
| 首次部署 / 环境搭建 | [部署手册](docs/03-部署运维/部署手册.md) |
| 线上出问题排查 | [问题排查SOP](docs/03-部署运维/问题排查SOP.md) + [常见问题FAQ](docs/03-部署运维/常见问题FAQ.md) |
| 性能/安全/灾备 | [性能优化](docs/05-性能优化/) |
| 看原型 / UI 设计 | [原型设计](docs/06-原型设计/) |

### 完整目录

| 目录 | 位置 |
|------|------|
| 需求文档 | [docs/01-需求文档/](docs/01-需求文档/) |
| 架构设计 | [docs/02-架构设计/](docs/02-架构设计/) |
| 部署运维 | [docs/03-部署运维/](docs/03-部署运维/) |
| └ 部署手册 | [docs/03-部署运维/部署手册.md](docs/03-部署运维/部署手册.md) |
| └ 更新流程 SOP | [docs/03-部署运维/更新流程.md](docs/03-部署运维/更新流程.md) |
| 开发规范 | [docs/04-开发规范/](docs/04-开发规范/) |
| 性能优化 | [docs/05-性能优化/](docs/05-性能优化/) |
| 原型设计 | [docs/06-原型设计/](docs/06-原型设计/) |
| 测试规范 | [docs/07-测试规范/](docs/07-测试规范/) |
| 历史归档 | [docs/08-历史归档/](docs/08-历史归档/)（临时报告，仅供参考） |

> **问题登记与复盘已迁移到全局**:[`f:\claude code\问题登记与复盘\`](f:/claude%20code/%E9%97%AE%E9%A2%98%E7%99%BB%E8%AE%B0%E4%B8%8E%E5%A4%8D%E7%9B%98/)

---

## 快速检查清单

### 启动前
- [ ] Node 版本是 18.x（`node -v`）
- [ ] 后端 `.env` 配置正确（DB_HOST=124.222.151.69）
- [ ] 前端 `.env.development` 存在

### 问题修复后(必做)
- [ ] L3浏览器端到端验证通过
- [ ] **登记到问题簿**: `python scripts/log_issue.py`(30秒)

详见 **[问题登记工作流](docs/09-项目复盘/问题登记工作流.md)**

### 验证（按"完成的定义"，必须走到 L3 端到端）

验证分3个级别(L1服务存活 / L2接口连通 / L3浏览器端到端),**只有 L3 通过才算"完成/可用"**。

详细清单与工具见 **[测试规范.md 第五章](docs/07-测试规范/测试规范.md#五真实场景端到端测试强制开发与部署通用)**。

> ⚠️ 只做 curl(L2) 不算验证完成。curl 测不出 CORS/前端报错——本项目曾因此连续误判"部署成功"。

---

## 已知问题（待修复）

### 1. Device 模型字段名与数据库不匹配

**问题**：backend/app/models/device.py 的3个字段名与数据库列名不一致：

| models.py | 数据库实际列名 |
|-----------|---------------|
| installation_date | install_date |
| debugging_date | debug_date |
| acceptance_date | accept_date |

**影响**：当前 Dashboard 碰巧未使用这3个字段,能正常运行。但只要有功能 SELECT/INSERT 这些字段就会抛 500 错误。

**修复方向**：
- 方案A(推荐): 改 models.py 字段名对齐数据库（`installation_date` → `install_date`）
- 方案B: ALTER TABLE 给数据库加别名列（造成冗余）

### 2. Dashboard 统计逻辑待优化

| 项 | 当前逻辑 | 建议优化 |
|----|----------|---------|
| 重点学校卡片显示0 | 演示数据所有 schools.is_key=0 | 标记1-2所学校为重点 |
| 设备类型数=180 | 统计逻辑可能不准 | 改为 `COUNT(DISTINCT device_name)` |
| Dashboard 待办来源 | 只显示 wbs_tasks | 考虑合并 todos 表数据？ |

**说明**：这些是业务逻辑/产品设计问题,非技术bug,需产品决策是否调整。

---

## 技术支持

- **服务器**: ssh ubuntu@124.222.151.69
- **MySQL**: docker exec -it gx_mysql mysql -uroot -pGX2026!root gx_project

---

**维护者**: GX-PM Team  
**最后更新**: 2026-07-22
**版本**: V2.1
