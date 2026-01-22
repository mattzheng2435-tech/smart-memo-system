"""
搜索备忘录工具 - 支持模糊语义搜索
"""

from ..database import search_memos, fuzzy_search_memos


async def handle(pool, args):
    """
    处理搜索备忘录请求

    Args:
        pool: 数据库连接池
        args: {query, status, limit}

    Returns:
        str: 搜索结果
    """
    query = args.get("query", "")
    status = args.get("status", "pending")
    limit = args.get("limit", 10)

    if not query:
        return "❌ 请提供搜索关键词"

    async with pool.acquire() as conn:
        # 先尝试模糊搜索（更宽松）
        keywords = query.split()
        fuzzy_results = await fuzzy_search_memos(conn, keywords, status)

        if not fuzzy_results:
            # 如果模糊搜索无结果，尝试全文搜索
            results = await search_memos(conn, query, status, limit)
        else:
            results = fuzzy_results

    if not results:
        return f"""🔍 搜索 '{query}' 未找到匹配的备忘录

💡 建议:
   - 尝试使用不同的关键词
   - 检查拼写是否正确
   - 使用 'status=all' 搜索所有状态的任务"""

    # 格式化结果
    response = f"""🔍 搜索 '{query}' 的结果 (共 {len(results)} 项):

"""

    for i, row in enumerate(results, 1):
        status_icon = "✅" if row['status'] == 'completed' else "⏳"
        priority_icon = get_priority_icon(row['priority'])

        response += f"""{i}. {status_icon} {priority_icon} {row['what']}
"""

        if row['when_due']:
            due_str = row['when_due'].strftime("%Y-%m-%d %H:%M")
            response += f"   📅 截止: {due_str}"

        if row['who']:
            response += f"\n   👥 相关人: {row['who']}"

        response += "\n"

    return response


def get_priority_icon(priority):
    """获取优先级图标"""
    icons = {
        'high': '🔴',
        'normal': '🟡',
        'low': '🟢'
    }
    return icons.get(priority, '⚪')
