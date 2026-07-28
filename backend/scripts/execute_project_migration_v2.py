# -*- coding: utf-8 -*-
"""执行 project_id 迁移 - 按步骤执行"""
import os
import sys

import pymysql
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    charset='utf8mb4',
)

print('开始执行迁移...\n')

steps = [
    # 步骤1: schools
    ("步骤1.1", "ALTER TABLE schools ADD COLUMN project_id INT NOT NULL DEFAULT 1 COMMENT '所属项目' AFTER id"),
    ("步骤1.2", "ALTER TABLE schools ADD FOREIGN KEY (project_id) REFERENCES project_info(id)"),
    ("步骤1.3", "ALTER TABLE schools ADD INDEX idx_project (project_id)"),

    # 步骤2: dict_items
    ("步骤2.1", "ALTER TABLE dict_items ADD COLUMN project_id INT DEFAULT 1 COMMENT '所属项目（NULL=全局共享）' AFTER id"),
    ("步骤2.2", "ALTER TABLE dict_items ADD FOREIGN KEY (project_id) REFERENCES project_info(id)"),
    ("步骤2.3", "ALTER TABLE dict_items ADD INDEX idx_project_category (project_id, category)"),

    # 步骤3: wbs_tasks
    ("步骤3.1", "ALTER TABLE wbs_tasks ADD COLUMN project_id INT NOT NULL DEFAULT 1 COMMENT '所属项目' AFTER id"),
    ("步骤3.2", "ALTER TABLE wbs_tasks ADD COLUMN requires_material TINYINT DEFAULT 0 COMMENT '是否需要上传材料' AFTER is_orphan"),
    ("步骤3.3", "ALTER TABLE wbs_tasks ADD COLUMN material_status ENUM('无要求','待上传','部分上传','已完成') DEFAULT '无要求' COMMENT '材料状态' AFTER requires_material"),
    ("步骤3.4", "ALTER TABLE wbs_tasks ADD FOREIGN KEY (project_id) REFERENCES project_info(id)"),
    ("步骤3.5", "ALTER TABLE wbs_tasks ADD INDEX idx_project_school (project_id, school_id)"),
    ("步骤3.6", "ALTER TABLE wbs_tasks ADD INDEX idx_material_status (material_status)"),

    # 步骤4: devices
    ("步骤4.1", "ALTER TABLE devices ADD COLUMN project_id INT NOT NULL DEFAULT 1 COMMENT '所属项目' AFTER id"),
    ("步骤4.2", "ALTER TABLE devices ADD FOREIGN KEY (project_id) REFERENCES project_info(id)"),
    ("步骤4.3", "ALTER TABLE devices ADD INDEX idx_project_school (project_id, school_id)"),

    # 步骤5: trainings
    ("步骤5.1", "ALTER TABLE trainings ADD COLUMN project_id INT NOT NULL DEFAULT 1 COMMENT '所属项目' AFTER id"),
    ("步骤5.2", "ALTER TABLE trainings ADD FOREIGN KEY (project_id) REFERENCES project_info(id)"),
    ("步骤5.3", "ALTER TABLE trainings ADD INDEX idx_project (project_id)"),

    # 步骤6: risks
    ("步骤6.1", "ALTER TABLE risks ADD COLUMN project_id INT NOT NULL DEFAULT 1 COMMENT '所属项目' AFTER id"),
    ("步骤6.2", "ALTER TABLE risks ADD FOREIGN KEY (project_id) REFERENCES project_info(id)"),
    ("步骤6.3", "ALTER TABLE risks ADD INDEX idx_project_school (project_id, school_id)"),

    # 步骤7: reports
    ("步骤7.1", "ALTER TABLE reports ADD COLUMN project_id INT NOT NULL DEFAULT 1 COMMENT '所属项目' AFTER id"),
    ("步骤7.2", "ALTER TABLE reports ADD FOREIGN KEY (project_id) REFERENCES project_info(id)"),
    ("步骤7.3", "ALTER TABLE reports ADD INDEX idx_project_type (project_id, report_type)"),

    # 步骤8: files
    ("步骤8.1", "ALTER TABLE files ADD COLUMN project_id INT NOT NULL DEFAULT 1 COMMENT '所属项目' AFTER id"),
    ("步骤8.2", "ALTER TABLE files ADD COLUMN wbs_task_id INT COMMENT '关联WBS任务ID' AFTER source_id"),
    ("步骤8.3", "ALTER TABLE files ADD COLUMN template_id INT COMMENT '使用的模板ID' AFTER wbs_task_id"),
    ("步骤8.4", "ALTER TABLE files ADD FOREIGN KEY (project_id) REFERENCES project_info(id)"),
    ("步骤8.5", "ALTER TABLE files ADD INDEX idx_project_module (project_id, source_module)"),
    ("步骤8.6", "ALTER TABLE files ADD INDEX idx_wbs_task (wbs_task_id)"),

    # 步骤9: operation_logs
    ("步骤9.1", "ALTER TABLE operation_logs ADD COLUMN project_id INT COMMENT '所属项目（NULL=跨项目操作）' AFTER id"),
    ("步骤9.2", "ALTER TABLE operation_logs ADD FOREIGN KEY (project_id) REFERENCES project_info(id) ON DELETE SET NULL"),
    ("步骤9.3", "ALTER TABLE operation_logs ADD INDEX idx_project_module (project_id, module)"),

    # 步骤10: templates 重建
    ("步骤10.1", "RENAME TABLE templates TO templates_old_20260728"),
    ("步骤10.2", """CREATE TABLE templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL COMMENT '所属项目',
    template_key VARCHAR(50) NOT NULL COMMENT '模板分组键',
    name VARCHAR(100) NOT NULL COMMENT '模板名称',
    type VARCHAR(50) NOT NULL COMMENT '模板类型',
    file_path VARCHAR(500) NOT NULL COMMENT '服务器存储路径',
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_size INT COMMENT '文件大小',
    file_type VARCHAR(50) COMMENT '文件类型',
    version VARCHAR(20) NOT NULL COMMENT '版本号',
    description TEXT COMMENT '说明',
    status ENUM('启用','停用') DEFAULT '启用' COMMENT '状态',
    is_latest TINYINT DEFAULT 1 COMMENT '是否最新版',
    is_deleted TINYINT DEFAULT 0 COMMENT '软删除标记',
    upload_by INT NOT NULL COMMENT '上传人',
    download_count INT DEFAULT 0 COMMENT '下载次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project_info(id),
    FOREIGN KEY (upload_by) REFERENCES users(id),
    INDEX idx_project_type (project_id, type),
    INDEX idx_project_status (project_id, status, is_latest),
    INDEX idx_template_key (template_key, is_latest)
) COMMENT='模板表' DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""),

    # 步骤11: template_wbs_stages
    ("步骤11", """CREATE TABLE template_wbs_stages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_id INT NOT NULL COMMENT '模板ID',
    level ENUM('L1','L2','L3') NOT NULL COMMENT '关联层级',
    stage_value VARCHAR(100) NOT NULL COMMENT '阶段值',
    is_required TINYINT DEFAULT 1 COMMENT '是否强制上传',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE,
    UNIQUE KEY uk_template_level_stage (template_id, level, stage_value)
) COMMENT='模板-WBS阶段关联表' DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""),

    # 步骤12: 数据字典
    ("步骤12", """INSERT INTO dict_items (project_id, category, label, value, sort_order) VALUES
(1, '模板类型', '到货验收表', '到货验收表', 1),
(1, '模板类型', '加电测试表', '加电测试表', 2),
(1, '模板类型', '校级验收单', '校级验收单', 3),
(1, '模板类型', '培训确认表', '培训确认表', 4),
(1, '模板类型', '培训签到表', '培训签到表', 5),
(1, '模板类型', '培训反馈表', '培训反馈表', 6),
(1, '模板类型', '其他交付材料', '其他交付材料', 7),
(1, '模板类型', '项目周报', '项目周报', 11),
(1, '模板类型', '项目月报', '项目月报', 12),
(1, '模板类型', '校级周报', '校级周报', 13),
(1, '模板类型', '校级月报', '校级月报', 14),
(1, '模板类型', '专项汇报', '专项汇报', 15)"""),
]

try:
    with conn.cursor() as cur:
        for i, (label, sql) in enumerate(steps, 1):
            print(f'[{i}/{len(steps)}] {label}')
            print(f'  SQL: {sql[:100]}...' if len(sql) > 100 else f'  SQL: {sql}')

            try:
                cur.execute(sql)
                conn.commit()
                print(f'  ✅ 成功\n')
            except Exception as e:
                print(f'  ❌ 失败: {e}\n')
                raise

    print('✅ 迁移完成！')

except Exception as e:
    print(f'\n❌ 迁移失败: {e}')
    conn.rollback()
    sys.exit(1)

finally:
    conn.close()
