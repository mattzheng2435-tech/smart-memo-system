"""
批量清算工具 - 批量完成/删除备忘录
"""

from ..database import fuzzy_search_memos, batch_complete


async def handle(pool, args):
    """
    处理批量清算请求

    Args:
        pool: 数据库连接池
        args: {criteria, preview_only}

    Returns:
        str: 响应消息
    """
    criteria = args.get("criteria", "")
    preview_only = args.get("preview_only", True)

    if not criteria:
        return """❌ 请提供清算条件

💡 示例:
   - "已完成" - 清算所有已完成的任务
   - "过期" - 清算所有逾期的任务
   - "低优先级" - 清算所有低优先级任务
   - "包含关键词X" - 清算所有包含特定关键词的任务"""

    # 解析条件
    keywords = []
    status_filter = "completed"  # 默认清算已完成的

    if criteria == "已完成" or criteria == "completed":
        status_filter = "completed"
    elif criteria == "逾期" or criteria == "过期" or criteria == "overdue":
        status_filter = "pending"
        keywords = []  # 特殊处理
    elif criteria == "低优先级" or criteria == "low":
        status_filter = "pending"
        keywords = []  # 特殊处理
    else:
        keywords = criteria.split()

    # 搜索匹配的备忘录
    async with pool.acquire() as conn:
        if criteria == "逾期" or criteria == "过期":
            # 查询逾期任务
            from datetime import datetime
            rows = await conn.fetch("""
                SELECT * FROM memos
                WHERE status = 'pending' AND when_due < NOW()
                ORDER BY when_due ASC
            """)
            memos = [dict(row) for row in rows]
        elif criteria == "低优先级" or criteria == "low":
            rows = await conn.fetch("""
                SELECT * FROM memos
                WHERE status = 'completed' AND priority = 'low'
                ORDER BY completed_at DESC
            """)
            memos = [dict(row) for row in rows]
        else:
            memos = await fuzzy_search_memos(conn, keywords, status=status_filter)

    if not memos:
        return f"""🔍 未找到匹配条件 '{criteria}' 的备忘录

无需清算。"""

    if preview_only:
        # 预览模式
        return format_preview(memos, criteria)
    else:
        # 执行清算
        memo_ids = [m['id'] for m in memos]
        async with pool.acquire() as conn:
            count = await batch_complete(conn, memo_ids)

        return f"""✅ 已批量清算 {count} 个任务

条件: {criteria}

太棒了！继续保持高效！"""


def format_preview(memos, criteria):
    """格式化预览结果"""
    response = f"""🔍 预览: 将清算以下 {len(memos)} 个任务

条件: {criteria}

--------
"""

    for i, memo in enumerate(memos, 1):
        response += f"{i}. {memo['what']}"

        if memo.get('when_due'):
            due_str = memo['when_due'].strftime("%Y-%m-%d %H:%M")
            response += f"\n   📅 {due_str}"

        if memo.get('who'):
            response += f"\n   👥 {memo['who']}"

        response += f"\n   🆔 {memo['id'][:8]}..."
        response += "\n\n"

    response += """--------
💡 这是预览模式，尚未执行。

确认要清算这些任务吗？请设置 preview_only=false 再次调用。
"""

    return response
