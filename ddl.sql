-- ============================================================
-- GX教育项目交付管理系统 - 数据库完整DDL（16张表）
-- 版本：V2.1
-- 日期：2026-07-17
-- 字符集：utf8mb4
-- ============================================================

CREATE DATABASE IF NOT EXISTS gx_project 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE gx_project;

-- ============================================================
-- 1. users - 用户表
-- ============================================================
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '登录账号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希(bcrypt)',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    role ENUM('admin','project_manager','campus_manager') NOT NULL COMMENT '角色',
    phone VARCHAR(20) UNIQUE NOT NULL COMMENT '手机号',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    status ENUM('启用','停用') DEFAULT '启用' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='用户表';

-- ============================================================
-- 2. schools - 学校表
-- ============================================================
CREATE TABLE schools (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL COMMENT '学校编码',
    full_name VARCHAR(200) NOT NULL COMMENT '学校全称',
    region VARCHAR(100) NOT NULL COMMENT '所属区域',
    address VARCHAR(255) COMMENT '详细地址',
    campus_manager_id INT COMMENT '校园经理ID',
    contact_person VARCHAR(50) NOT NULL COMMENT '校方联系人',
    contact_phone VARCHAR(20) NOT NULL COMMENT '校方联系电话',
    project_status ENUM('未启动','实施中','试运行','已验收','维保中') DEFAULT '未启动' COMMENT '项目状态',
    remark TEXT COMMENT '备注',
    is_key TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否重点学校',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (campus_manager_id) REFERENCES users(id) ON DELETE SET NULL
) COMMENT='学校表';

-- ============================================================
-- 3. device_systems - 设备系统字典表
-- ============================================================
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
) COMMENT='设备系统字典表';

-- ============================================================
-- 4. suppliers - 供应商表
-- ============================================================
CREATE TABLE suppliers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL COMMENT '供应商名称',
    contact_person VARCHAR(50) NOT NULL COMMENT '联系人',
    contact_phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    contact_email VARCHAR(100) COMMENT '联系邮箱',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='供应商表';

-- ============================================================
-- 5. templates - 模板表
-- ============================================================
CREATE TABLE templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '模板名称',
    type ENUM('到货验收表','加电测试表','校级验收单','培训确认表','培训签到表','培训反馈表','其他') NOT NULL COMMENT '模板类型',
    stage ENUM('到货验收','加电测试','校级验收','培训') NOT NULL COMMENT '关联阶段',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    version VARCHAR(20) NOT NULL COMMENT '版本号',
    description TEXT COMMENT '说明',
    status ENUM('启用','停用') DEFAULT '启用' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='模板表';

-- ============================================================
-- 6. dict_items - 数据字典表
-- ============================================================
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
) COMMENT='数据字典表';

-- ============================================================
-- 7. project_info - 项目信息表
-- ============================================================
CREATE TABLE project_info (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(100) NOT NULL COMMENT '项目名称',
    project_code VARCHAR(50) UNIQUE NOT NULL COMMENT '项目编码',
    start_date DATE NOT NULL COMMENT '项目开始日期',
    end_date DATE NOT NULL COMMENT '项目结束日期',
    overall_status ENUM('未启动','进行中','试运行','已验收','已结项') DEFAULT '未启动' COMMENT '项目整体状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='项目信息表';

-- ============================================================
-- 8. wbs_tasks - WBS任务表
-- ============================================================
CREATE TABLE wbs_tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_phase_l1 VARCHAR(50) NOT NULL COMMENT 'L1项目阶段',
    sub_phase_l2 VARCHAR(50) NOT NULL COMMENT 'L2子阶段',
    task_package_l3 VARCHAR(100) NOT NULL COMMENT 'L3工作任务包',
    work_content_l4 VARCHAR(200) NOT NULL COMMENT 'L4工作内容',
    work_detail_l5 VARCHAR(200) COMMENT 'L5工作明细',
    stage_type ENUM('到货验收','加电测试','校级验收','培训','无') COMMENT '关联阶段类型',
    plan_start_date DATE NOT NULL COMMENT '计划开始时间',
    plan_end_date DATE NOT NULL COMMENT '计划结束时间',
    status ENUM('待开始','进行中','已完成','已延期','待补材料') NOT NULL COMMENT '状态',
    actual_start_date DATE COMMENT '实际开始时间',
    actual_end_date DATE COMMENT '实际结束时间',
    responsible_person_id INT NOT NULL COMMENT '责任人',
    progress_note TEXT COMMENT '进展说明',
    deliverables VARCHAR(255) COMMENT '输出物',
    school_id INT NOT NULL COMMENT '关联学校',
    source_device_id INT COMMENT '来源设备记录ID',
    construction_year INT COMMENT '建设年份',
    is_orphan TINYINT DEFAULT 0 COMMENT '是否孤儿任务',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (responsible_person_id) REFERENCES users(id),
    FOREIGN KEY (school_id) REFERENCES schools(id)
) COMMENT='WBS任务表';

