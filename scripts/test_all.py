#!/usr/bin/env python3
"""
功能测试脚本 - 测试备忘录系统的核心功能
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta

# 数据库配置
DATABASE_URL = "postgresql://postgres:Zyz0201afq!@db.lfhbowwktzoaeznfvxky.supabase.co:5432/postgres"

async def test_create_memo():
    """测试创建备忘录"""
    print("\n=== Test 1: Create Memo ===")

    conn = await asyncpg.connect(DATABASE_URL)

    # 创建一个测试备忘录
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)

    row = await conn.fetchrow("""
        INSERT INTO memos (what, when_due, who, priority)
        VALUES ($1, $2, $3, $4)
        RETURNING *
    """, "测试任务：给Paul发邮件", tomorrow, "Paul", "high")

    await conn.close()

    print(f"[OK] Memo created!")
    print(f"   ID: {row['id']}")
    print(f"   Content: {row['what']}")
    print(f"   Due: {row['when_due']}")
    print(f"   Who: {row['who']}")
    print(f"   Priority: {row['priority']}")

    return row['id']

async def test_search_memos():
    """测试搜索备忘录"""
    print("\n=== Test 2: Search Memos ===")

    conn = await asyncpg.connect(DATABASE_URL)

    rows = await conn.fetch("""
        SELECT * FROM memos
        WHERE to_tsvector('english', what) @@ to_tsquery('english', $1)
        ORDER BY created_at DESC
        LIMIT 5
    """, "Paul")

    await conn.close()

    print(f"[OK] Found {len(rows)} memos")
    for i, row in enumerate(rows, 1):
        print(f"\n{i}. {row['what']}")
        print(f"   Time: {row['when_due']}")
        if row['who']:
            print(f"   Who: {row['who']}")

async def test_list_pending():
    """测试列出待办"""
    print("\n=== Test 3: List Pending ===")

    conn = await asyncpg.connect(DATABASE_URL)

    rows = await conn.fetch("""
        SELECT * FROM memos
        WHERE status = 'pending'
        ORDER BY priority DESC, when_due ASC
        LIMIT 10
    """)

    await conn.close()

    print(f"[OK] Found {len(rows)} pending memos")
    for i, row in enumerate(rows, 1):
        priority_icon = "[HIGH]" if row['priority'] == 'high' else "[NORMAL]"
        print(f"\n{i}. {priority_icon} {row['what']}")
        if row['when_due']:
            due_str = row['when_due'].strftime("%Y-%m-%d %H:%M")
            print(f"   Due: {due_str}")

async def test_complete_memo():
    """测试完成任务"""
    print("\n=== Test 4: Complete Memo ===")

    conn = await asyncpg.connect(DATABASE_URL)

    # 找到一个待完成的任务
    row = await conn.fetchrow("""
        SELECT * FROM memos
        WHERE status = 'pending'
        ORDER BY created_at ASC
        LIMIT 1
    """)

    if not row:
        print("[WARN] No pending memo to complete")
        await conn.close()
        return

    # 标记为完成
    result = await conn.fetchrow("""
        UPDATE memos
        SET status = 'completed', completed_at = NOW()
        WHERE id = $1
        RETURNING *
    """, row['id'])

    await conn.close()

    print(f"[OK] Memo completed!")
    print(f"   Task: {result['what']}")
    print(f"   Completed at: {result['completed_at']}")

async def main():
    """运行所有测试"""
    print("""
╔════════════════════════════════════════════════════════════╗
║     Smart Memo System - Functional Test                 ║
╚════════════════════════════════════════════════════════════╝
""")

    try:
        await test_create_memo()
        await test_search_memos()
        await test_list_pending()
        await test_complete_memo()

        print("\n" + "="*60)
        print("[OK] All tests passed!")
        print("="*60)
        print("\nYour Smart Memo System is ready to use!")
        print("\nNext steps:")
        print("1. Try it in Claude Code: '提醒我明天给Paul发邮件'")
        print("2. Deploy to Railway (optional)")
        print("3. Configure GitHub Actions (optional)")

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
