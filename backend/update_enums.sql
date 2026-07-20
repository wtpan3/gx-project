-- 更新枚举值以匹配文档要求
-- 执行日期: 2026-07-20

USE gx_project_dev;

-- 1. 更新 devices 表的枚举值
ALTER TABLE devices
  MODIFY COLUMN source ENUM('三方外采', '库存设备'),
  MODIFY COLUMN status ENUM('待发货', '已到货', '已安装', '已调试', '运行中');

-- 2. 更新 risks 表的枚举值
ALTER TABLE risks
  MODIFY COLUMN status ENUM('已识别', '应对中', '已关闭');

-- 3. 更新 schools 表字段名
ALTER TABLE schools
  CHANGE COLUMN is_priority is_key TINYINT DEFAULT 0;

-- 4. 更新 software_modules 表字段
ALTER TABLE software_modules
  CHANGE COLUMN online_status phase ENUM('需求收集', '需求确认', '软件开发', '软件测试', '软件部署', '上线运行') NOT NULL,
  ADD COLUMN expected_completion_date DATE AFTER progress;

-- 5. 更新现有数据以匹配新枚举值

-- 更新设备来源数据
UPDATE devices SET source = '三方外采' WHERE source = '外部采购';
UPDATE devices SET source = '库存设备' WHERE source = '自主研发';

-- 更新设备状态数据
UPDATE devices SET status = '待发货' WHERE status = '待采购';
UPDATE devices SET status = '运行中' WHERE status = '已验收';

-- 更新风险状态数据
UPDATE risks SET status = '已识别' WHERE status = '未处理';
UPDATE risks SET status = '应对中' WHERE status = '处理中';

-- 更新软件模块阶段数据（如果存在旧数据）
-- UPDATE software_modules SET phase = '软件开发' WHERE phase = '开发中';
-- UPDATE software_modules SET phase = '软件测试' WHERE phase = '测试中';
-- UPDATE software_modules SET phase = '上线运行' WHERE phase = '已上线';

SELECT '数据库枚举值更新完成' AS result;