-- ============================================================
-- 9. devices - 设备信息表
-- ============================================================
CREATE TABLE devices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(100) NOT NULL COMMENT '项目名称',
    construction_year INT NOT NULL COMMENT '建设年份',
    system_id INT NOT NULL COMMENT '系统ID',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    brand VARCHAR(100) NOT NULL COMMENT '品牌',
    model VARCHAR(100) NOT NULL COMMENT '型号',
    params TEXT COMMENT '技术参数',
    type ENUM('硬件','软件','服务') NOT NULL COMMENT '设备类型',
    unit VARCHAR(20) NOT NULL COMMENT '单位',
    source ENUM('三方外采','库存设备') NOT NULL COMMENT '设备来源',
    quantity INT NOT NULL COMMENT '数量',
    school_id INT NOT NULL COMMENT '分配学校',
    install_location VARCHAR(100) COMMENT '安装位置',
    status ENUM('待发货','已发货','已到货','已安装','已调试','已验收') NOT NULL COMMENT '当前状态',
    supplier_id INT COMMENT '供应商(仅外部采购)',
    plan_arrival_date DATE NOT NULL COMMENT '到货计划时间',
    delivery_no VARCHAR(50) COMMENT '发货单号',
    delivery_date DATE COMMENT '发货日期',
    arrival_date DATE COMMENT '到货日期',
    install_date DATE COMMENT '安装完成日期',
    debug_date DATE COMMENT '调试完成日期',
    accept_date DATE COMMENT '验收日期',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES device_systems(id),
    FOREIGN KEY (school_id) REFERENCES schools(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
) COMMENT='设备信息表';

-- ============================================================
-- 10. trainings - 培训计划表
-- ============================================================
CREATE TABLE trainings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type ENUM('集中培训','现场培训','线上培训','区级培训') NOT NULL COMMENT '培训类型',
    content VARCHAR(200) NOT NULL COMMENT '培训内容',
    target_audience VARCHAR(100) NOT NULL COMMENT '参训对象',
    person_count INT NOT NULL COMMENT '预计人数',
    duration_days DECIMAL(3,1) NOT NULL COMMENT '培训天数',
    location VARCHAR(100) NOT NULL COMMENT '培训地点',
    method ENUM('理论讲授','实操演练','考核测评') NOT NULL COMMENT '培训方式',
    exam_method ENUM('笔试','实操','问卷','无') NOT NULL COMMENT '考核方式',
    plan_date DATE NOT NULL COMMENT '计划日期',
    actual_date DATE COMMENT '实际日期',
    status ENUM('待培训','培训中','已完成','已取消') NOT NULL COMMENT '培训状态',
    related_task_id INT COMMENT '关联WBS任务ID',
    is_district TINYINT DEFAULT 0 COMMENT '是否区级培训',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (related_task_id) REFERENCES wbs_tasks(id) ON DELETE SET NULL
) COMMENT='培训计划表';

-- ============================================================
-- 11. training_schools - 培训学校关联表
-- ============================================================
CREATE TABLE training_schools (
    id INT PRIMARY KEY AUTO_INCREMENT,
    training_id INT NOT NULL COMMENT '培训ID',
    school_id INT NOT NULL COMMENT '学校ID',
    FOREIGN KEY (training_id) REFERENCES trainings(id) ON DELETE CASCADE,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
) COMMENT='培训学校关联表';

-- ============================================================
-- 12. risks - 风险管理表
-- ============================================================
CREATE TABLE risks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    risk_desc TEXT NOT NULL COMMENT '风险描述',
    trigger_condition TEXT COMMENT '触发条件',
    impact_description TEXT COMMENT '影响描述',
    probability ENUM('高','中','低') NOT NULL COMMENT '概率',
    impact ENUM('高','中','低') NOT NULL COMMENT '影响',
    risk_level ENUM('高','中','低') COMMENT '风险等级(自动计算)',
    response_strategy TEXT COMMENT '应对措施',
    response_deadline DATE COMMENT '应对计划完成时间',
    responsible_person_id INT NOT NULL COMMENT '责任人',
    status ENUM('已识别','应对中','已关闭') NOT NULL COMMENT '状态',
    school_id INT COMMENT '关联学校',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (responsible_person_id) REFERENCES users(id),
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL
) COMMENT='风险管理表';

-- ============================================================
-- 13. risk_tasks - 风险应对任务关联表
-- ============================================================
CREATE TABLE risk_tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    risk_id INT NOT NULL COMMENT '风险ID',
    task_id INT NOT NULL COMMENT 'WBS任务ID',
    FOREIGN KEY (risk_id) REFERENCES risks(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES wbs_tasks(id) ON DELETE CASCADE
) COMMENT='风险应对任务关联表';

-- ============================================================
-- 14. reports - 报告管理表
-- ============================================================
CREATE TABLE reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    report_type ENUM('week','month') NOT NULL COMMENT '报告类型',
    report_scope ENUM('project','school') NOT NULL COMMENT '报告范围',
    school_id INT COMMENT '学校ID(scope=school时必填)',
    period_start DATE NOT NULL COMMENT '周期开始',
    period_end DATE NOT NULL COMMENT '周期结束',
    title VARCHAR(200) NOT NULL COMMENT '报告标题',
    content JSON NOT NULL COMMENT '内容快照',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
) COMMENT='报告管理表';

