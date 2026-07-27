import pymysql

conn = pymysql.connect(
    host='124.222.151.69',
    user='root',
    password='GX2026!root',
    database='gx_project_dev',
    charset='utf8mb4'
)

cursor = conn.cursor()

# 恢复status枚举为原始值
cursor.execute(""
    ALTER TABLE risks 
    MODIFY COLUMN status ENUM('已识别', '应对中', '已关闭') 
    COMMENT '风险状态'
"")

conn.commit()
print('✓ status枚举已恢复为：已识别/应对中/已关闭')

cursor.close()
conn.close()
