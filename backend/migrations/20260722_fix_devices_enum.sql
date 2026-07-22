-- ============================================================
-- 补充迁移脚本：修正 devices 表 type 和 status 枚举
-- 文件：backend/migrations/20260722_fix_devices_enum.sql
-- 日期：2026-07-22
-- 版本：040802
-- ============================================================
--
-- 【脚本用途】
--   补充 20260721_alter_enum_values.sql 遗漏的两个字段：
--     1. devices.type   -> 硬件, 软件, 其他 (ddl.sql写的是'服务',实际models.py是'其他')
--     2. devices.status -> 待发货, 已到货, 已安装, 已调试, 运行中
--
-- 【根本原因】
--   ddl.sql 和 models.py 不一致:
--     ddl.sql:   type=('硬件','软件','服务'), status=('待发货','已发货','已到货','已安装','已调试','已验收')
--     models.py: type=('硬件','软件','其他'), status=('待发货','已到货','已安装','已调试','运行中')
--   生产库用 ddl.sql 建的,但代码用 models.py 跑,导致演示数据插入失败。
--
-- 【执行前必须确认】
--   1. 已备份生产库 gx_project
--   2. devices 表当前无数据或确认可以丢弃旧数据(ENUM值变化会截断不匹配的旧值)
--   3. 本脚本幂等:重复执行安全
--
-- ============================================================

USE gx_project;

-- 修正 devices.type: '硬件','软件','服务' → '硬件','软件','其他'
ALTER TABLE devices MODIFY COLUMN type
  ENUM('硬件','软件','其他') NOT NULL
  COMMENT '设备类型';

-- 修正 devices.status: 去掉'已发货'/'已验收',改为'运行中'
ALTER TABLE devices MODIFY COLUMN status
  ENUM('待发货','已到货','已安装','已调试','运行中')
  COMMENT '当前状态';

-- 验证
SHOW COLUMNS FROM devices LIKE 'type';
SHOW COLUMNS FROM devices LIKE 'status';

-- 期望结果:
--   devices.type   -> enum('硬件','软件','其他')
--   devices.status -> enum('待发货','已到货','已安装','已调试','运行中')
