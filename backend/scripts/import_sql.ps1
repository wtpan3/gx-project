# SQL导入封装脚本 - 自动添加utf8mb4字符集参数
# 用法: .\import_sql.ps1 <sql_file> [database_name]

param(
    [Parameter(Mandatory=$true)]
    [string]$SqlFile,
    
    [Parameter(Mandatory=$false)]
    [string]$Database = "gx_project_dev"
)

if (-not (Test-Path $SqlFile)) {
    Write-Host "错误: 文件不存在 - $SqlFile" -ForegroundColor Red
    exit 1
}

Write-Host "================================================"
Write-Host "  SQL导入工具（自动添加utf8mb4字符集）"
Write-Host "================================================"
Write-Host "文件: $SqlFile"
Write-Host "目标库: $Database"
Write-Host "字符集: utf8mb4 (强制)"
Write-Host ""
Write-Host "执行中..."

# 自动添加 --default-character-set=utf8mb4
Get-Content $SqlFile | docker exec -i gx_mysql mysql `
    -uroot `
    -pGX2026!root `
    --default-character-set=utf8mb4 `
    $Database

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ 导入成功" -ForegroundColor Green
    Write-Host ""
    Write-Host "验证方法:"
    Write-Host "  docker exec gx_mysql mysql -uroot -pGX2026!root $Database -e 'SHOW TABLES;'"
} else {
    Write-Host ""
    Write-Host "✗ 导入失败" -ForegroundColor Red
    exit 1
}