-- ============================================================
-- 15. files - 交付材料库表
-- ============================================================
CREATE TABLE files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    file_size INT COMMENT '文件大小(字节)',
    file_type VARCHAR(50) COMMENT '文件类型',
    source_module ENUM('project','training') NOT NULL COMMENT '来源模块',
    source_id INT NOT NULL COMMENT '来源记录ID',
    school_id INT COMMENT '关联学校',
    is_district TINYINT DEFAULT 0 COMMENT '是否区级培训材料',
    stage_type ENUM('到货验收','加电测试','校级验收','培训') COMMENT '阶段类型',
    upload_by INT NOT NULL COMMENT '上传人',
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_by) REFERENCES users(id),
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL
) COMMENT='交付材料库表';

-- ============================================================
-- 16. operation_logs - 操作日志表
-- ============================================================
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT='操作日志表';

-- ============================================================
-- 17. production_lines - 产线类型字典表
-- ============================================================
CREATE TABLE production_lines (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL COMMENT '产线编码',
    name VARCHAR(100) NOT NULL COMMENT '产线名称',
    description VARCHAR(500) COMMENT '描述',
    is_enabled TINYINT DEFAULT 1 COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='产线类型字典表';

-- ============================================================
-- 18. software_modules - 软件模块交付进度表
-- ============================================================
CREATE TABLE software_modules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '模块名称',
    phase ENUM('需求收集','需求确认','软件开发','软件测试','软件部署','上线运行') NOT NULL COMMENT '当前阶段',
    progress INT DEFAULT 0 COMMENT '完成进度(0-100)',
    expected_completion_date DATE COMMENT '预计完成时间',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='软件模块交付进度表';

-- ============================================================
-- 19. todos - 待办任务表
-- ============================================================
CREATE TABLE todos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL COMMENT '任务标题',
    description TEXT COMMENT '任务描述',
    priority ENUM('高','中','低') DEFAULT '中' COMMENT '优先级',
    due_date DATE COMMENT '截止日期',
    status ENUM('待处理','已完成') DEFAULT '待处理' COMMENT '状态',
    assignee_id INT COMMENT '负责人ID',
    creator_id INT COMMENT '创建人ID',
    source_type ENUM('project','wbs','system') DEFAULT 'project' COMMENT '来源类型',
    source_id INT COMMENT '来源记录ID',
    transferred_from INT COMMENT '转办来源人ID',
    parent_id INT COMMENT '父待办ID，支持多级树形结构，NULL为顶级',
    completed_at DATETIME COMMENT '完成时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_id) REFERENCES todos(id) ON DELETE CASCADE,
    INDEX idx_parent (parent_id)
) COMMENT='待办任务表';

-- ============================================================
-- 初始化数据
-- ============================================================

-- 1. 默认管理员账号（密码：Admin@2026）
INSERT INTO users (username, password_hash, real_name, role, phone, email, status) 
VALUES (
    'admin',
    '$2b$12$raNb1MQCp8eBVZwFIvM7wOh66yFySULvnRz4N5iSgh0xILGXRFb4u',
    '系统管理员',
    'admin',
    '13800000000',
    'admin@gx.com',
    '启用'
);

-- 2. 默认项目信息
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

-- 5. 数据字典 - WBS状态
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('WBS状态', '待开始', '待开始', 1),
('WBS状态', '进行中', '进行中', 2),
('WBS状态', '已完成', '已完成', 3),
('WBS状态', '已延期', '已延期', 4),
('WBS状态', '待补材料', '待补材料', 5);

-- 6. 数据字典 - L1阶段
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('L1阶段', '启动规划', '启动规划', 1),
('L1阶段', '交付实施', '交付实施', 2),
('L1阶段', '验收移交', '验收移交', 3),
('L1阶段', '运营维护', '运营维护', 4);

-- 7. 数据字典 - L2子阶段（启动规划）
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('L2子阶段_启动规划', '合同交底', '合同交底', 1),
('L2子阶段_启动规划', '团队组建', '团队组建', 2),
('L2子阶段_启动规划', '实施方案编制', '实施方案编制', 3);

-- 8. 数据字典 - L2子阶段（交付实施）
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('L2子阶段_交付实施', '硬件交付', '硬件交付', 1),
('L2子阶段_交付实施', '软件交付', '软件交付', 2),
('L2子阶段_交付实施', '应用培训', '应用培训', 3);

-- 9. 数据字典 - L2子阶段（验收移交）
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('L2子阶段_验收移交', '竣工资料提交', '竣工资料提交', 1),
('L2子阶段_验收移交', '业主验收会', '业主验收会', 2),
('L2子阶段_验收移交', '资产移交确认', '资产移交确认', 3);

-- 10. 数据字典 - L2子阶段（运营维护）
INSERT INTO dict_items (category, label, value, sort_order) VALUES
('L2子阶段_运营维护', '日常运维', '日常运维', 1),
('L2子阶段_运营维护', '定期巡检', '定期巡检', 2),
('L2子阶段_运营维护', '故障处理', '故障处理', 3);