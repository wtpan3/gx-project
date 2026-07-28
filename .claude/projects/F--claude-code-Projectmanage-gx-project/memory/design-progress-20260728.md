---
name: design-progress-20260728
description: 2026-07-28架构设计与文档同步工作进度
metadata:
  type: project
---

# 2026-07-28 架构设计与文档同步进度

## 完成工作

### 1. 学校状态枚举统一
- 修改 `backend/app/models/school.py` 的 project_status 枚举
- 从 `('未启动','实施中','已完成','已验收','维护中')` 改为 `('未启动','实施中','试运行','已验收','维保中')`
- 与 ddl.sql 对齐为旧5态
- 数据库查询确认20所学校的 project_status 均为 NULL，无历史数据迁移风险
- 补充 CLAUDE.md 枚举值清单

### 2. 删除device_systems表（重大架构调整）
**核心诉求**：去除与devices表的重复字段，所有设备信息在devices表直接维护

**执行步骤**：
1. 数据备份：6条device_systems + 1240条devices
2. 数据库迁移：
   - 添加 devices.system_name 字段
   - 从 device_systems 回填 system_name 到1240条devices
   - 删除 devices.system_id 外键约束
   - 删除 devices.system_id 列
   - 删除 device_systems 表
3. ORM模型修改：删除 device_system.py，修改 device.py
4. 业务代码修改：Dashboard统计改为按 Device.system_name 去重
5. 脚本文件更新：clear_demo.py、seed_demo.py、check_schema.py
6. 前端路由清理：删除 /device-systems 路由
7. DDL同步：ddl.sql 删除建表语句，修改devices表定义

**验证结果**：
- ✅ device_systems表已删除
- ✅ devices.system_name字段存在
- ✅ devices.system_id字段已删除
- ✅ 1240条devices的system_name已回填
- ✅ Device模型加载成功
- ✅ Dashboard统计系统数改为去重查询

### 3. 文档全面同步
**数据库设计.md**：
- 删除 2.3 device_systems 章节
- 修改 2.9 devices 表定义（system_id改system_name）
- 枚举值统一：
  - devices.type: 硬件/软件/其他（原文档错写"服务"）
  - devices.source: 三方外采/库存设备（原文档错写"库存发货/外部采购"）
  - devices.status: 5态（原文档错写6态含已发货/已验收）
- 删除唯一约束表和外键约束表中的device_systems相关项

**需求文档V2.3.md**：
- 4.3设备字典章节添加架构变更说明（2026-07-28删表，功能合并至设备信息）

**开发排期总表V2.2.md**：
- 标注设备字典模块已废弃
- P0清单删除设备字典开发任务
- D1字段变更作废（device_systems表已不存在）

## Git提交

**Commit 1**: `156cdd8` - refactor: 删除device_systems表，devices独立管理  
**Commit 2**: `03a3404` - docs: 同步文档与实际数据库结构

## 发现的遗留问题

### 问题1：Dashboard首页状态口径不一致
- 首页环形图：6态（待启动/装修中/安装中/调试中/培训中/已完成），从WBS任务动态计算
- schools.project_status字段：5态（未启动/实施中/试运行/已验收/维保中），全部NULL未使用
- **建议**：明确两套并存的定位，或统一为一套

### 问题2：排期表字段变更待办
- D2: devices缺 serial_numbers 字段（批次序列号记录）
- D5: devices.source 命名已统一✅
- 原D1（device_systems加production_line_id）已作废，如需产线关联应改为devices表加

### 问题3：数据库设计文档历史脱节严重
已通过本次全面更新修复大部分问题，当前文档与ddl.sql/models基本对齐。

## 下次会话建议

1. 决策：Dashboard首页6态 vs 字段5态如何处理
2. 补充：devices表缺失字段（serial_numbers等）
3. 继续：Playwright测试修复或其他待办任务

**Why**: 完成了一次重大架构调整（删除冗余表）和文档对齐工作，为后续P0模块开发扫清障碍。

**How to apply**: 
- 下次开发设备信息模块时，直接在devices表维护所有字段，无需考虑字典表
- 文档修改参考本次模式：代码改动 → 文档同步 → Git分批提交
- 架构变更在需求文档中明确标注变更日期和理由，保留历史参考价值
