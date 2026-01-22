"""
数据库查询封装
所有 SQL 操作都在这里定义
"""

from datetime import datetime
from typing import List, Optional
import uuid


async def create_memo(
    conn,
    what: str,
    when_due: Optional[datetime] = None,
    who: Optional[str] = None,
    priority: str = "normal",
    tags: Optional[List[str]] = None,
    context: Optional[str] = None,
    category: Optional[str] = None,
    metadata: Optional[dict] = None
) -> dict:
    """创建新备忘录"""
    memo_id = uuid.uuid4()

    row = await conn.fetchrow("""
        INSERT INTO memos (id, what, when_due, who, priority, tags, context, category, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
    """, memo_id, what, when_due, who, priority, tags or [], context, category, metadata or {})

    return dict(row)


async def search_memos(
    conn,
    query: str,
    status: str = "pending",
    limit: int = 10
) -> List[dict]:
    """
    全文搜索备忘录
    使用 PostgreSQL 的全文搜索功能
    """
    if status == "all":
        rows = await conn.fetch("""
            SELECT id, what, when_due, who, status, priority,
                   ts_rank(to_tsvector('english', what || ' ' || COALESCE(context, '')),
                           to_tsquery('english', $1)) as rank
            FROM memos
            WHERE to_tsvector('english', what || ' ' || COALESCE(context, '')) @@ to_tsquery('english', $1)
            ORDER BY rank DESC, created_at DESC
            LIMIT $2
        """, query, limit)
    else:
        rows = await conn.fetch("""
            SELECT id, what, when_due, who, status, priority,
                   ts_rank(to_tsvector('english', what || ' ' || COALESCE(context, '')),
                           to_tsquery('english', $1)) as rank
            FROM memos
            WHERE status = $2
              AND to_tsvector('english', what || ' ' || COALESCE(context, '')) @@ to_tsquery('english', $1)
            ORDER BY rank DESC, created_at DESC
            LIMIT $3
        """, query, status, limit)

    return [dict(row) for row in rows]


async def fuzzy_search_memos(
    conn,
    keywords: List[str],
    status: str = "pending"
) -> List[dict]:
    """
    模糊搜索备忘录
    用于自然语言匹配 (例如 "给老板做演示")
    """
    if not keywords:
        return []

    # 构建查询条件
    conditions = []
    for keyword in keywords:
        conditions.append(f"what ILIKE '%{keyword}%'")

    where_clause = " AND ".join(conditions)
    if status != "all":
        where_clause = f"status = '{status}' AND " + where_clause

    query = f"""
        SELECT * FROM memos
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT 20
    """

    rows = await conn.fetch(query)
    return [dict(row) for row in rows]


async def complete_memo(conn, memo_id: str) -> Optional[dict]:
    """标记备忘录为完成"""
    row = await conn.fetchrow("""
        UPDATE memos
        SET status = 'completed',
            completed_at = NOW(),
            updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """, memo_id)

    return dict(row) if row else None


async def get_pending_memos(
    conn,
    limit: int = 20,
    category: Optional[str] = None
) -> List[dict]:
    """获取待办事项列表"""
    if category:
        rows = await conn.fetch("""
            SELECT * FROM memos
            WHERE status = 'pending' AND category = $1
            ORDER BY priority DESC, when_due ASC
            LIMIT $2
        """, category, limit)
    else:
        rows = await conn.fetch("""
            SELECT * FROM memos
            WHERE status = 'pending'
            ORDER BY priority DESC, when_due ASC
            LIMIT $1
        """, limit)

    return [dict(row) for row in rows]


async def get_daily_memos(conn, date: datetime) -> dict:
    """
    获取指定日期的备忘录统计
    用于每日早报生成
    """
    day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start.replace(hour=23, minute=59, second=59, microsecond=999999)

    # 今日待办
    pending = await conn.fetch("""
        SELECT what, when_due, priority, who
        FROM memos
        WHERE status = 'pending'
          AND when_due >= $1
          AND when_due < $2
        ORDER BY priority DESC, when_due ASC
    """, day_start, day_end)

    # 逾期任务
    overdue = await conn.fetch("""
        SELECT what, when_due, who
        FROM memos
        WHERE status = 'pending'
          AND when_due < $1
        ORDER BY when_due ASC
    """, day_start)

    # 今日已完成
    completed = await conn.fetch("""
        SELECT what, completed_at
        FROM memos
        WHERE status = 'completed'
          AND completed_at >= $1
          AND completed_at < $2
        ORDER BY completed_at DESC
    """, day_start, day_end)

    return {
        'pending': [dict(row) for row in pending],
        'overdue': [dict(row) for row in overdue],
        'completed': [dict(row) for row in completed]
    }


async def batch_complete(conn, memo_ids: List[str]) -> int:
    """批量完成备忘录"""
    result = await conn.execute("""
        UPDATE memos
        SET status = 'completed',
            completed_at = NOW(),
            updated_at = NOW()
        WHERE id = ANY($1)
    """, memo_ids)

    # result 返回 "UPDATE count" 格式
    count = int(result.split()[-1])
    return count
