-- 创建数据库
CREATE DATABASE IF NOT EXISTS gx_project 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE gx_project;

-- ==================== 用户表 ====================
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '登录账号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    role ENUM('admin','project_manager','campus_manager') NOT NULL COMMENT '角色',
    phone VARCHAR(20) UNIQUE NOT NULL COMMENT '手机号',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    status ENUM('启用','停用') DEFAULT '启用' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==================== 学校表 ====================
CREATE TABLE schools (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL COMMENT '学校编码',
    full_name VARCHAR(200) NOT NULL COMMENT '学校全称',
    region VARCHAR(100) NOT NULL COMMENT '所属区域',
    address VARCHAR(255) COMMENT '详细地址',
    campus_manager_id INT COMMENT '校园经理ID',
    contact_person VARCHAR(50) NOT NULL COMMENT '校方联系人',
    contact_phone VARCHAR(20) NOT NULL COMMENT '校方联系电话',
    project_status ENUM('未启动','实施中','试运行','已验收','维保中') DEFAULT '未启动',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (campus_manager_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ==================== 设备系统字典表 ====================
CREATE TABLE device_systems (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(100) NOT NULL COMMENT '项目名称',
    construction_year INT NOT NULL COMMENT '建设年份',
    system_name VARCHAR(100) NOT NULL COMMENT '系统名称',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    brand VARCHAR(100) NOT NULL COMMENT '品牌',
    model VARCHAR(100) NOT NULL COMMENT '型号',
    params TEXT COMMENT '技术参数',
    type ENUM('硬件','软件','服务') NOT NULL COMMENT '设备类型',
    unit VARCHAR(20) NOT NULL COMMENT '单位',
    plan_quantity INT NOT NULL COMMENT '计划数量',
    is_enabled TINYINT DEFAULT 1 COMMENT '是否启用(软删除)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_project_system_device_year (project_name, system_name, device_name, construction_year)
);

-- ==================== 供应商表 ====================
CREATE TABLE suppliers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL COMMENT '供应商名称',
    contact_person VARCHAR(50) NOT NULL COMMENT '联系人',
    contact_phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    contact_email VARCHAR(100) COMMENT '联系邮箱',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==================== 模板表 ====================
CREATE TABLE templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '模板名称',
    type VARCHAR(50) NOT NULL COMMENT '模板类型',
    stage VARCHAR(50) NOT NULL COMMENT '关联阶段',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    version VARCHAR(20) NOT NULL COMMENT '版本号',
    description TEXT COMMENT '说明',
    status ENUM('启用','停用') DEFAULT '启用' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==================== 数据字典表 ====================
CREATE TABLE dict_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category VARCHAR(50) NOT NULL COMMENT '字典分类',
    label VARCHAR(100) NOT NULL COMMENT '显示名称',
    value VARCHAR(100) NOT NULL COMMENT '值',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_enabled TINYINT DEFAULT 1 COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_category_value (category, value)
);

-- ==================== 项目信息表 ====================
CREATE TABLE project_info (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(100) NOT NULL COMMENT '项目名称',
    project_code VARCHAR(50) UNIQUE NOT NULL COMMENT '项目编码',
    start_date DATE NOT NULL COMMENT '项目开始日期',
    end_date DATE NOT NULL COMMENT '项目结束日期',
    overall_status ENUM('未启动','进行中','试运行','已验收','已结项') DEFAULT '未启动' COMMENT '项目整体状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ==================== 操作日志表 ====================
CREATE TABLE operation_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '操作人ID',
    module VARCHAR(50) NOT NULL COMMENT '所属模块',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    target_id INT COMMENT '操作目标ID',
    before_data JSON COMMENT '变更前数据',
    after_data JSON COMMENT '变更后数据',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    batch_file_name VARCHAR(255) COMMENT '批量导入文件名',
    batch_success_count INT COMMENT '批量成功数',
    batch_fail_count INT COMMENT '批量失败数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ==================== 初始化数据 ====================

-- 1. 初始管理员账号（密码：Admin@2026）
INSERT INTO users (username, password_hash, real_name, role, phone, email, status) 
VALUES ('admin', '$2b$12$w6FVXvZxVKZBVaYp9GX1aeLQZ.C9MhBqQYrVZ8WjVXvZxVKZBVaY', '系统管理员', 'admin', '13800000000', 'admin@gx.com', '启用');

-- 2. 项目信息
INSERT INTO project_info (project_name, project_code, start_date, end_date, overall_status) 
VALUES ('GXAI+教育项目', 'GX2026', '2026-01-01', '2026-12-31', '进行中');

-- 3. 数据字典 - 关联阶段
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('关联阶段', '到货验收', '到货验收', 1),
('关联阶段', '加电测试', '加电测试', 2),
('关联阶段', '校级验收', '校级验收', 3),
('关联阶段', '培训', '培训', 4),
('关联阶段', '无', '无', 5);

-- 4. 数据字典 - 建设年份
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('建设年份', '2026', '2026', 1),
('建设年份', '2027', '2027', 2),
('建设年份', '2028', '2028', 3);

-- 5. 数据字典 - WBS状态（含待补材料）
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('WBS状态', '待开始', '待开始', 1),
('WBS状态', '进行中', '进行中', 2),
('WBS状态', '已完成', '已完成', 3),
('WBS状态', '已延期', '已延期', 4),
('WBS状态', '待补材料', '待补材料', 5);

-- 6. 数据字典 - 项目整体状态
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('项目整体状态', '未启动', '未启动', 1),
('项目整体状态', '进行中', '进行中', 2),
('项目整体状态', '试运行', '试运行', 3),
('项目整体状态', '已验收', '已验收', 4),
('项目整体状态', '已结项', '已结项', 5);

-- 7. 数据字典 - L1阶段
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('L1阶段', '启动规划', '启动规划', 1),
('L1阶段', '交付实施', '交付实施', 2),
('L1阶段', '验收移交', '验收移交', 3),
('L1阶段', '运营维护', '运营维护', 4);

-- 8. 数据字典 - L2子阶段（启动规划）
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('L2子阶段_启动规划', '合同交底', '合同交底', 1),
('L2子阶段_启动规划', '团队组建', '团队组建', 2),
('L2子阶段_启动规划', '实施方案编制', '实施方案编制', 3);

-- 9. 数据字典 - L2子阶段（交付实施）
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('L2子阶段_交付实施', '硬件交付', '硬件交付', 1),
('L2子阶段_交付实施', '软件交付', '软件交付', 2),
('L2子阶段_交付实施', '应用培训', '应用培训', 3);

-- 10. 数据字典 - L2子阶段（验收移交）
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('L2子阶段_验收移交', '竣工资料提交', '竣工资料提交', 1),
('L2子阶段_验收移交', '业主验收会', '业主验收会', 2),
('L2子阶段_验收移交', '资产移交确认', '资产移交确认', 3);

-- 11. 数据字典 - L2子阶段（运营维护）
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('L2子阶段_运营维护', '日常运维', '日常运维', 1),
('L2子阶段_运营维护', '定期巡检', '定期巡检', 2),
('L2子阶段_运营维护', '故障处理', '故障处理', 3);
