# Schema一致性检查脚本使用说明

## 📌 目的

**防止数据库schema与SQLAlchemy models定义不一致**，自动检测ddl.sql与models.py之间的差异。

## 🎯 解决的问题

历史问题（来自问题登记簿）：
- P004: devices.type ENUM值不一致（ddl.sql写"服务"，models写"其他"）
- P005: devices.status ENUM值不一致（ddl.sql和models.py独立演化）
- P006: Device模型字段名不匹配（models写installation_date，库是install_date）
- P020: ALTER表语句与权威迁移脚本不一致

**根本原因**：ddl.sql和models.py分开维护，手工同步容易遗漏。

## 🚀 使用方法

### 基本用法

```bash
cd backend

# 检查默认数据库（gx_project_dev）
python scripts/check_schema.py

# 检查指定数据库
python scripts/check_schema.py --db gx_project

# 检查生产库
python scripts/check_schema.py --db gx_project_prod
```

### 集成到开发流程

#### 1. 修改models.py后立即检查

```bash
# 编辑models.py
vim app/models.py

# 立即检查一致性
python scripts/check_schema.py

# 如有差异，同步修改ddl.sql或迁移脚本
```

#### 2. 执行迁移脚本后验证

```bash
# 执行迁移
./scripts/import_sql.sh migrations/20260725_add_column.sql

# 验证schema一致性
python scripts/check_schema.py
```

#### 3. Git pre-commit hook（推荐）

在 `.git/hooks/pre-commit` 添加：

```bash
#!/bin/bash
# 如果修改了models.py，自动检查schema一致性

if git diff --cached --name-only | grep -q "app/models.py"; then
    echo "检测到models.py变更，执行schema一致性检查..."
    cd backend
    python scripts/check_schema.py --db gx_project_dev
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Schema一致性检查失败！"
        echo "请修复models.py与数据库的不一致后再提交。"
        exit 1
    fi
    
    echo "✅ Schema一致性检查通过"
fi
```

## ✅ 检查项说明

### 1. 表存在性检查

检查models.py中定义的表是否都在数据库中存在。

**示例输出**：
```
检查表: devices
  ❌ 表不存在
```

### 2. 字段名一致性检查

检查表的字段名在数据库和模型中是否一致。

**示例输出**：
```
检查表: devices
  ❌ 字段 installation_date: 模型有但数据库没有
  ⚠️  字段 install_date: 数据库有但模型没有
```

**常见问题**：字段名拼写错误或命名风格不统一。

### 3. ENUM值一致性检查 ⭐

检查ENUM类型字段的可选值是否一致（最容易出问题的地方）。

**示例输出**：
```
检查表: devices
  ❌ 字段 type: ENUM值不一致
     数据库多: {'服务'}
     模型多: {'其他'}
```

**常见问题**：
- ddl.sql定义了"硬件/软件/服务"
- models.py定义了"硬件/软件/其他"
- 导致INSERT失败或查询结果异常

### 4. Nullable一致性检查

检查字段是否必填的定义是否一致。

**示例输出**：
```
  ⚠️  devices.description: nullable不一致 (DB: True, Model: False)
```

### 5. 类型检查

检查字段数据类型是否匹配。

**示例输出**：
```
  ⚠️  devices.quantity: 类型不匹配 (DB: INT, Model: VARCHAR)
```

## 📊 输出说明

### 检查通过

```
==========================================
Schema一致性检查
==========================================
数据库: gx_project_dev
检查模型数: 9
==========================================

检查表: devices
  ✅ 字段名一致

检查表: device_systems
  ✅ 字段名一致

... (其他表)

==========================================
检查总结
==========================================
✅ 所有检查通过！数据库schema与模型定义完全一致。

==========================================
错误数: 0
警告数: 0
==========================================
```

### 发现问题

```
==========================================
检查总结
==========================================

❌ 发现 2 个错误:
  ❌ devices.installation_date: 模型中定义但数据库中不存在
  ❌ devices.type: ENUM值不一致
   数据库多: {'服务'}
   模型多: {'其他'}

⚠️  发现 1 个警告:
  ⚠️  devices.install_date: 数据库中存在但模型中未定义

==========================================
错误数: 2
警告数: 1
==========================================
```

## 🔧 修复建议

### 问题类型1：字段名不匹配

**症状**：
```
❌ devices.installation_date: 模型中定义但数据库中不存在
⚠️  devices.install_date: 数据库中存在但模型中未定义
```

