# GX教育项目交付管理系统 - 顶层铁律

> 本文件由 Claude Code 自动加载（已实测确认）。
> 本文件是 GX 项目**特有规则**，与全局 CLAUDE.md（C:\Users\wtpan3\.claude\CLAUDE.md）**叠加生效**。
> 通用铁律（§1.1.4 不凭假设 / §1.2.7 危险操作先确认 / §1.2.11 遇障碍不退缩 /
> §1.2.12 单任务执行边界 / §2.x 防偷懒 /verify /debugging / PM身份与风格 / 5Why）见全局，
> 此处不重复，只写项目特有项。

## 项目身份
- 名称：GX教育项目交付管理系统（PM团队内部工具，非客户项目）
- 技术栈：React 18 + FastAPI + MySQL 8.0
- 服务器：124.222.151.69
- 开发库：gx_project_dev（远程）｜生产库：gx_project（远程，禁止直接改）
- 本地：前端 localhost:3000 ｜ 后端 127.0.0.1:8000
- 默认账号：admin / Admin@2026
- 进度状态文件：项目根目录 `state.json`（唯一进度记录处）。每次任务完成后更新；会话开始先读它恢复上下文，会话结束必须记录当前进度/剩余工作/已知问题/下次上下文。

## 铁律（不可违反）

1. 先读地图：**任何任务开始前（包括用户直接扔任务时）**先读 state.json；若是本会话首次响应，主动用一句话汇报上次进度和 next_context，再开始干活。**怀疑失忆时（上下文压缩）主动重读 state.json + 最近修改文件**，不确定时不猜。**涉及业务规则/表结构/API/枚举约定时，动手前先查 README.md 对应章节（含核心业务规则、数据库表结构、API接口规范），不凭记忆。**
2. 禁止脑补：不确定路径/字段/枚举值必须搜索项目；搜不到就说"找不到"，不猜。**禁止用"我觉得/我猜/应该是/大概率"等主观措辞下结论，一切基于可见事实（代码/日志/文档）。**
3. 完成的定义(DoD)：只有 L3 浏览器端到端走通才算"完成"。
   - L1 服务存活 / L2 curl 可达 都不算完成。
   - 前端改动必须 `cd frontend && npm run build` 出现 Compiled successfully。
   - 改数据结构前必须 grep 前端确认如何使用，同步改前端。
4. 强制流程：代码修改走 [诊断]→[方案]→[确认]→[执行]→[记档]。诊断阶段必须自查联动点（涉及多模块/前后端/数据库时列出影响范围），有联动必须先同步修改再动手。
5. 四同步收尾：任务完成后必须同时完成4项——①代码改动 ②相关文档同步更新 ③更新state.json(modified_files+last_decision) ④git commit。**缺任何一项都不算完成**。能回答"为什么改、影响了谁、文档是否同步"三问才算完成。
6. 修复问题立即登记（流程见全局 §2.1+）：本项目登记位置
   f:\claude code\问题登记与复盘\问题登记簿.csv。
7. 临时文件放 ai_workspace/，不散落根目录。
8. 危险操作先确认（清单/话术见全局 §1.2.7）：本项目重点是删除/推送/批量改/reset --hard。
9. 不改生产库；push 规则见下方 Git 段（默认可执行 add/commit，push 前必须说明并获确认）。
10. 配置变更必须记录：修改环境变量/Nginx配置/部署参数时，必须追加到 docs/03-部署运维/配置变更记录.md（时间+修改人+原因+内容），避免配置漂移。
11. 任务前复述需求：开始任务前，先用自己的话复述用户需求，确认理解一致后再动手，避免理解走样。
12. 禁止擅自优化：修Bug就只修Bug，不要顺手重构/加功能。有优化想法先提出确认。全局§1.2.12"单任务边界"适用。
13. 锁死依赖版本：装任何第三方库必须指定具体版本号（如 `axios==1.6.2`），禁止"最新版"/开放范围；同步更新 requirements.txt / package.json。可疑或形似仿冒的包名先向用户说明。

## 结束会话时（用户说"结束会话/下班/收工"）
1. 问题登记检查流程见全局 §2.1++。
2. **必须更新 state.json**，记录4项：
   - 已完成的工作（completed_this_session）
   - 剩余待办（pending）
   - 当前遇到的问题（known_issues）
   - 下次开始的上下文（next_context）
   - 同时更新 last_updated / modified_files / last_decision
3. **任务完成确认清单**（汇报5项）：
   - 已修改文件列表
   - 变更内容摘要
   - 验证方式（L3浏览器/编译/测试）
   - 影响范围（哪些模块/功能）
   - 文档同步情况（哪些文档已同步更新）

