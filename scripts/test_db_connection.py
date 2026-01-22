#!/usr/bin/env python3
"""
Supabase 数据库连接测试脚本
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# 数据库配置
DATABASE_URL = "postgresql://postgres:Zyz0201afq!@db.lfhbowwktzoaeznfvxky.supabase.co:5432/postgres"

async def test_connection():
    """测试数据库连接"""
    print("[INFO] Connecting to Supabase database...")
    print(f"   Database: db.lfhbowwktzoaeznfvxky.supabase.co")
    print(f"   Port: 5432")
    print()

    try:
        # 创建连接
        conn = await asyncpg.connect(DATABASE_URL, timeout=10)

        print("[OK] Database connection successful!\n")

        # 测试查询
        version = await conn.fetchval("SELECT version()")
        print(f"[INFO] PostgreSQL version:")
        print(f"   {version[:60]}...\n")

        # 检查表是否存在
        tables = await conn.fetch("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """)

        if tables:
            print("[INFO] Current tables:")
            for t in tables:
                print(f"   - {t['tablename']}")
        else:
            print("[WARN] No tables found in database")
            print("\n[TIP] Please execute in Supabase SQL Editor:")
            print("   file: supabase/schema.sql")

        # 关闭连接
        await conn.close()
        print("\n[OK] Test completed!")

    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        print("\n[TIP] Please check:")
        print("   1. Is supabase/config.py configured correctly?")
        print("   2. Is Supabase project running?")
        print("   3. Is database password correct?")
        print("   4. Is port 5432 (not 6543)?")
        return False

    return True

if __name__ == "__main__":
    asyncio.run(test_connection())
