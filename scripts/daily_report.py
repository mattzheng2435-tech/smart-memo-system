#!/usr/bin/env python3
"""
生成每日早报脚本
连接数据库查询今日待办、逾期任务、已完成任务
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.database import get_pool


async def generate_daily_report():
    """生成每日报告"""
    print("📊 正在生成每日报告...")

    try:
        pool = await get_pool()

        # 获取当前时间（上海时区）
        tz = ZoneInfo("Asia/Shanghai")
        now = datetime.now(tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # 获取今日数据
        async with pool.acquire() as conn:
            # 今日待办
            pending_rows = await conn.fetch("""
                SELECT what, when_due, priority, who
                FROM memos
                WHERE status = 'pending'
                  AND when_due >= $1
                  AND when_due < $2
                ORDER BY priority DESC, when_due ASC
            """, today_start, today_end)

            # 逾期任务
            overdue_rows = await conn.fetch("""
                SELECT what, when_due, who
                FROM memos
                WHERE status = 'pending'
                  AND when_due < $1
                ORDER BY when_due ASC
            """, now)

            # 今日已完成
            completed_rows = await conn.fetch("""
                SELECT what, completed_at
                FROM memos
                WHERE status = 'completed'
                  AND completed_at >= $1
                  AND completed_at < $2
                ORDER BY completed_at DESC
            """, today_start, today_end)

        # 格式化报告
        report = format_report(now, pending_rows, overdue_rows, completed_rows)

        # 保存到文件
        report_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "daily_report.md"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ 每日报告已生成: {report_file}")
        print(f"\n📧 报告内容:\n")
        print(report)

        return report

    except Exception as e:
        print(f"❌ 生成报告失败: {e}")
        raise


def format_report(now, pending, overdue, completed):
    """格式化 Markdown 报告"""
    date_str = now.strftime('%Y年%m月%d日')
    weekday = now.strftime('%A')

    report = f"""# 📅 {date_str} {weekday} 每日早报

"""

    # 逾期任务
    if overdue:
        report += """## 🔴 紧急任务 (已逾期)

"""
        for task in overdue:
            due = task['when_due'].astimezone(ZoneInfo("Asia/Shanghai"))
            overdue_str = format_timedelta(now - due)
            report += f"- ⚠️ **{task['what']}**\n"
            report += f"  截止: {due.strftime('%H:%M')}, 逾期: {overdue_str}"
            if task['who']:
                report += f", 相关人: {task['who']}"
            report += "\n"
    else:
        report += """## 🔴 紧急任务 (已逾期)

✅ 无逾期任务

"""

    # 今日待办
    report += f"""## 📋 今日待办 ({len(pending)}项)

"""
    if pending:
        for task in pending:
            priority_icon = get_priority_icon(task['priority'])
            due = task['when_due'].astimezone(ZoneInfo("Asia/Shanghai"))
            report += f"{priority_icon} **{due.strftime('%H:%M')}** - {task['what']}\n"
            if task['who']:
                report += f"  👥 {task['who']}\n"
    else:
        report += "✅ 今日暂无待办任务\n"

    # 今日已完成
    report += f"""
## ✅ 今日已完成 ({len(completed)}项)

"""
    if completed:
        for task in completed:
            completed_at = task['completed_at'].astimezone(ZoneInfo("Asia/Shanghai"))
            report += f"- ~~{task['what']}~~ ({completed_at.strftime('%H:%M')})\n"
    else:
        report += "暂无\n"

    # 统计信息
    total_pending = len(pending) + len(overdue)
    report += f"""
---

📊 今日概览
- 待办: {len(pending)} 项
- 逾期: {len(overdue)} 项
- 已完成: {len(completed)} 项
- 总计: {total_pending + len(completed)} 项

💪 加油！今天也是高效的一天！

---
*本邮件由智能备忘录系统自动生成*
"""

    return report


def format_timedelta(td):
    """格式化时间差"""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    days = hours // 24

    if days > 0:
        return f"{days}天"
    elif hours > 0:
        return f"{hours}小时"
    else:
        return f"{total_seconds // 60}分钟"


def get_priority_icon(priority):
    """获取优先级图标"""
    icons = {
        'high': '🔴',
        'normal': '🟡',
        'low': '🟢'
    }
    return icons.get(priority, '⚪')


if __name__ == "__main__":
    report = asyncio.run(generate_daily_report())
