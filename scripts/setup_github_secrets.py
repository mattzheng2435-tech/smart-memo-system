#!/usr/bin/env python3
"""
GitHub Secrets 配置指南
"""

print("""
=======================================================
        GitHub Secrets 配置指南 - 智能备忘录系统
=======================================================

代码正在推送到 GitHub...
同时，我准备告诉你如何配置 Secrets。

=======================================================

第一步：进入仓库设置
------------------------

1. 在 Chrome 浏览器中，你刚才打开的 GitHub 页面
   地址：https://github.com/mattzheng2435-tech/smart-memo-system

2. 点击页面顶部的 "Settings" 标签

=======================================================

第二步：添加 Secrets
----------------------

1. 在左侧菜单找到 "Secrets and variables"
   点击 "Actions"

2. 点击右侧的 "New repository secret" 按钮

3. 需要添加以下 6 个 Secrets（逐个添加）：

   -------------------------------------------
   第1个 Secret:
   Name:  DATABASE_URL
   Value: postgresql://postgres:Zyz0201afq!@db.lfhbowwktzoaeznfvxky.supabase.co:5432/postgres
   -------------------------------------------

   -------------------------------------------
   第2个 Secret:
   Name:  EMAIL_ADDRESS
   Value: zhengyuanzhe@ribaotechnology.com
   -------------------------------------------

   -------------------------------------------
   第3个 Secret:
   Name:  EMAIL_PASSWORD
   Value: Zyz0201afq!
   -------------------------------------------

   -------------------------------------------
   第4个 Secret:
   Name:  SMTP_SERVER
   Value: smtp.qiye.163.com
   -------------------------------------------

   -------------------------------------------
   第5个 Secret:
   Name:  SMTP_PORT
   Value: 465
   -------------------------------------------

   -------------------------------------------
   第6个 Secret:
   Name:  WORK_EMAIL
   Value: zhengyuanzhe@ribaotechnology.com
   -------------------------------------------

每个Secret添加后，点击 "Add secret" 保存。

=======================================================

第三步：验证配置
--------------

所有 Secrets 添加完成后，你应该能看到类似这样的列表：

[OK] DATABASE_URL
[OK] EMAIL_ADDRESS
[OK] EMAIL_PASSWORD
[OK] SMTP_SERVER
[OK] SMTP_PORT
[OK] WORK_EMAIL

=======================================================

完成后告诉我，我会帮你测试工作流！
""")

print("\n请完成上述步骤，然后告诉我：\"配置完成了\"")
