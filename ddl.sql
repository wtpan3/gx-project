-- ============================================================
-- GX教育项目交付管理系统 - 数据库结构定义
-- 生成时间: 2026-07-28
-- 数据库: gx_project_dev
-- 字符集: utf8mb4
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. users - 用户表
-- ============================================================
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '登录账号',
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码哈希(bcrypt)',
  `real_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '真实姓名',
  `role` enum('admin','project_manager','campus_manager') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '手机号',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '邮箱',
  `status` enum('启用','停用') COLLATE utf8mb4_unicode_ci DEFAULT '启用' COMMENT '状态',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================================
-- 2. project_info - 项目信息表
-- ============================================================
CREATE TABLE `project_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '项目名称',
  `project_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '项目编码',
  `start_date` date NOT NULL COMMENT '项目开始日期',
  `end_date` date NOT NULL COMMENT '项目结束日期',
  `overall_status` enum('未启动','进行中','试运行','已验收','已结项') COLLATE utf8mb4_unicode_ci DEFAULT '未启动' COMMENT '项目整体状态',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_code` (`project_code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目信息表';

-- ============================================================
-- 3. schools - 学校表
-- ============================================================
CREATE TABLE `schools` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL DEFAULT '1' COMMENT '所属项目',
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学校编码',
  `full_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学校全称',
  `region` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '所属区域',
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '详细地址',
  `campus_manager_id` int DEFAULT NULL COMMENT '校园经理ID',
  `contact_person` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '校方联系人',
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '校方联系电话',
  `project_status` enum('未启动','实施中','试运行','已验收','维保中') COLLATE utf8mb4_unicode_ci DEFAULT '未启动' COMMENT '项目状态',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `is_key` tinyint DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `campus_manager_id` (`campus_manager_id`),
  KEY `idx_project` (`project_id`),
  CONSTRAINT `schools_ibfk_1` FOREIGN KEY (`campus_manager_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `schools_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学校表';

-- ============================================================
-- 4. suppliers - 供应商表
-- ============================================================
CREATE TABLE `suppliers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '供应商名称',
  `contact_person` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '联系人',
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '联系电话',
  `contact_email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系邮箱',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='供应商表';

-- ============================================================
-- 5. templates - 模板表
-- ============================================================
CREATE TABLE `templates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL COMMENT '所属项目',
  `template_key` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模板分组键',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模板名称',
  `type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模板类型',
  `file_path` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '服务器存储路径',
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '原始文件名',
  `file_size` int DEFAULT NULL COMMENT '文件大小',
  `file_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '文件类型',
  `version` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '版本号',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '说明',
  `status` enum('启用','停用') COLLATE utf8mb4_unicode_ci DEFAULT '启用' COMMENT '状态',
  `is_latest` tinyint DEFAULT '1' COMMENT '是否最新版',
  `is_deleted` tinyint DEFAULT '0' COMMENT '软删除标记',
  `upload_by` int NOT NULL COMMENT '上传人',
  `download_count` int DEFAULT '0' COMMENT '下载次数',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `upload_by` (`upload_by`),
  KEY `idx_project_type` (`project_id`,`type`),
  KEY `idx_project_status` (`project_id`,`status`,`is_latest`),
  KEY `idx_template_key` (`template_key`,`is_latest`),
  CONSTRAINT `templates_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`),
  CONSTRAINT `templates_ibfk_2` FOREIGN KEY (`upload_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模板表';

-- ============================================================
-- 6. template_wbs_stages - 模板-WBS阶段关联表
-- ============================================================
CREATE TABLE `template_wbs_stages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `template_id` int NOT NULL COMMENT '模板ID',
  `level` enum('L1','L2','L3') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联层级',
  `stage_value` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '阶段值',
  `is_required` tinyint DEFAULT '1' COMMENT '是否强制上传',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_template_level_stage` (`template_id`,`level`,`stage_value`),
  CONSTRAINT `template_wbs_stages_ibfk_1` FOREIGN KEY (`template_id`) REFERENCES `templates` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模板-WBS阶段关联表';

-- ============================================================
-- 7. dict_items - 数据字典表
-- ============================================================
CREATE TABLE `dict_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int DEFAULT '1' COMMENT '所属项目（NULL=全局共享）',
  `category` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '字典分类',
  `label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '显示名称',
  `value` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '值',
  `sort_order` int DEFAULT '0' COMMENT '排序',
  `is_enabled` tinyint DEFAULT '1' COMMENT '是否启用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_category_value` (`category`,`value`),
  KEY `idx_project_category` (`project_id`,`category`),
  CONSTRAINT `dict_items_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据字典表';

-- ============================================================
-- 8. wbs_tasks - WBS任务表
-- ============================================================
CREATE TABLE `wbs_tasks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL DEFAULT '1' COMMENT '所属项目',
  `task_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `project_phase_l1` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'L1项目阶段',
  `sub_phase_l2` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'L2子阶段',
  `task_package_l3` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'L3工作任务包',
  `work_content_l4` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'L4工作内容',
  `work_detail_l5` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'L5工作明细',
  `priority` enum('高','中','低') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '中',
  `stage_type` enum('到货验收','加电测试','校级验收','培训','无') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '关联阶段类型',
  `plan_start_date` date NOT NULL COMMENT '计划开始时间',
  `plan_end_date` date NOT NULL COMMENT '计划结束时间',
  `status` enum('待开始','进行中','已完成','已延期','待补材料') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '待开始',
  `actual_start_date` date DEFAULT NULL COMMENT '实际开始时间',
  `actual_end_date` date DEFAULT NULL COMMENT '实际结束时间',
  `responsible_person_id` int DEFAULT NULL,
  `progress_note` text COLLATE utf8mb4_unicode_ci COMMENT '进展说明',
  `deliverables` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '输出物',
  `school_id` int DEFAULT NULL,
  `source_device_id` int DEFAULT NULL COMMENT '来源设备记录ID',
  `construction_year` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_orphan` tinyint DEFAULT '0' COMMENT '是否孤儿任务',
  `requires_material` tinyint DEFAULT '0' COMMENT '是否需要上传材料',
  `material_status` enum('无要求','待上传','部分上传','已完成') COLLATE utf8mb4_unicode_ci DEFAULT '无要求' COMMENT '材料状态',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `parent_id` int DEFAULT NULL,
  `progress` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_task_code` (`task_code`),
  KEY `assignee_id` (`responsible_person_id`),
  KEY `school_id` (`school_id`),
  KEY `fk_wbs_parent` (`parent_id`),
  KEY `idx_project_school` (`project_id`,`school_id`),
  KEY `idx_material_status` (`material_status`),
  CONSTRAINT `fk_wbs_parent` FOREIGN KEY (`parent_id`) REFERENCES `wbs_tasks` (`id`),
  CONSTRAINT `wbs_tasks_ibfk_1` FOREIGN KEY (`responsible_person_id`) REFERENCES `users` (`id`),
  CONSTRAINT `wbs_tasks_ibfk_2` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `wbs_tasks_ibfk_3` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=195 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='WBS任务表';

-- ============================================================
-- 9. devices - 设备信息表
-- ============================================================
CREATE TABLE `devices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL DEFAULT '1' COMMENT '所属项目',
  `project_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '项目名称',
  `construction_year` int NOT NULL COMMENT '建设年份',
  `system_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '系统名称',
  `device_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '设备名称',
  `brand` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '品牌',
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '型号',
  `params` text COLLATE utf8mb4_unicode_ci COMMENT '技术参数',
  `type` enum('硬件','软件','服务') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '设备类型',
  `unit` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '单位',
  `source` enum('三方外采','库存设备') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `quantity` int NOT NULL COMMENT '数量',
  `school_id` int NOT NULL COMMENT '分配学校',
  `install_location` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '安装位置',
  `status` enum('待发货','已到货','已安装','已调试','运行中') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `supplier_id` int DEFAULT NULL COMMENT '供应商(仅外部采购)',
  `plan_arrival_date` date NOT NULL COMMENT '到货计划时间',
  `delivery_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '发货单号',
  `delivery_date` date DEFAULT NULL COMMENT '发货日期',
  `arrival_date` date DEFAULT NULL COMMENT '到货日期',
  `install_date` date DEFAULT NULL COMMENT '安装完成日期',
  `debug_date` date DEFAULT NULL COMMENT '调试完成日期',
  `accept_date` date DEFAULT NULL COMMENT '验收日期',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `school_id` (`school_id`),
  KEY `supplier_id` (`supplier_id`),
  KEY `idx_project_school` (`project_id`,`school_id`),
  CONSTRAINT `devices_ibfk_2` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`),
  CONSTRAINT `devices_ibfk_3` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `devices_ibfk_4` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1241 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备信息表';

-- ============================================================
-- 10. trainings - 培训计划表
-- ============================================================
CREATE TABLE `trainings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL DEFAULT '1' COMMENT '所属项目',
  `type` enum('集中培训','现场培训','线上培训','区级培训') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '培训类型',
  `content` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '培训内容',
  `target_audience` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '参训对象',
  `person_count` int NOT NULL COMMENT '预计人数',
  `duration_days` decimal(3,1) NOT NULL COMMENT '培训天数',
  `location` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '培训地点',
  `method` enum('理论讲授','实操演练','考核测评') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '培训方式',
  `exam_method` enum('笔试','实操','问卷','无') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '考核方式',
  `plan_date` date NOT NULL COMMENT '计划日期',
  `actual_date` date DEFAULT NULL COMMENT '实际日期',
  `status` enum('待培训','培训中','已完成','已取消') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '培训状态',
  `related_task_id` int DEFAULT NULL COMMENT '关联WBS任务ID',
  `is_district` tinyint DEFAULT '0' COMMENT '是否区级培训',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `related_task_id` (`related_task_id`),
  KEY `idx_project` (`project_id`),
  CONSTRAINT `trainings_ibfk_1` FOREIGN KEY (`related_task_id`) REFERENCES `wbs_tasks` (`id`) ON DELETE SET NULL,
  CONSTRAINT `trainings_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='培训计划表';

-- ============================================================
-- 11. training_schools - 培训学校关联表
-- ============================================================
CREATE TABLE `training_schools` (
  `id` int NOT NULL AUTO_INCREMENT,
  `training_id` int NOT NULL COMMENT '培训ID',
  `school_id` int NOT NULL COMMENT '学校ID',
  PRIMARY KEY (`id`),
  KEY `training_id` (`training_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `training_schools_ibfk_1` FOREIGN KEY (`training_id`) REFERENCES `trainings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `training_schools_ibfk_2` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='培训学校关联表';

-- ============================================================
-- 12. risks - 风险管理表
-- ============================================================
CREATE TABLE `risks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL DEFAULT '1' COMMENT '所属项目',
  `risk_desc` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '风险描述',
  `trigger_condition` text COLLATE utf8mb4_unicode_ci COMMENT '触发条件',
  `impact_description` text COLLATE utf8mb4_unicode_ci COMMENT '影响描述',
  `risk_level` enum('高','中','低') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '风险等级(自动计算)',
  `response_strategy` text COLLATE utf8mb4_unicode_ci COMMENT '应对措施',
  `progress_note` text COLLATE utf8mb4_unicode_ci COMMENT '进展说明（自由文本）',
  `responsible_person_id` int NOT NULL COMMENT '责任人',
  `status` enum('已识别','应对中','已关闭') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `school_id` int DEFAULT NULL COMMENT '关联学校',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `responsible_person_id` (`responsible_person_id`),
  KEY `school_id` (`school_id`),
  KEY `idx_project_school` (`project_id`,`school_id`),
  CONSTRAINT `risks_ibfk_1` FOREIGN KEY (`responsible_person_id`) REFERENCES `users` (`id`),
  CONSTRAINT `risks_ibfk_2` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`) ON DELETE SET NULL,
  CONSTRAINT `risks_ibfk_3` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风险管理表';

-- ============================================================
-- 13. risk_tasks - 风险应对任务关联表
-- ============================================================
CREATE TABLE `risk_tasks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `risk_id` int NOT NULL COMMENT '风险ID',
  `task_id` int NOT NULL COMMENT 'WBS任务ID',
  PRIMARY KEY (`id`),
  KEY `risk_id` (`risk_id`),
  KEY `task_id` (`task_id`),
  CONSTRAINT `risk_tasks_ibfk_1` FOREIGN KEY (`risk_id`) REFERENCES `risks` (`id`) ON DELETE CASCADE,
  CONSTRAINT `risk_tasks_ibfk_2` FOREIGN KEY (`task_id`) REFERENCES `wbs_tasks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风险应对任务关联表';

-- ============================================================
-- 14. reports - 报告管理表
-- ============================================================
CREATE TABLE `reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL DEFAULT '1' COMMENT '所属项目',
  `report_type` enum('week','month') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '报告类型',
  `report_scope` enum('project','school') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '报告范围',
  `school_id` int DEFAULT NULL COMMENT '学校ID(scope=school时必填)',
  `period_start` date NOT NULL COMMENT '周期开始',
  `period_end` date NOT NULL COMMENT '周期结束',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '报告标题',
  `content` json NOT NULL COMMENT '内容快照',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `school_id` (`school_id`),
  KEY `idx_project_type` (`project_id`,`report_type`),
  CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reports_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报告管理表';

-- ============================================================
-- 15. files - 交付材料库表
-- ============================================================
CREATE TABLE `files` (
  `id` int NOT NULL AUTO_INCREMENT,
  `project_id` int NOT NULL DEFAULT '1' COMMENT '所属项目',
  `file_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件名',
  `file_path` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件路径',
  `file_size` int DEFAULT NULL COMMENT '文件大小(字节)',
  `file_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '文件类型',
  `source_module` enum('project','training') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '来源模块',
  `source_id` int NOT NULL COMMENT '来源记录ID',
  `wbs_task_id` int DEFAULT NULL COMMENT '关联WBS任务ID',
  `template_id` int DEFAULT NULL COMMENT '使用的模板ID',
  `school_id` int DEFAULT NULL COMMENT '关联学校',
  `is_district` tinyint DEFAULT '0' COMMENT '是否区级培训材料',
  `stage_type` enum('到货验收','加电测试','校级验收','培训') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '阶段类型',
  `upload_by` int NOT NULL COMMENT '上传人',
  `upload_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `upload_by` (`upload_by`),
  KEY `school_id` (`school_id`),
  KEY `idx_project_module` (`project_id`,`source_module`),
  KEY `idx_wbs_task` (`wbs_task_id`),
  CONSTRAINT `files_ibfk_1` FOREIGN KEY (`upload_by`) REFERENCES `users` (`id`),
  CONSTRAINT `files_ibfk_2` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`) ON DELETE SET NULL,
  CONSTRAINT `files_ibfk_3` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='交付材料库表';

-- ============================================================
-- 16. operation_logs - 操作日志表
-- ============================================================
CREATE TABLE `operation_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_id` int DEFAULT NULL COMMENT '所属项目（NULL=跨项目操作）',
  `user_id` int NOT NULL COMMENT '操作人ID',
  `module` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '所属模块',
  `action` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '操作类型',
  `target_id` int DEFAULT NULL COMMENT '操作目标ID',
  `before_data` json DEFAULT NULL COMMENT '变更前数据',
  `after_data` json DEFAULT NULL COMMENT '变更后数据',
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'IP地址',
  `batch_file_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '批量导入文件名',
  `batch_success_count` int DEFAULT NULL COMMENT '批量成功数',
  `batch_fail_count` int DEFAULT NULL COMMENT '批量失败数',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_project_module` (`project_id`,`module`),
  CONSTRAINT `operation_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `operation_logs_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- ============================================================
-- 17. production_lines - 产线类型字典表
-- ============================================================
CREATE TABLE `production_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '产线名称',
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '产线描述',
  `is_enabled` tinyint DEFAULT '1' COMMENT '是否启用(0否1是)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  UNIQUE KEY `code_2` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产线类型字典表';

-- ============================================================
-- 18. software_modules - 软件模块交付进度表
-- ============================================================
CREATE TABLE `software_modules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模块名称',
  `phase` enum('需求收集','需求确认','软件开发','软件测试','软件部署','上线运行') COLLATE utf8mb4_unicode_ci NOT NULL,
  `progress` int DEFAULT '0' COMMENT '完成进度(0-100)',
  `expected_completion_date` date DEFAULT NULL,
  `sort_order` int DEFAULT '0' COMMENT '排序值',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='软件模块交付进度表';

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 初始化数据
-- ============================================================

-- 1. 默认管理员账号（密码：Admin@2026）
INSERT INTO users (id, username, password_hash, real_name, role, phone, email, status, created_at, updated_at) VALUES
(1, 'admin', '$2b$12$raNb1MQCp8eBVZwFIvM7wOh66yFySULvnRz4N5iSgh0xILGXRFb4u', '系统管理员', 'admin', '13800000000', 'admin@gx.com', '启用', '2026-07-17 14:09:19', '2026-07-17 14:09:19');

-- 2. 默认项目信息
INSERT INTO project_info (id, project_name, project_code, start_date, end_date, overall_status, created_at, updated_at) VALUES
(1, 'GXAI+教育项目', 'GX2026', '2026-01-01', '2026-12-31', '进行中', '2026-07-17 14:09:20', '2026-07-17 14:09:20');

-- 3. 数据字典 - 关联阶段
INSERT INTO dict_items (id, project_id, category, label, value, sort_order, is_enabled, created_at, updated_at) VALUES
(1, 1, '关联阶段', '到货验收', '到货验收', 1, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(2, 1, '关联阶段', '加电测试', '加电测试', 2, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(3, 1, '关联阶段', '校级验收', '校级验收', 3, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(4, 1, '关联阶段', '培训', '培训', 4, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(5, 1, '关联阶段', '无', '无', 5, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20');

-- 4. 数据字典 - 建设年份
INSERT INTO dict_items (id, project_id, category, label, value, sort_order, is_enabled, created_at, updated_at) VALUES
(6, 1, '建设年份', '2026', '2026', 1, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(7, 1, '建设年份', '2027', '2027', 2, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(8, 1, '建设年份', '2028', '2028', 3, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20');

-- 5. 数据字典 - WBS状态
INSERT INTO dict_items (id, project_id, category, label, value, sort_order, is_enabled, created_at, updated_at) VALUES
(9, 1, 'WBS状态', '待开始', '待开始', 1, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(10, 1, 'WBS状态', '进行中', '进行中', 2, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(11, 1, 'WBS状态', '已完成', '已完成', 3, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(12, 1, 'WBS状态', '已延期', '已延期', 4, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(13, 1, 'WBS状态', '待补材料', '待补材料', 5, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20');

-- 6. 数据字典 - L1阶段
INSERT INTO dict_items (id, project_id, category, label, value, sort_order, is_enabled, created_at, updated_at) VALUES
(14, 1, 'L1阶段', '启动规划', '启动规划', 1, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(15, 1, 'L1阶段', '交付实施', '交付实施', 2, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(16, 1, 'L1阶段', '验收移交', '验收移交', 3, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20'),
(17, 1, 'L1阶段', '运营维护', '运营维护', 4, 1, '2026-07-17 14:09:20', '2026-07-17 14:09:20');

-- 7. 数据字典 - 模板类型
INSERT INTO dict_items (id, project_id, category, label, value, sort_order, is_enabled, created_at, updated_at) VALUES
(30, 1, '模板类型', '到货验收表', '到货验收表', 1, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(31, 1, '模板类型', '加电测试表', '加电测试表', 2, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(32, 1, '模板类型', '校级验收单', '校级验收单', 3, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(33, 1, '模板类型', '培训确认表', '培训确认表', 4, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(34, 1, '模板类型', '培训签到表', '培训签到表', 5, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(35, 1, '模板类型', '培训反馈表', '培训反馈表', 6, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(36, 1, '模板类型', '其他交付材料', '其他交付材料', 7, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(37, 1, '模板类型', '项目周报', '项目周报', 11, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(38, 1, '模板类型', '项目月报', '项目月报', 12, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(39, 1, '模板类型', '校级周报', '校级周报', 13, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(40, 1, '模板类型', '校级月报', '校级月报', 14, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26'),
(41, 1, '模板类型', '专项汇报', '专项汇报', 15, 1, '2026-07-28 13:20:26', '2026-07-28 13:20:26');

-- 8. 数据字典 - L2阶段-启动规划
-- 9. 数据字典 - L2阶段-交付实施
-- 10. 数据字典 - L2阶段-验收移交
-- 11. 数据字典 - L2阶段-运营维护
