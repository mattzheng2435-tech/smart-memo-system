#!/usr/bin/env python3
"""
快速设置脚本
帮助用户初始化项目
"""

import os
import sys


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          智能备忘录系统 - 快速设置向导                      ║
╚══════════════════════════════════════════════════════════════╝

本指南将帮助你完成以下步骤：
  1. 配置 Supabase
  2. 测试数据库连接
  3. 部署 MCP Server
  4. 配置 GitHub Actions

""")
    input("按 Enter 继续...")

    print("\n" + "="*60)
    print("步骤 1: 配置 Supabase")
    print("="*60)

    print("""
1. 访问 https://supabase.com
2. 创建新项目（免费）
3. 在 SQL Editor 中执行以下建表脚本:
   file: supabase/schema.sql

4. 获取项目凭证:
   - Project URL
   - Anon Key
   - Database Connection String (端口 5432!)

5. 配置文件:""")

    print("""
   cd supabase
   cp config_template.py config.py
   # 编辑 config.py 填写凭证
""")

    input("\n配置完成后按 Enter...")

    print("\n" + "="*60)
    print("步骤 2: 测试数据库连接")
    print("="*60)

    print("\n运行测试脚本:")
    print("  python scripts/init_db.py")

    choice = input("\n是否现在测试数据库连接？(y/n): ")
    if choice.lower() == 'y':
        os.system("python scripts/init_db.py")

    print("\n" + "="*60)
    print("步骤 3: 部署 MCP Server 到 Railway")
    print("="*60)

    print("""
1. 安装 Railway CLI:
   npm install -g railway

2. 登录并创建项目:
   railway login
   cd mcp-server
   railway new

3. 设置环境变量:
   railway variables set DATABASE_URL="你的数据库连接串"
   railway variables set SUPABASE_URL="你的Supabase URL"
   railway variables set SUPABASE_KEY="你的Supabase Key"

4. 部署:
   railway up
""")

    input("\n部署完成后按 Enter...")

    print("\n" + "="*60)
    print("步骤 4: 配置 GitHub Actions")
    print("="*60)

    print("""
在你的 GitHub 仓库中添加 Secrets:

Settings → Secrets and variables → Actions → New repository secret

需要添加的 Secrets:
  - DATABASE_URL          (Supabase 数据库连接串)
  - EMAIL_ADDRESS         (zhengyuanzhe@ribaotechnology.com)
  - EMAIL_PASSWORD        (邮箱密码/应用专用密码)
  - SMTP_SERVER           (smtp.qiye.163.com)
  - SMTP_PORT             (465)
  - WORK_EMAIL            (zhengyuanzhe@ribaotechnology.com)

然后手动触发工作流测试:
  gh workflow run daily-report.yml
""")

    print("\n" + "="*60)
    print("✅ 设置完成！")
    print("="*60)

    print("""
你现在可以在 Claude Code 中使用智能备忘录了！

试试说:
  - "提醒我明天给Paul发邮件"
  - "我今天有哪些待办"
  - "完成了给Paul发邮件那个任务"

每天早上 09:30，你会收到一封每日早报邮件。

文档: README.md
问题反馈: 检查 README.md 中的故障排除部分
""")


if __name__ == "__main__":
    main()
