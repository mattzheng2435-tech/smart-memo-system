# GitHub Actions 配置指南

## 概述
配置 GitHub Actions 实现每天早上 09:30 自动发送每日报告到你的工作邮箱。

---

## 步骤 1: 推送代码到 GitHub

### 1.1 创建 GitHub 仓库（如果还没有）

```bash
cd C:\Users\matt\smart-memo-system
git init
git add .
git commit -m "Initial commit: Smart Memo System"
```

### 1.2 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名称：`smart-memo-system`
3. 设为 **Private**（私有）或 **Public**（公开）都可以
4. **不要**勾选任何初始化选项（README、.gitignore、license）
5. 点击 **Create repository**

### 1.3 推送代码

```bash
git remote add origin https://github.com/你的用户名/smart-memo-system.git
git branch -M main
git push -u origin main
```

---

## 步骤 2: 配置 GitHub Secrets

### 2.1 进入仓库设置

1. 在 GitHub 仓库页面，点击 **Settings**
2. 左侧菜单点击 **Secrets and variables** → **Actions**
3. 点击 **New repository secret**

### 2.2 添加以下 Secrets（逐个添加）

点击 **New repository secret**，逐个添加以下内容：

| Name | Secret |
|------|--------|
| `DATABASE_URL` | `postgresql://postgres:Zyz0201afq!@db.lfhbowwktzoaeznfvxky.supabase.co:5432/postgres` |
| `EMAIL_ADDRESS` | `zhengyuanzhe@ribaotechnology.com` |
| `EMAIL_PASSWORD` | `Zyz0201afq!` |
| `SMTP_SERVER` | `smtp.qiye.163.com` |
| `SMTP_PORT` | `465` |
| `WORK_EMAIL` | `zhengyuanzhe@ribaotechnology.com` |

**注意**：
- Name 区分大小写
- 每次添加后点击 **Add secret**
- 添加完后会显示在列表中

---

## 步骤 3: 手动测试工作流

### 3.1 手动触发测试

1. 在 GitHub 仓库页面，点击 **Actions** 标签
2. 左侧会看到 "每日早报" 工作流
3. 点击右侧的 **Run workflow** 按钮
4. 选择分支（通常是 main），点击绿色的 **Run workflow** 按钮

### 3.2 查看运行日志

1. 工作流运行后，点击运行记录
2. 查看每个步骤的日志
3. 如果失败，查看错误信息

---

## 步骤 4: 验证成功

### 成功的标志

✅ 工作流运行成功（绿色对勾）
✅ 在你的邮箱收到测试邮件
✅ 邮件标题格式：`[Daily Report] 2026-01-22`

### 每日自动发送

- **时间**：每天早上 09:30（北京时间）
- **频率**：每天一次
- **内容**：今日待办、逾期任务、已完成任务

---

## 常见问题

### Q: 工作流运行失败？

**A**: 检查以下几点：
1. Secrets 是否正确配置（Settings → Secrets and variables → Actions）
2. 查看运行日志，找到具体的错误信息
3. 确认 `.github/workflows/daily-report.yml` 文件存在

### Q: 没有收到邮件？

**A**:
1. 检查垃圾邮件文件夹
2. 确认邮箱密码正确
3. 检查 SMTP 服务器和端口配置
4. 查看工作流日志

### Q: 想修改发送时间？

**A**: 编辑 `.github/workflows/daily-report.yml`，修改 cron 表达式：
```
# 早上 08:00 = UTC 00:00
cron: '0 0 * * *'
# 早上 10:00 = UTC 02:00
cron: '0 2 * * *'
# 晚上 22:00 = UTC 14:00
cron: '0 14 * * *'
```

---

## 完成后

Railway 部署和 GitHub Actions 配置完成后，你的智能备忘录系统将完全自动化运行！

✅ **Railway**: MCP Server 24/7 在云端运行
✅ **GitHub Actions**: 每天早上 09:30 发送邮件报告

你现在可以在 Claude Code 中随时使用：
```
"提醒我明天给Paul发邮件"
"我今天有哪些待办"
```

每天早上会自动收到邮件报告！

---

需要帮助配置或遇到问题，随时告诉我！
