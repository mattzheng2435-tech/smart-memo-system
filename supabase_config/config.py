"""
Supabase 配置文件
"""

# Supabase 项目配置
SUPABASE_URL = "https://lfhbowwktzoaeznfvxky.supabase.co"
SUPABASE_KEY = "sb_publishable_lV-31rITpkrBfMBKzYca6Q_I25B43HZ"
SUPABASE_SERVICE_KEY = "sb_secret_bl9B1bTRqU5vtjXV7lO6Yg_xO2YI308"

# 数据库直连字符串
# 重要: 使用端口 5432 (直连) 而非 6543 (Pooler)
# asyncpg 与 Supabase PgBouncer 不兼容
DATABASE_URL = "postgresql://postgres:Zyz0201afq!@db.lfhbowwktzoaeznfvxky.supabase.co:5432/postgres"

# 时区设置
TIMEZONE = "Asia/Shanghai"
