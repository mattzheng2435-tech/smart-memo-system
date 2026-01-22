#!/usr/bin/env python3
"""
数据库初始化脚本
用于测试数据库连接和创建表结构
"""

import asyncio
import sys
import os

# 直接添加 mcp-server 到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mcp_server_path = os.path.join(project_root, 'mcp-server')
sys.path.insert(0, mcp_server_path)

# 同时添加项目根目录到路径
sys.path.insert(0, project_root)

try:
    from database.connection import get_pool
except ImportError:
    # 如果还是失败，尝试直接导入
    import importlib.util
    spec = importlib.util.spec_from_file_location("connection", os.path.join(mcp_server_path, "database", "connection.py"))
    connection_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(connection_module)
    get_pool = connection_module.get_pool


async def init_database():
    """初始化数据库"""
    print("🔌 连接到数据库...")

    try:
        pool = await get_pool()
        print("✅ 数据库连接成功！")

        # 测试查询
        async with pool.acquire() as conn:
            version = await conn.fetchval("SELECT version()")
            print(f"📊 PostgreSQL 版本: {version[:50]}...")

            # 检查表是否存在
            tables = await conn.fetch("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
            """)
            print(f"📋 当前数据库表: {[t['tablename'] for t in tables]}")

        print("\n✅ 数据库初始化完成！")
        print("\n💡 下一步:")
        print("   1. 在 Supabase 控制台执行 supabase/schema.sql 创建表结构")
        print("   2. 运行测试: python scripts/test_connection.py")

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n💡 请检查:")
        print("   1. supabase/config.py 是否正确配置")
        print("   2. DATABASE_URL 是否使用端口 5432 (不是 6543)")
        print("   3. Supabase 项目是否正常运行")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_database())