**修复方案A**：修改models.py对齐数据库（推荐）

```python
# models.py
class Device(Base):
    # installation_date = Column(DateTime)  # 删除
    install_date = Column(DateTime)  # 使用数据库的字段名
```

**修复方案B**：修改数据库对齐模型

```sql
-- 迁移脚本
ALTER TABLE devices 
    CHANGE COLUMN install_date installation_date DATETIME;
```

### 问题类型2：ENUM值不一致

**症状**：
```
❌ devices.type: ENUM值不一致
   数据库多: {'服务'}
   模型多: {'其他'}
```

**修复方案A**：修改models.py对齐数据库（推荐）

```python
# models.py
class Device(Base):
    type = Column(Enum('硬件', '软件', '服务'))  # 改为'服务'
```

**修复方案B**：修改数据库对齐模型

```sql
-- 迁移脚本
ALTER TABLE devices 
    MODIFY COLUMN type ENUM('硬件','软件','其他');

-- 同时迁移数据
UPDATE devices SET type='其他' WHERE type='服务';
```

### 问题类型3：Nullable不一致

**症状**：
```
⚠️  devices.description: nullable不一致 (DB: True, Model: False)
```

**影响**：
- DB允许NULL，Model标记为必填 → INSERT时可能忘记赋值导致NULL
- DB不允许NULL，Model标记为可选 → INSERT NULL会失败

**修复**：统一为更严格的定义（通常是NOT NULL）

```python
# models.py
class Device(Base):
    description = Column(String, nullable=True)  # 改为允许NULL
```

或

```sql
-- 迁移脚本
ALTER TABLE devices 
    MODIFY COLUMN description VARCHAR(500) NOT NULL;
```

## ⚙️ 配置说明

脚本内置配置（可根据需要修改 `check_schema.py`）：

```python
DB_CONFIG = {
    'host': '124.222.151.69',
    'port': 3306,
    'user': 'root',
    'password': 'GX2026!root',
    'database': 'gx_project_dev',  # 默认数据库
    'charset': 'utf8mb4'
}
```

## 🚨 注意事项

### 1. 检查时机

- ✅ 修改models.py后
- ✅ 执行迁移脚本后
- ✅ Git提交前（通过pre-commit hook）
- ✅ 部署到新环境前

### 2. 不要盲目修复

- 检查出差异后，**先分析原因**再决定修复方向
- 优先保持**数据库为准**（因为数据已经在库里）
- 如需修改数据库，**写迁移脚本**而非直接ALTER

### 3. 生产环境谨慎

```bash
# ❌ 不要直接在生产库检查
python scripts/check_schema.py --db gx_project_prod  # 只读操作，可以

# ❌ 不要在生产库使用 --fix（未来功能）
python scripts/check_schema.py --db gx_project_prod --fix  # 危险！
```

## 🔄 开发流程最佳实践

### 标准流程

1. **修改需求** → 确定需要改哪些字段
2. **更新models.py** → 修改SQLAlchemy模型定义
3. **写迁移脚本** → 创建 `migrations/YYYYMMDD_description.sql`
4. **执行迁移** → `./scripts/import_sql.sh migrations/xxx.sql`
5. **验证一致性** → `python scripts/check_schema.py`
6. **提交代码** → Git提交（pre-commit hook自动检查）

### 反模式（❌ 避免）

```bash
# ❌ 只改models.py不改数据库
vim app/models.py  # 加了新字段
# ... 忘记写迁移脚本
git commit  # 提交了，但数据库没变

# ❌ 只改数据库不改models.py
docker exec -it gx_mysql mysql ...
ALTER TABLE devices ADD COLUMN new_field ...;  # 加了新字段
# ... 忘记改models.py
# SQLAlchemy查询时访问不到这个字段

# ❌ 手动ALTER忘记记录
# 在数据库里随便改了，没写迁移脚本
# 下次重建数据库时丢失这个变更
```

## 📚 相关文档

- [README.md 重要踩坑记录](../README.md#重要踩坑记录)
- [问题登记簿](F:\claude code\问题登记与复盘\问题登记簿.csv) - P004/P005/P006/P020
- [数据库表结构](../README.md#数据库表结构)

## 🔄 更新历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-07-25 | v1.0 | 初始版本，支持表/字段名/ENUM/nullable检查 |

---

**维护者**: GX-PM Team  
**创建日期**: 2026-07-25
