"""
Supabase PostgreSQL 连接池配置
使用 asyncpg 实现高性能异步数据库连接

重要: 使用直连端口 (5432) 而非 Supabase 池化端口 (6543)
asyncpg 与 Supabase PgBouncer 不兼容
"""

import asyncpg
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from supabase.config import DATABASE_URL

_pool = None

async def get_pool():
    """
    获取数据库连接池 (单例模式)
    第一次调用时创建连接池，后续调用复用

    Returns:
        asyncpg.Pool: 数据库连接池
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=60,
            timeout=30
        )
    return _pool

async def close_pool():
    """关闭数据库连接池"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

async def get_connection():
    """
    获取单个数据库连接
    用于需要事务控制的场景

    Returns:
        asyncpg.Connection: 数据库连接
    """
    pool = await get_pool()
    return await pool.acquire()
