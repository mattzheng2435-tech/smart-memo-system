#!/usr/bin/env python3
"""
功能测试脚本
测试备忘录系统的核心功能
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.database import get_pool, create_memo, search_memos, get_pending_memos, complete_memo


async def test_create_memo():
    """测试创建备忘录"""
    print("\n" + "="*60)
    print("测试 1: 创建备忘录")
    print("="*60)

    pool = await get_pool()

    async with pool.acquire() as conn:
        # 创建一个测试备忘录
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)

        row = await create_memo(
            conn,
            what="测试任务：给Paul发邮件",
            when_due=tomorrow,
            who="Paul",
            priority="high"
        )

        print(f"✅ 创建成功!")
        print(f"   ID: {row['id']}")
        print(f"   内容: {row['what']}")
        print(f"   时间: {row['when_due']}")
        print(f"   相关人: {row['who']}")


async def test_search_memos():
    """测试搜索备忘录"""
    print("\n" + "="*60)
    print("测试 2: 搜索备忘录")
    print("="*60)

    pool = await get_pool()

    async with pool.acquire() as conn:
        results = await search_memos(conn, "Paul", "pending", 5)

        print(f"✅ 搜索完成，找到 {len(results)} 个结果")
        for i, row in enumerate(results, 1):
            print(f"\n{i}. {row['what']}")
            if row['when_due']:
                print(f"   时间: {row['when_due'].strftime('%Y-%m-%d %H:%M')}")
            if row['who']:
                print(f"   相关人: {row['who']}")


async def test_list_pending():
    """测试列出待办"""
    print("\n" + "="*60)
    print("测试 3: 列出待办")
    print("="*60)

    pool = await get_pool()

    async with pool.acquire() as conn:
        memos = await get_pending_memos(conn, limit=5)

        print(f"✅ 找到 {len(memos)} 个待办")
        for i, memo in enumerate(memos, 1):
            priority_icon = "🔴" if memo['priority'] == 'high' else "🟡"
            print(f"\n{i}. {priority_icon} {memo['what']}")
            if memo['when_due']:
                due_str = memo['when_due'].strftime("%m-%d %H:%M")
                print(f"   📅 {due_str}")


async def test_complete_memo():
    """测试完成任务"""
    print("\n" + "="*60)
    print("测试 4: 完成任务")
    print("="*60)

    pool = await get_pool()

    # 先搜索一个待完成的任务
    async with pool.acquire() as conn:
        results = await search_memos(conn, "测试", "pending", 1)

        if not results:
            print("⚠️  没有找到可以完成测试的任务")
            return

        memo_id = results[0]['id']
        print(f"完成任务: {results[0]['what']}")

        result = await complete_memo(conn, memo_id)

        if result:
            print(f"✅ 任务已完成!")
            print(f"   完成时间: {result['completed_at'].strftime('%Y-%m-%d %H:%M')}")


async def main():
    """运行所有测试"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          智能备忘录系统 - 功能测试                         ║
╚══════════════════════════════════════════════════════════════╝
""")

    try:
        await test_create_memo()
        await test_search_memos()
        await test_list_pending()
        await test_complete_memo()

        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)

        print("\n💡 下一步:")
        print("   1. 在 Claude Code 中测试对话")
        print("   2. 部署到 Railway")
        print("   3. 配置 GitHub Actions 自动化")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n💡 请检查:")
        print("   1. supabase/config.py 是否正确配置")
        print("   2. Supabase 项目是否正常运行")
        print("   3. 数据库表是否已创建")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
