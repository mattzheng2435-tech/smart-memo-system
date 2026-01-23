#!/usr/bin/env python3
"""
生成每日早报 - GitHub Actions 版本（使用 Supabase REST API）
"""
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from supabase import create_client, Client
from dateutil import parser as date_parser

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# 如果环境变量为空，尝试从本地配置文件读取
if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        import supabase_config.config as config
        if not SUPABASE_URL:
            SUPABASE_URL = config.SUPABASE_URL
        if not SUPABASE_KEY:
            SUPABASE_KEY = config.SUPABASE_SERVICE_KEY
        print(f"[DEBUG] Loaded config from file: URL={SUPABASE_URL[:30]}...")
    except ImportError as e:
        print(f"[DEBUG] Failed to import config: {e}")
        pass

# 验证配置
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is not configured")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY is not configured")

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

    # 查询所有待办任务
    pending_response = supabase.table('memos').select('*').eq('status', 'pending').order('when_due').execute()
    pending = pending_response.data

    # 逾期任务
    overdue_response = supabase.table('memos').select('*').eq('status', 'pending').lt('when_due', now.isoformat()).order('when_due').execute()
    overdue = overdue_response.data

    # 今日已完成
    completed_response = supabase.table('memos').select('*').eq('status', 'completed').gte('completed_at', today_start.isoformat()).lt('completed_at', today_end.isoformat()).order('completed_at', desc=True).execute()
    completed = completed_response.data

    # 格式化报告
    report = format_report(now, pending, overdue, completed, tz)

    # 保存到文件
    report_file = "daily_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[OK] Daily report generated: {report_file}")
    print(f"[INFO] Pending: {len(pending)}, Overdue: {len(overdue)}, Completed: {len(completed)}")

    return report


def format_report(now, pending, overdue, completed, tz):
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
            due_str = task.get('when_due')
            if due_str:
                due = date_parser.isoparse(due_str).astimezone(tz)
                overdue_hours = int((now - due).total_seconds() / 3600)
                overdue_str = f"{overdue_hours}h" if overdue_hours > 0 else "recently"
                report += f"- [OVERDUE by {overdue_str}] **{task['what']}**\n"
                if task.get('who'):
                    report += f"  截止: {due.strftime('%m-%d %H:%M')}, 相关人: {task['who']}\n"
    else:
        report += """## [URGENT] Overdue Tasks

[OK] No overdue tasks

"""

    # 分类待办任务：无时间 vs 有时间
    urgent_tasks = []  # 无时间的（立即启动）
    today_tasks = []    # 今天的任务
    future_tasks = []   # 未来的任务

    for task in pending:
        due_str = task.get('when_due')
        if not due_str:
            urgent_tasks.append(task)
        else:
            due = date_parser.isoparse(due_str).astimezone(tz)
            due_date = due.date()

            if due_date == now.date():
                today_tasks.append((task, due))
            else:
                future_tasks.append((task, due))

    # 立即启动任务
    if urgent_tasks:
        report += """## [ASAP] 立即启动任务

"""
        for task in urgent_tasks:
            priority_icon = "[HIGH]" if task.get('priority') == 'high' else "[NORMAL]"
            report += f"{priority_icon} **{task['what']}**\n"
            if task.get('who'):
                report += f"  相关人: {task['who']}\n"
        report += "\n"

    # 今天的任务
    if today_tasks:
        report += f"""## Today's Tasks ({len(today_tasks)} items)

"""
        # 按时间排序
        today_tasks.sort(key=lambda x: x[1])

        for task, due in today_tasks:
            priority_icon = "[HIGH]" if task.get('priority') == 'high' else "[NORMAL]"
            report += f"{priority_icon} **{due.strftime('%H:%M')}** - {task['what']}\n"
            if task.get('who'):
                report += f"  相关人: {task['who']}\n"
        report += "\n"

    # 未来任务
    if future_tasks:
        report += f"""## Upcoming Tasks ({len(future_tasks)} items)

"""
        # 按时间排序
        future_tasks.sort(key=lambda x: x[1])

        for task, due in future_tasks:
            priority_icon = "[HIGH]" if task.get('priority') == 'high' else "[NORMAL]"
            date_str = due.strftime('%m-%d')
            time_str = due.strftime('%H:%M')
            report += f"{priority_icon} **{date_str} {time_str}** - {task['what']}\n"
            if task.get('who'):
                report += f"  相关人: {task['who']}\n"
        report += "\n"

    # 如果没有任务
    if not urgent_tasks and not today_tasks and not future_tasks:
        report += "## All Tasks\n\n[OK] No pending tasks\n\n"

    # 今日已完成
    report += f"""
## Completed Today ({len(completed)} items)

"""
    if completed:
        for task in completed:
            completed_at_str = task.get('completed_at')
            if completed_at_str:
                completed_at = date_parser.isoparse(completed_at_str).astimezone(tz)
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
