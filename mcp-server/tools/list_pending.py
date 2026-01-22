"""
列出待办事项工具
"""

from datetime import datetime
from ..database import get_pending_memos


async def handle(pool, args):
    """
    处理列出待办请求

    Args:
        pool: 数据库连接池
        args: {limit, category}

    Returns:
        str: 待办列表
    """
    limit = args.get("limit", 20)
    category = args.get("category", None)

    async with pool.acquire() as conn:
        memos = await get_pending_memos(conn, limit, category)

    if not memos:
        return """📋 当前没有待办任务

✨ 太棒了！所有任务都已完成！"""

    # 按优先级分组
    high_priority = []
    normal_priority = []
    low_priority = []

    for memo in memos:
        if memo['priority'] == 'high':
            high_priority.append(memo)
        elif memo['priority'] == 'normal':
            normal_priority.append(memo)
        else:
            low_priority.append(memo)

    # 格式化输出
    response = f"""📋 待办事项列表 (共 {len(memos)} 项)

"""

    # 高优先级
    if high_priority:
        response += """🔴 高优先级
--------
"""
        for memo in high_priority:
            response += format_memo(memo)
        response += "\n"

    # 普通优先级
    if normal_priority:
        response += """🟡 普通优先级
--------
"""
        for memo in normal_priority:
            response += format_memo(memo)
        response += "\n"

    # 低优先级
    if low_priority:
        response += """🟢 低优先级
--------
"""
        for memo in low_priority:
            response += format_memo(memo)

    return response


def format_memo(memo):
    """格式化单个备忘录"""
    response = f"⏳ {memo['what']}"

    if memo['when_due']:
        # 计算是否逾期
        due = memo['when_due']
        now = datetime.now(memo['when_due'].tzinfo)

        if due < now:
            # 逾期
            overdue_hours = (now - due).total_seconds() / 3600
            if overdue_hours < 24:
                response += f" ⚠️ 逾期 {int(overdue_hours)} 小时"
            else:
                response += f" ⚠️ 逾期 {int(overdue_hours / 24)} 天"
        else:
            # 未逾期，显示截止时间
            due_str = due.strftime("%m-%d %H:%M")
            response += f" 📅 {due_str}"

    if memo['who']:
        response += f"\n   👥 {memo['who']}"

    response += f"\n   🆔 {memo['id'][:8]}..."

    response += "\n"
    return response
