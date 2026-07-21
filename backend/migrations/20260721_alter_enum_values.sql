-- ============================================================
-- 枚举值同步迁移脚本
-- 文件：backend/migrations/20260721_alter_enum_values.sql
-- 日期：2026-07-21
-- 版本：040801
-- ============================================================
--
-- 【脚本用途】
--   将开发库 gx_project_dev 已修正的枚举值定义，同步到生产库 gx_project。
--   涉及 4 个字段：
--     1. wbs_tasks.status        -> 待开始, 进行中, 已完成, 已延期, 待补材料
--     2. risks.status            -> 已识别, 应对中, 已关闭
--     3. devices.source          -> 三方外采, 库存设备
--     4. software_modules.phase  -> 需求收集, 需求确认, 软件开发, 软件测试, 软件部署, 上线运行
--   目标值与后端 ORM 模型（backend/app/models/）及 README 枚举摘要表完全一致。
--
-- 【执行前必须确认（重要）】
--   1. 已备份生产库 gx_project（mysqldump 全量备份）。
--   2. software_modules 表必须已存在。若生产库仅用旧版 ddl.sql 初始化过，
--      该表可能缺失（旧 ddl.sql 未包含此表）——需先由 ORM 建表或手工补建，
--      否则第 4 组 ALTER 会报 "Table doesn't exist"。
--   3. 存量脏数据风险：MySQL 收窄 ENUM 时，若表中存在不在新枚举列表内的旧值，
--      严格模式下会报 "Data truncated"，非严格模式下会被清成空串。
--      本脚本采用“先扩容→再映射→后收窄”三步法规避该风险，但 wbs_tasks 的
--      旧值 '已暂停' 无明确对应新值，其映射语句默认注释，需人工确认后启用。
--   4. 第二步的值映射（如 待处理->已识别）为基于语义的推测，
--      执行前请结合实际业务数据核对，必要时调整映射关系。
--
-- 【执行方式】
--   生产库为远程服务器（非本地 Docker）。可用 Navicat 直接连接执行，
--   或命令行（注意指定 utf8mb4 防止中文乱码）：
--     mysql -h <生产库IP> -u<user> -p --default-character-set=utf8mb4 gx_project < 20260721_alter_enum_values.sql
--
-- 【幂等性】
--   全部语句可重复执行：ENUM 已是目标定义时 MODIFY 不报错；
--   UPDATE 映射在旧值已清零时匹配 0 行；最终收窄结果保持一致。
-- ============================================================

USE gx_project;

-- ============================================================
-- 第一步：扩容 ENUM 为「新值 ∪ 旧值」超集
--   目的：让存量旧值在过渡期保持合法，同时允许写入新值，避免直接收窄丢数据。
-- ============================================================

-- 1.1 wbs_tasks.status：旧值可能含 '已暂停'
ALTER TABLE wbs_tasks MODIFY status
  ENUM('待开始','进行中','已完成','已延期','待补材料','已暂停')
  NOT NULL DEFAULT '待开始' COMMENT '状态';

-- 1.2 risks.status：旧值可能含 '待处理','处理中'
ALTER TABLE risks MODIFY status
  ENUM('已识别','应对中','已关闭','待处理','处理中')
  NOT NULL COMMENT '状态';

-- 1.3 devices.source：旧值可能含 '库存发货','外部采购'
ALTER TABLE devices MODIFY source
  ENUM('三方外采','库存设备','库存发货','外部采购')
  NOT NULL COMMENT '设备来源';

-- 1.4 software_modules.phase：新旧值一致，扩容即目标集（前提该表已存在）
ALTER TABLE software_modules MODIFY phase
  ENUM('需求收集','需求确认','软件开发','软件测试','软件部署','上线运行')
  NOT NULL COMMENT '阶段';

-- ============================================================
-- 第二步：将存量旧值映射为新值
--   目的：收窄前把不在目标集内的旧值迁移到语义等价的新值。
--   幂等：旧值已清零时匹配 0 行，重复执行无副作用。
--   注意：以下映射为语义推测，执行前请结合真实数据核对。
-- ============================================================

-- 2.1 wbs_tasks.status：'已暂停' 无明确对应新值，默认注释，人工确认后启用
--     （若确认按“已延期”处理，取消下一行注释）
-- UPDATE wbs_tasks SET status = '已延期' WHERE status = '已暂停';

-- 2.2 risks.status：待处理->已识别，处理中->应对中
UPDATE risks SET status = '已识别' WHERE status = '待处理';
UPDATE risks SET status = '应对中' WHERE status = '处理中';

-- 2.3 devices.source：库存发货->库存设备，外部采购->三方外采
UPDATE devices SET source = '库存设备' WHERE source = '库存发货';
UPDATE devices SET source = '三方外采' WHERE source = '外部采购';

-- 2.4 software_modules.phase：新旧一致，无需映射

-- ============================================================
-- 第三步：收窄 ENUM 为最终目标定义
--   目的：去掉过渡期保留的旧值，使定义与 model/README/ddl 完全一致。
--   前置：第二步已清空所有旧值，否则严格模式会报 Data truncated。
--   若 wbs_tasks 仍有 '已暂停' 数据（第 2.1 未启用），此步会报错，属预期拦截。
-- ============================================================

-- 3.1 wbs_tasks.status
ALTER TABLE wbs_tasks MODIFY status
  ENUM('待开始','进行中','已完成','已延期','待补材料')
  NOT NULL DEFAULT '待开始' COMMENT '状态';

-- 3.2 risks.status
ALTER TABLE risks MODIFY status
  ENUM('已识别','应对中','已关闭')
  NOT NULL COMMENT '状态';

-- 3.3 devices.source
ALTER TABLE devices MODIFY source
  ENUM('三方外采','库存设备')
  NOT NULL COMMENT '设备来源';

-- 3.4 software_modules.phase（已是目标集，重复执行保证一致）
ALTER TABLE software_modules MODIFY phase
  ENUM('需求收集','需求确认','软件开发','软件测试','软件部署','上线运行')
  NOT NULL COMMENT '阶段';

-- ============================================================
-- 第四步：验证查询（执行后逐条运行，确认 Type 列为目标定义）
-- ============================================================
SHOW COLUMNS FROM wbs_tasks LIKE 'status';
SHOW COLUMNS FROM risks LIKE 'status';
SHOW COLUMNS FROM devices LIKE 'source';
SHOW COLUMNS FROM software_modules LIKE 'phase';

-- 期望结果：
--   wbs_tasks.status       -> enum('待开始','进行中','已完成','已延期','待补材料')
--   risks.status           -> enum('已识别','应对中','已关闭')
--   devices.source         -> enum('三方外采','库存设备')
--   software_modules.phase -> enum('需求收集','需求确认','软件开发','软件测试','软件部署','上线运行')

