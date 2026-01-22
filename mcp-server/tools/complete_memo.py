"""
完成备忘录工具 - 支持模糊语义匹配
"""

from ..database import fuzzy_search_memos, complete_memo


async def handle(pool, args):
    """
    处理完成备忘录请求

    Args:
        pool: 数据库连接池
        args: {memo_id} - 可以是 ID 或模糊匹配文本

    Returns:
        str: 响应消息
    """
    memo_id = args.get("memo_id", "")

    if not memo_id:
        return "❌ 请提供要完成的备忘录ID或描述"

    # 检查是否是 UUID (精确匹配)
    import uuid
    try:
        uuid.UUID(memo_id)
        # 是有效的 UUID，直接完成
        async with pool.acquire() as conn:
            result = await complete_memo(conn, memo_id)

        if result:
            return f"""🎉 太棒了！已完成任务:

  {result['what']}

  完成时间: {result['completed_at'].strftime('%Y-%m-%d %H:%M')}"""
        else:
            return f"❌ 未找到 ID 为 {memo_id} 的备忘录"

    except ValueError:
        # 不是 UUID，尝试模糊搜索
        pass

    # 模糊搜索
    keywords = memo_id.split()

    async with pool.acquire() as conn:
        results = await fuzzy_search_memos(conn, keywords, status="pending")

    if not results:
        return f"""❌ 未找到匹配 '{memo_id}' 的待办任务

💡 提示:
   - 尝试使用不同的关键词
   - 或者直接使用备忘录ID"""

    if len(results) == 1:
        # 唯一匹配，直接完成
        memo = results[0]
        async with pool.acquire() as conn:
            result = await complete_memo(conn, memo['id'])

        return f"""🎉 太棒了！已完成任务:

  {result['what']}

  完成时间: {result['completed_at'].strftime('%Y-%m-%d %H:%M')}"""

    # 多个匹配，让用户选择
    response = f"""🤔 找到 {len(results)} 个匹配的任务，请问你要完成哪一个？

"""

    for i, row in enumerate(results, 1):
        response += f"{i}. {row['what']}"
        if row['when_due']:
            due_str = row['when_due'].strftime("%Y-%m-%d %H:%M")
            response += f" (截止: {due_str})"
        response += "\n"

    response += "\n💡 请使用具体的任务ID或更精确的描述"

    return response
