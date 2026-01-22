#!/usr/bin/env python3
"""
Railway 部署自动化脚本
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """运行命令并显示输出"""
    print(f"\n[{description}]")
    print(f"命令: {cmd}")
    print("-" * 60)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("[ERROR]", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     Railway 自动部署 - 智能备忘录系统                  ║
╚══════════════════════════════════════════════════════════════╝

请按以下步骤操作：

STEP 1: 确认已登录
""")

    # 检查登录状态
    if run_command("railway status", "检查登录状态"):
        print("[OK] 已登录到 Railway")
    else:
        print("\n[INFO] 需要先登录")
        print("\n请在终端执行:")
        print("  railway login")
        print("\n这会打开浏览器让你确认登录。")
        print("\n登录完成后，按回车继续...")
        input()

    print("""
STEP 2: 初始化项目
""")

    os.chdir(r"C:\Users\matt\smart-memo-system")

    if run_command("railway init", "初始化Railway项目"):
        print("[OK] 项目初始化成功")
    else:
        print("[WARN] 可能已经初始化过了，继续...")

    print("""
STEP 3: 部署 MCP Server
""")

    os.chdir("mcp-server")

    if run_command("railway up", "部署到Railway"):
        print("[OK] 部署命令已执行")
    else:
        print("[ERROR] 部署失败")
        return False

    print("""
STEP 4: 设置环境变量
""")

    print("现在需要在 Railway 控制台设置环境变量。")
    print("\n我会生成设置命令，请复制到 Railway 中执行。")

    env_vars = {
        'DATABASE_URL': 'postgresql://postgres:Zyz0201afq!@db.lfhbowwktzoaeznfvxky.supabase.co:5432/postgres',
        'SUPABASE_URL': 'https://lfhbowwktzoaeznfvxky.supabase.co',
        'SUPABASE_KEY': 'sb_publishable_lV-31rITpkrBfMBKzYca6Q_I25B43HZ'
    }

    print("\n请在 Railway 项目页面执行以下命令：")
    print("=" * 60)

    for key, value in env_vars.items():
        print(f"railway variables set {key}=\"{value}\"")

    print("=" * 60)
    print("\n设置完成后，在 Railway 控制台点击 'Deploy' 重新部署。")
    print("\n完成后告诉我，我会帮你验证部署是否成功！")

if __name__ == "__main__":
    main()
