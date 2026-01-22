#!/usr/bin/env python3
"""测试 MCP Server 导入"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'mcp-server'))

try:
    from database.connection import get_pool
    print("[OK] MCP Server imports working!")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

# 测试数据库连接
async def test():
    pool = await get_pool()
    print("[OK] Database pool created!")
    import asyncio
    asyncio.run(test())
