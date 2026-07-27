# GX项目 - MySQL SQL导入脚本（强制utf8mb4字符集）
# 用途: 防止导入SQL时忘记指定字符集导致中文双重编码
# 作者: GX-PM Team
# 日期: 2026-07-23

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$SqlFile,

    [Parameter(Mandatory=$false, Position=1)]
    [string]$DbName = "gx_project_dev"
)

# 颜色输出函数
function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

# 检查文件是否存在
if (-not (Test-Path $SqlFile)) {
    Write-ColorOutput Red "错误: 文件不存在: $SqlFile"
    exit 1
}

# MySQL连接配置
$MYSQL_HOST = "gx_mysql"          # Docker容器名
$MYSQL_USER = "root"
$MYSQL_PASSWORD = "GX2026!root"

Write-ColorOutput Yellow "========================================"
Write-ColorOutput Yellow "GX项目 SQL导入工具"
Write-ColorOutput Yellow "========================================"
Write-ColorOutput Green "SQL文件: $SqlFile"
Write-ColorOutput Green "目标数据库: $DbName"
Write-ColorOutput Green "字符集: utf8mb4 (强制)"
Write-ColorOutput Yellow "========================================"
Write-Output ""

# 确认导入
$confirmation = Read-Host "确认导入? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-ColorOutput Yellow "已取消导入"
    exit 0
}

# 执行导入
Write-ColorOutput Yellow "正在导入..."

Get-Content $SqlFile | docker exec -i $MYSQL_HOST mysql `
    -u$MYSQL_USER `
    -p$MYSQL_PASSWORD `
    --default-character-set=utf8mb4 `
    $DbName

if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput Green "✓ 导入成功！"
    Write-Output ""
    Write-ColorOutput Yellow "建议执行验证:"
    Write-Output "docker exec -it $MYSQL_HOST mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $DbName"
    Write-Output "然后执行: SHOW TABLES; 或 SELECT * FROM <表名> LIMIT 1;"
} else {
    Write-ColorOutput Red "✗ 导入失败"
    exit 1
}
