"""
产线-系统关系迁移脚本
1. 备份 production_lines 现有数据
2. 新建 systems 表
3. production_lines: 3条demo -> 9条真实产品线
4. systems: 写入21个系统, 关联产品线
5. devices: 新增 system_id 列并回填

注意: AI算力中心/智能交互终端 不建字典行(用户确认方案A),
      其412条设备保留 system_name, system_id 留空待后续维护
"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text

PROJECT_ID = 1

# 产品线定义: (code, name, description)
PRODUCTION_LINES = [
    ('PL-CLASSROOM',  '大课堂',              '智慧课堂类产品'),
    ('PL-DAXUEQING',  '大学情',              '学情分析类产品'),
    ('PL-PLATFORM',   '平台产品线',          '基础平台与应用能力'),
    ('PL-STEAM',      '科创教育',            '科创实验室类产品'),
    ('PL-EXAM-LANG',  '考试与语言学习产品线', 'AI听说与语言学习'),
    ('PL-SPORT',      '智慧体育产品线',      '智慧体育类产品'),
    ('PL-MENTAL',     '智慧心育产品线',      '心理健康教育'),
    ('PL-SCIPOP',     '科普研究院',          '科普类产品'),
    ('PL-READING',    '读写科技',            '阅读类产品'),
]

# 系统定义: (系统名称, 所属产线code)
SYSTEMS = [
    ('智慧课堂',              'PL-CLASSROOM'),
    ('AI教师助手',            'PL-CLASSROOM'),
    ('智慧黑板',              'PL-CLASSROOM'),
    ('大数据精准教学分析系统', 'PL-DAXUEQING'),
    ('智能批阅服务',          'PL-DAXUEQING'),
    ('数智工作台',            'PL-PLATFORM'),
    ('教育数据指挥中心',      'PL-PLATFORM'),
    ('智能应用创编平台',      'PL-PLATFORM'),
    ('应用能力服务',          'PL-PLATFORM'),
    ('学生评价系统',          'PL-PLATFORM'),
    ('人工智能实验室',        'PL-STEAM'),
    ('信息科技',              'PL-STEAM'),
    ('AI科学实验室',          'PL-STEAM'),
    ('AI听说模拟测试',        'PL-EXAM-LANG'),
    ('AI英语听说教学',        'PL-EXAM-LANG'),
    ('智慧操场',              'PL-SPORT'),
    ('运动小站',              'PL-SPORT'),
    ('智慧体育课',            'PL-SPORT'),
    ('智慧心育',              'PL-MENTAL'),
    ('智慧科技长廊',          'PL-SCIPOP'),
    ('数字阅览室',            'PL-READING'),
]

DDL_SYSTEMS = """
CREATE TABLE systems (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL DEFAULT 1 COMMENT '所属项目',
    name VARCHAR(100) NOT NULL COMMENT '系统名称',
    production_line_id INT COMMENT '所属产线',
    description VARCHAR(500) COMMENT '描述',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_enabled TINYINT DEFAULT 1 COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project_info(id),
    FOREIGN KEY (production_line_id) REFERENCES production_lines(id) ON DELETE SET NULL,
    UNIQUE KEY uq_systems_project_name (project_id, name),
    INDEX idx_project (project_id),
    INDEX idx_production_line (production_line_id)
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统字典表'
"""


def main():
    with engine.begin() as c:
        # ---------- 步骤1: 备份 production_lines ----------
        old = [dict(r._mapping) for r in c.execute(text(
            'SELECT id,project_id,code,name,description,is_enabled FROM production_lines'))]
        bak = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'backup_production_lines.json')
        with open(bak, 'w', encoding='utf-8') as f:
            json.dump(old, f, ensure_ascii=False, indent=2)
        print(f'[1/5] 已备份 production_lines {len(old)} 条 -> {bak}')

        # ---------- 步骤2: 建 systems 表 ----------
        exists = list(c.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_name='systems' AND table_schema=DATABASE()")))[0][0]
        if exists:
            print('[2/5] systems 表已存在, 跳过建表')
        else:
            c.execute(text(DDL_SYSTEMS))
            print('[2/5] systems 表创建成功')

        # ---------- 步骤3: 替换 production_lines ----------
        c.execute(text('DELETE FROM production_lines'))
        for i, (code, name, desc) in enumerate(PRODUCTION_LINES):
            c.execute(text(
                'INSERT INTO production_lines (project_id,code,name,description,is_enabled) '
                'VALUES (:p,:c,:n,:d,1)'),
                {'p': PROJECT_ID, 'c': code, 'n': name, 'd': desc})
        print(f'[3/5] production_lines: {len(old)} 条demo -> {len(PRODUCTION_LINES)} 条真实产品线')

        # ---------- 步骤4: 写入 systems ----------
        pl_map = {r[0]: r[1] for r in c.execute(text(
            'SELECT code,id FROM production_lines'))}
        c.execute(text('DELETE FROM systems'))
        for i, (sname, plcode) in enumerate(SYSTEMS):
            c.execute(text(
                'INSERT INTO systems (project_id,name,production_line_id,sort_order,is_enabled) '
                'VALUES (:p,:n,:pl,:s,1)'),
                {'p': PROJECT_ID, 'n': sname, 'pl': pl_map[plcode], 's': i})
        print(f'[4/5] systems: 写入 {len(SYSTEMS)} 个系统')

        # ---------- 步骤5: devices.system_id ----------
        has_col = len(list(c.execute(text("SHOW COLUMNS FROM devices LIKE 'system_id'")))) > 0
        if has_col:
            print('[5/5] devices.system_id 已存在, 仅重新回填')
        else:
            c.execute(text(
                'ALTER TABLE devices ADD COLUMN system_id INT NULL '
                "COMMENT '所属系统' AFTER system_name"))
            c.execute(text(
                'ALTER TABLE devices ADD CONSTRAINT fk_devices_system '
                'FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE SET NULL'))
            c.execute(text('ALTER TABLE devices ADD INDEX idx_system (system_id)'))
            print('[5/5] devices.system_id 列+外键+索引 添加成功')

        filled = c.execute(text(
            'UPDATE devices d JOIN systems s '
            'ON d.system_name = s.name AND d.project_id = s.project_id '
            'SET d.system_id = s.id')).rowcount
        print(f'      回填 system_id: {filled} 条')

        orphan = list(c.execute(text(
            'SELECT system_name, COUNT(*) FROM devices WHERE system_id IS NULL '
            'GROUP BY system_name')))
        print('      未回填(system_id为NULL)的设备:')
        for r in orphan:
            print(f'        {r[0]} -> {r[1]} 条')


if __name__ == '__main__':
    main()
