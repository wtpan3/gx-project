# SQL导入脚本使用说明

## 📌 目的

**防止MySQL中文双重编码问题**：自动为所有SQL导入操作添加 `--default-character-set=utf8mb4` 参数。

## 🎯 解决的问题

历史问题（来自问题登记簿）：
- P007: device_systems.type 中文乱码
- P008: software_modules.phase 中文乱码
- P009: todos.priority 中文乱码
- P010: todos.status 中文乱码

**根本原因**：导入SQL时忘记指定字符集，导致UTF-8中文被当作latin1再转一次UTF-8，造成双重编码。

## 🚀 使用方法

### Bash版本（Git Bash / WSL）

```bash
cd backend

# 导入到默认数据库（gx_project_dev）
./scripts/import_sql.sh ddl.sql

# 导入到指定数据库
./scripts/import_sql.sh migration.sql gx_project

# 导入到生产库
./scripts/import_sql.sh seed_data.sql gx_project
```

### PowerShell版本

```powershell
cd backend

# 导入到默认数据库（gx_project_dev）
.\scripts\import_sql.ps1 ddl.sql

# 导入到指定数据库
.\scripts\import_sql.ps1 migration.sql gx_project

# 导入到生产库
.\scripts\import_sql.ps1 seed_data.sql gx_project
```

## ✅ 脚本特性

1. **自动字符集设置**：自动添加 `--default-character-set=utf8mb4` 参数
2. **参数校验**：检查SQL文件是否存在
3. **清晰输出**：显示导入进度和结果
4. **错误处理**：导入失败时返回非零退出码
5. **默认数据库**：未指定数据库时使用 `gx_project_dev`

## 📋 参数说明

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| SQL文件 | 是 | 要导入的SQL文件路径 | - |
| 数据库名 | 否 | 目标数据库名称 | gx_project_dev |

## 🔧 技术细节

### 核心命令

```bash
docker exec -i gx_mysql mysql \
    -h124.222.151.69 \
    -P3306 \
    -uroot \
    -pGX2026!root \
    --default-character-set=utf8mb4 \  # 关键参数
    gx_project_dev < ddl.sql
```

### 为什么需要 --default-character-set=utf8mb4？

1. **MySQL客户端默认字符集**可能是 latin1
2. **不指定字符集**的后果：
   - 客户端读取SQL文件时用UTF-8解码（正确）
   - 发送到服务器时用latin1编码（错误）
   - 服务器用UTF-8存储（再次编码）
   - 结果：`'硬件'` → `0xc3a7c2a1...`（双重编码乱码）

3. **指定utf8mb4**：
   - 客户端读取SQL文件：UTF-8解码（正确）
   - 发送到服务器：直接以UTF-8发送（正确）
   - 服务器存储：UTF-8存储（正确）
   - 结果：`'硬件'` 正常显示

## ⚠️ 注意事项

### 1. 脚本位置

脚本必须从 `backend` 目录执行，因为SQL文件通常在 `backend` 下。

### 2. Docker容器名称

脚本默认使用 `gx_mysql` 作为容器名称，如果容器名不同需要修改脚本：

```bash
# 修改这一行
DOCKER_CONTAINER="gx_mysql"
```

### 3. 生产环境导入

导入到生产库前，务必：
1. 备份现有数据
2. 在开发库测试SQL
3. 确认SQL内容无误

```bash
# 先备份
docker exec gx_mysql mysqldump -uroot -pGX2026!root \
    --default-character-set=utf8mb4 \
    gx_project > backup_$(date +%Y%m%d_%H%M%S).sql

# 再导入
./scripts/import_sql.sh migration.sql gx_project
```

## 🧪 验证导入结果

导入完成后，检查中文是否正常：

```sql
-- 检查ENUM定义（不应出现乱码或hex）
SHOW COLUMNS FROM device_systems LIKE 'type';
SHOW COLUMNS FROM software_modules LIKE 'phase';

-- 查看实际数据
SELECT type FROM device_systems LIMIT 5;
SELECT phase FROM software_modules LIMIT 5;
```

**正常输出**：
```
type: ENUM('硬件','软件','其他')
phase: ENUM('需求收集','需求确认','软件开发','软件测试','软件部署','上线运行')
```

**异常输出**（双重编码）：
```
type: ENUM(0xc3a7c2a1..., 0xc3a8...)
```

## 📚 相关文档

- [README.md 重要踩坑记录](../README.md#mysql中文双重编码问题-)
- [问题登记簿](F:\claude code\问题登记与复盘\问题登记簿.csv) - P007/P008/P009/P010

## 🔄 更新历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-07-25 | v1.0 | 初始版本，创建Bash和PowerShell两个版本 |

---

**维护者**: GX-PM Team  
**创建日期**: 2026-07-25
