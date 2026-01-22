#!/usr/bin/env python3
"""
本地发送每日报告邮件
"""
import sys
import os

# 添加 email_client 路径
email_client_path = r'C:\Users\matt\email_client'
sys.path.insert(0, email_client_path)

from email_client import EmailClient
from datetime import datetime

def send_local_report():
    """本地发送报告"""
    print("[INFO] Reading daily report...")

    try:
        with open("daily_report.md", "r", encoding="utf-8") as f:
            report_body = f.read()
    except FileNotFoundError:
        print("[ERROR] daily_report.md not found")
        print("[INFO] Please generate the report first")
        return False

    print("[INFO] Sending email via local SMTP...")

    client = EmailClient()
    work_email = "zhengyuanzhe@ribaotechnology.com"
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

        return success

    finally:
        client.disconnect()

if __name__ == "__main__":
    send_local_report()