## 数据库枚举值（权威=ddl.sql，禁止猜）
| 字段 | 枚举值 |
|------|--------|
| schools.project_status | 未启动, 实施中, 试运行, 已验收, 维保中 |
| wbs_tasks.status | 待开始, 进行中, 已完成, 已延期, 待补材料 |
| wbs_tasks.priority | 高, 中, 低 |
| wbs_tasks.material_status | 无要求, 待上传, 部分上传, 已完成 |
| risks.status | 已识别, 应对中, 已关闭 |
| devices.source | 三方外采, 库存设备 |
| devices.status | 待发货, 已到货, 已安装, 已调试, 运行中 |
| devices.type | 硬件, 软件, 其他 |
| software_modules.phase | 需求收集,需求确认,软件开发,软件测试,软件部署,上线运行 |
| todos.status | 待处理, 已完成 |
| todos.source_type | project, wbs, system |
| templates.status | 启用, 停用 |
| template_wbs_stages.level | L1, L2, L3 |
| todos.priority | 高, 中, 低 |

## 易错字段名（以 ddl.sql / 模型为准）
- schools：full_name(非name)、region(非district)、campus_manager_id(非principal)、is_key、**project_id**
- risks：risk_desc(非description)、impact_description(非impact)、response_strategy(非response_plan)、responsible_person_id(非owner_id)、**project_id**
  - ⚠️ 风险轻量模型：**已删除 probability/impact/response_deadline**，**新增 progress_note**。勿用已删字段。现存字段：risk_desc/trigger_condition/impact_description/risk_level/response_strategy/progress_note/responsible_person_id/status/school_id/**project_id**
- wbs_tasks：task_code(唯一)、responsible_person_id(非assignee_id)、work_content_l4(L4统计口径)、parent_id(层级父子，前端树形依赖)、**project_id**、**requires_material**、**material_status**
- devices：**project_id**、**system_id(FK→systems，权威归属字段)**、system_name(文本，保留兼容，勿作归属判断)、type(硬件/软件/其他)、source(三方外采/库存设备)
- templates：**重大变更（2026-07-28）**— 删除stage字段，新增project_id/template_key/file_name/file_size/file_type/upload_by/download_count/is_latest/is_deleted；type从ENUM改为VARCHAR(50)从字典读；关联WBS改用template_wbs_stages表
- template_wbs_stages：**新表**— template_id/level(L1/L2/L3)/stage_value/is_required
- files：**project_id**、**wbs_task_id**、**template_id**（后两者支持材料卡点机制）
- software_modules：**project_id**、phase(非current_phase)、progress、expected_completion_date、sort_order；**无 code/description 字段**
- production_lines：**project_id**、code/name/description/is_enabled；**无 system_id 字段**（反向关联在 systems.production_line_id）。现有9条真实产品线，demo 3条已删
- systems：**新表（2026-07-28）**— project_id/name/production_line_id(FK→production_lines)/description/sort_order/is_enabled，唯一键(project_id,name)；现有21条。层级 **产线→系统→设备**，对应关系存于数据非代码写死；清单见 需求文档V2.3 §6.11.3
- todos：**project_id**（2026-07-28 首次建表）、parent_id(树形)、transferred_from_id(非transferred_from)
- task_attachments：**无 project_id**，经 task_id→wbs_tasks 间接归属项目
- **已删除的表**（勿引用）：training_schools（并入trainings.school_id）、risk_tasks（风险轻量模型取消）、device_systems、templates_old_20260728
- 外键：responsible_person_id/assignee_id→users.id，school_id→schools.id，**project_id→project_info.id**，**devices.system_id→systems.id**，**systems.production_line_id→production_lines.id**
- 前端责任人显示 assignee_name（由 responsible_person_id JOIN users 查出），数据库无 assignee_name 列
- JWT 的 sub 字段用 user.id（不是 username）

## 文档索引
| 内容 | 位置 |
|------|------|
| 需求 | docs/01-需求文档/ |
| 架构/数据库设计 | docs/02-架构设计/ |
| 部署运维 | docs/03-部署运维/ |
| 开发规范 | docs/04-开发规范/ |
| 测试规范(DoD/L1L2L3) | docs/07-测试规范/测试规范.md |
| 交付自检报告模板 | docs/07-测试规范/交付自检报告模板.md |
| 测试报告模板 | docs/07-测试规范/测试报告模板.md |
| 验收标准清单 | docs/07-测试规范/验收标准清单.md |
| 问题登记 | f:\claude code\问题登记与复盘\问题登记簿.csv |

## 常用命令
| 操作 | 命令 |
|------|------|
| 启动后端 | cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 |
| 启动前端 | cd frontend && $env:BROWSER='none'; npm start |
| 前端编译验证 | cd frontend && npm run build |
| 后端健康 | curl http://127.0.0.1:8000/health |

## 架构约定（易踩坑）
- 前后端通信：开发直连 127.0.0.1:8000；生产 REACT_APP_API_URL **留空**(相对路径走Nginx反代)。切勿填回 http://124.222.151.69:8000（会重现CORS故障）。
- 前端统一用 src/services/api.ts / wbsService.ts，勿硬编码地址（api.ts 空值判断用 !== undefined，空串=相对路径）。
- Node 必须 18.x LTS，不支持 20+。前端启动前 PATH 加 Node：$env:PATH="C:\Program Files\nodejs;$env:PATH"
- CORS：不能同时 allow_origins=["*"] 和 allow_credentials=True。
- API 响应：**当前各接口返回裸 JSON**（如 {items}/{total,items}/{access_token}），**无统一 code/data/message 包装**。新增接口沿用现状，勿假设有统一包装层。认证 Header：Authorization: Bearer <token>，有效期1440分钟。
- API 路径：资源名复数+小写连字符(/wbs-tasks、/device-systems)；嵌套 /schools/{id}/devices；分页 page(从1起)/page_size(默认20,最大100/200)。

## 前端约定（易踩坑）
- 改完必须 npm run build 出现 Compiled successfully 才算语法正确。
- JSX 中 < > & 要转义（&lt; &gt; &amp;）——历史踩坑：< 未转义导致解析错误。
- 状态标签颜色：已完成(绿) 进行中(蓝/橙) 待开始(灰) 已延期(红) 待补材料(橙)。
- 数据可下钻：卡片→列表，环形图扇区→明细，列表/甘特/风险/待办行→详情抽屉。
- 层级树形用后端 parent_id，不要用 l1/l2/l3 路径匹配硬凑（历史踩坑）。
- UI视觉一致性（AI看不见画面，靠约定防走样）：①颜色/字号/间距/圆角以设计稿或本文件既定规范为准，不自编数值；②复杂页面分块做（如先导航栏再列表），一块验收通过再做下一块，不一次整页；③做完组件列"视觉清单"（背景色/边框圆角/内外边距）供对照；④改UI用 playwright-ui-auto 截图，前后版本对比确认无走样。

## MySQL 中文操作规范 — CRITICAL ⭐
导入SQL不加字符集会导致中文ENUM双重编码变乱码（历史P007-P010血泪）。
**必须用封装脚本执行，不要手敲 mysql 命令（避免漏 --default-character-set 参数）：**
```
backend/scripts/import_sql.ps1 <sql文件> [数据库名]   # PowerShell
backend/scripts/import_sql.sh  <sql文件> [数据库名]   # Bash
```
脚本已内置 --default-character-set=utf8mb4。建表/改表均需 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci。
脚本位置：`backend/scripts/import_sql.ps1`（Windows）或 `backend/scripts/import_sql.sh`（Linux/Mac）。

## 其他踩坑
- uvicorn --reload 不可靠：改完后端行为没变，手动 kill 所有 python 进程重启。
- 数据可下钻：所有列表/卡片/图表/行点击都要支持下钻（卡片→列表，扇区→明细，行→详情抽屉）。

## 安全基线（不可违反）
- 密钥隔离：所有密码/密钥/Token 放 `.env`（环境变量），禁止硬编码进代码；.env 不入库。
- 日志脱敏：日志禁止打印密码/Token/完整密钥等敏感信息（按 key 名引用，不打 value）。
- 新增网络暴露的接口/服务若无鉴权，必须主动提示安全影响，不静默创建。

## 核心业务规则（摘要，详细权威版见 README.md）
- 整体进度 = 已完成末级任务数(work_content_l4且status=已完成) / 总末级任务数，**无加权**（2026-07-26定稿，已废弃30/40/30加权，代码/文档已对齐）。
- 首页状态：🟢正常/🟡关注(延期3-7天或中风险或进度<80%)/🔴异常(延期>7天或≥2高风险)
- 待办联动：末级待办全完成→上级自动"已完成"
- WBS自动生成：设备新增时在"交付实施"阶段生成WBS任务(仅建设年份≤当前年)；设备编辑后更新时间/新增L4/多余标记孤儿
- 产线→系统→设备三级：9产线/21系统，权威归属用 devices.system_id（非 system_name）；首页"系统总数"取 systems 表计数，"产线类型"取 production_lines 计数；412条设备 system_id 为 NULL 待设备清单重维护时补

## Git 规范
- 提交格式：<type>(<scope>): <subject>，type=feat/fix/docs/style/refactor/perf/test/chore/ci
- add/commit 由 Claude 直接执行（SSH已配）；**push 前必须先说明提交内容并获用户确认，未经确认不 push main**
