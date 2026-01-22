"""
Supabase 配置文件
复制此文件为 config.py 并填写你的凭证
"""

# Supabase 项目配置
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"  # 客户端密钥
SUPABASE_SERVICE_KEY = "your-service-role-key"  # 仅服务端使用

# 数据库直连字符串
# 重要: 使用端口 5432 (直连) 而非 6543 (池化)
# asyncpg 与 Supabase PgBouncer 不兼容
DATABASE_URL = "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres"

# 时区设置
TIMEZONE = "Asia/Shanghai"
