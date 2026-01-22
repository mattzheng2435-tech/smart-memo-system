#!/usr/bin/env python3
"""
生成每日早报 - GitHub Actions 版本（使用 Supabase REST API）
"""
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from supabase import create_client, Client

# Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def generate_daily_report():
    """生成每日报告"""
    print("[INFO] Generating daily report...")

    # 创建 Supabase 客户端
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 获取当前时间（上海时区）
    tz = ZoneInfo("Asia/Shanghai")
    now = datetime.now(tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # 查询数据 - 今日待办
    pending_response = supabase.table('memos').select('*').eq('status', 'pending').gte('when_due', today_start.isoformat()).lt('when_due', today_end.isoformat()).order('priority', desc=True).order('when_due').execute()
    pending = pending_response.data

    # 逾期任务
    overdue_response = supabase.table('memos').select('*').eq('status', 'pending').lt('when_due', now.isoformat()).order('when_due').execute()
    overdue = overdue_response.data

    # 今日已完成
    completed_response = supabase.table('memos').select('*').eq('status', 'completed').gte('completed_at', today_start.isoformat()).lt('completed_at', today_end.isoformat()).order('completed_at', desc=True).execute()
    completed = completed_response.data

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
    generate_daily_report()
