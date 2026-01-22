#!/usr/bin/env python3
"""
发送每日报告邮件 - GitHub Actions 版本
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_daily_report():
    """生成并发送每日报告"""
    print("[INFO] Sending daily report...")

    # 从环境变量获取配置
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    work_email = os.getenv("WORK_EMAIL")

    # 验证环境变量
    if not all([smtp_server, smtp_port, email_address, email_password, work_email]):
        print("[ERROR] Missing environment variables")
        print("[INFO] Required: SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, WORK_EMAIL")
        return False

    # 读取报告文件
    try:
        with open("daily_report.md", "r", encoding="utf-8") as f:
            report_body = f.read()
    except FileNotFoundError:
        print("[ERROR] daily_report.md not found")
        print("[TIP] Run generate_daily_report.py first")
        return False

    # 创建邮件
    today = datetime.now().strftime('%Y-%m-%d')
    subject = f"[Daily Report] {today}"

    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = work_email
    msg['Subject'] = subject

    msg.attach(MIMEText(report_body, 'plain'))

    # 发送邮件
    try:
        print(f"[INFO] Connecting to {smtp_server}:{smtp_port}")
        # 尝试使用 SMTP_SSL
        try:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
            print("[INFO] Using SMTP_SSL")
        except Exception as ssl_error:
            print(f"[WARN] SMTP_SSL failed: {ssl_error}")
            print("[INFO] Trying SMTP with STARTTLS...")
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            server.starttls()

        server.login(email_address, email_password)
        server.send_message(msg)
        server.quit()
        print(f"[OK] Daily report sent to: {work_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        print(f"[ERROR] Server: {smtp_server}:{smtp_port}")
        return False

if __name__ == "__main__":
    success = send_daily_report()
    exit(0 if success else 1)
