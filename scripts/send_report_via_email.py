#!/usr/bin/env python3
"""
通过邮件发送每日报告
使用现有的 email_client.py 发送邮件
"""

import asyncio
import sys
import os

# 添加 email_client 路径
email_client_path = r'C:\Users\matt\email_client'
sys.path.insert(0, email_client_path)

from email_client import EmailClient
from scripts.daily_report import generate_daily_report


async def send_daily_report():
    """生成并发送每日报告"""
    print("📧 正在准备发送每日报告...")

    # 生成报告
    report = await generate_daily_report()

    # 读取报告文件
    report_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "daily_report.md"
    )

    with open(report_file, "r", encoding="utf-8") as f:
        report_body = f.read()

    # 发送邮件
    client = EmailClient()

    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    subject = f"📅 每日早报 - {today}"

    # 从环境变量或配置读取接收邮箱
    # 默认发送到工作邮箱
    to_email = os.getenv("WORK_EMAIL", "zhengyuanzhe@ribaotechnology.com")

    try:
        success = client.send_email(
            to=to_email,
            subject=subject,
            body=report_body
        )

        if success:
            print(f"\n✅ 每日报告已成功发送到: {to_email}")
        else:
            print(f"\n❌ 邮件发送失败")
            sys.exit(1)

    finally:
        client.disconnect()


if __name__ == "__main__":
    asyncio.run(send_daily_report())
