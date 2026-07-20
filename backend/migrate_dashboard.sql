-- ============================================================
-- 首页Dashboard数据模型迁移
-- 版本：V2.1-dashboard
-- 日期：2026-07-20
-- 说明：新增产线/软件模块表,schools加重点标记,risks改状态枚举
-- ============================================================

USE gx_project;

-- 1. schools 表新增重点学校标记
ALTER TABLE schools ADD COLUMN is_priority TINYINT DEFAULT 0 COMMENT '是否重点学校(0否1是)';

-- 2. risks 表修改状态枚举(对齐原型)
ALTER TABLE risks MODIFY COLUMN status ENUM('已识别','应对中','已关闭') NOT NULL DEFAULT '已识别' COMMENT '风险状态';

-- 3. 新建产线类型表
CREATE TABLE IF NOT EXISTS production_lines (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '产线名称',
    description VARCHAR(500) COMMENT '产线描述',
    is_enabled TINYINT DEFAULT 1 COMMENT '是否启用(0否1是)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='产线类型字典表';

-- 4. 新建软件模块进度表
CREATE TABLE IF NOT EXISTS software_modules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '模块名称',
    online_status ENUM('已上线','测试中','开发中','未开始') NOT NULL DEFAULT '开发中' COMMENT '上线状态',
    progress INT DEFAULT 0 COMMENT '完成进度(0-100)',
    sort_order INT DEFAULT 0 COMMENT '排序值',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='软件模块交付进度表';
