#!/usr/bin/env python3
"""
生成每日早报 - GitHub Actions 版本
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")

async def generate_daily_report():
    """生成每日报告"""
    print("[INFO] Generating daily report...")

    # 连接数据库
    conn = await asyncpg.connect(DATABASE_URL)

    # 获取当前时间（上海时区）
    tz = ZoneInfo("Asia/Shanghai")
    now = datetime.now(tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # 查询数据
    # 今日待办
    pending = await conn.fetch("""
        SELECT what, when_due, priority, who
        FROM memos
        WHERE status = 'pending'
          AND when_due >= $1
          AND when_due < $2
        ORDER BY priority DESC, when_due ASC
    """, today_start, today_end)

    # 逾期任务
    overdue = await conn.fetch("""
        SELECT what, when_due, who
        FROM memos
        WHERE status = 'pending'
          AND when_due < $1
        ORDER BY when_due ASC
    """, now)

    # 今日已完成
    completed = await conn.fetch("""
        SELECT what, completed_at
        FROM memos
        WHERE status = 'completed'
          AND completed_at >= $1
          AND completed_at < $2
        ORDER BY completed_at DESC
    """, today_start, today_end)

    await conn.close()

    # 格式化报告
    report = format_report(now, pending, overdue, completed)

    # 保存到文件
    report_file = "daily_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[OK] Daily report generated: {report_file}")
    print(f"[INFO] Pending: {len(pending)}, Overdue: {len(overdue)}, Completed: {len(completed)}")

    return report


def format_report(now, pending, overdue, completed):
    """格式化 Markdown 报告"""
    date_str = now.strftime('%Y年%m月%d日')
    weekday = now.strftime('%A')

    report = f"""# {date_str} {weekday} 每日早报

"""

    # 逾期任务
    if overdue:
        report += """## [URGENT] Overdue Tasks

"""
        for task in overdue:
            due = task['when_due'].astimezone(tz)
            overdue_hours = int((now - due).total_seconds() / 3600)
            overdue_str = f"{overdue_hours}h" if overdue_hours > 0 else "recently"
            report += f"- [OVERDUE by {overdue_str}] **{task['what']}**\n"
            if task['who']:
                report += f"  Due: {due.strftime('%H:%M')}, Person: {task['who']}\n"
    else:
        report += """## [URGENT] Overdue Tasks

[OK] No overdue tasks

"""

    # 今日待办
    report += f"""## Today's Tasks ({len(pending)} items)

"""
    if pending:
        for task in pending:
            priority_icon = "[HIGH]" if task['priority'] == 'high' else "[NORMAL]"
            due = task['when_due'].astimezone(tz)
            report += f"{priority_icon} **{due.strftime('%H:%M')}** - {task['what']}\n"
            if task['who']:
                report += f"  Person: {task['who']}\n"
    else:
        report += "[OK] No pending tasks for today\n"

    # 今日已完成
    report += f"""
## Completed Today ({len(completed)} items)

"""
    if completed:
        for task in completed:
            completed_at = task['completed_at'].astimezone(tz)
            report += f"- ~~{task['what']}~~ ({completed_at.strftime('%H:%M')})\n"
    else:
        report += "No completed tasks yet\n"

    # 统计
    total_pending = len(pending) + len(overdue)
    report += f"""
---

## Summary
- Pending: {len(pending)}
- Overdue: {len(overdue)}
- Completed: {len(completed)}
- Total: {total_pending + len(completed)}

Keep going! Have a productive day!

---
*Automated by Smart Memo System*
"""

    return report


if __name__ == "__main__":
    asyncio.run(generate_daily_report())
