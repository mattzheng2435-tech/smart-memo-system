#!/usr/bin/env python3
"""
发送每日报告邮件
"""
import sys
import os
from datetime import datetime

# 添加 email_client 路径
email_client_path = r'C:\Users\matt\email_client'
sys.path.insert(0, email_client_path)

try:
    from email_client import EmailClient
except ImportError:
    print("[ERROR] Cannot import email_client")
    print("[TIP] Make sure the path exists: C:\\Users\\matt\\email_client\\")
    sys.exit(1)

def send_daily_report():
    """生成并发送每日报告"""
    print("[INFO] Sending daily report...")

    # 读取报告文件
    try:
        with open("daily_report.md", "r", encoding="utf-8") as f:
            report_body = f.read()
    except FileNotFoundError:
        print("[ERROR] daily_report.md not found")
        print("[TIP] Run generate_daily_report.py first")
        sys.exit(1)

    # 发送邮件
    client = EmailClient()

    # 从环境变量获取配置
    work_email = os.getenv("WORK_EMAIL", "zhengyuanzhe@ribaotechnology.com")

    today = datetime.now().strftime('%Y-%m-%d')
    subject = f"[Daily Report] {today}"

    try:
        success = client.send_email(
            to=work_email,
            subject=subject,
            body=report_body
        )

        if success:
            print(f"[OK] Daily report sent to: {work_email}")
        else:
            print("[ERROR] Failed to send email")
            return False

    finally:
        client.disconnect()

    return True

if __name__ == "__main__":
    send_daily_report()
