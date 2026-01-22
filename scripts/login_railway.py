#!/usr/bin/env python3
"""
Railway CLI 登录 - 使用 Chrome 浏览器
"""

import subprocess
import sys
import os

print("""
╔══════════════════════════════════════════════════════════════╗
║           Railway CLI 登录指南 (Chrome)                     ║
╚══════════════════════════════════════════════════════════════╝

我将帮你打开 Chrome 浏览器并执行登录命令...

""")

# 设置浏览器为 Chrome
os.environ['BROWSER'] = 'start chrome'

print("[INFO] 正在打开 Chrome 浏览器...")
print("[INFO] 正在执行 railway login...")
print("-" * 60)

# 执行登录命令
try:
    result = subprocess.run(
        ['railway', 'login'],
        capture_output=False,
        timeout=60
    )
    print("\n[OK] 命令已执行!")
    print("\n[INFO] 请在 Chrome 浏览器中：")
    print("   1. 如果弹出 Railway 登录页面，登录你的账号")
    print("   2. 点击 'Confirm' 或 'Authorize' 按钮")
    print("   3. 等待授权完成")
    print("\n[INFO] 完成后在终端执行: railway whoami")
    print("       检查是否显示你的用户名")

except FileNotFoundError:
    print("\n[ERROR] railway 命令未找到")
    print("\n[INFO] 请先安装 Railway CLI:")
    print("   npm install -g @railway/cli")

except Exception as e:
    print(f"\n[ERROR] 执行失败: {e}")
    print("\n[TIP] 尝试手动执行: railway login")

if __name__ == "__main__":
    main()
