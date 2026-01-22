# 智能备忘录系统 (Smart Memo System)

一个基于 Claude Code + MCP Server + PostgreSQL 的智能备忘录系统，支持追问式创建、语义搜索和每日早报推送。

## 功能特性

- ✅ **追问式创建** - 自动补全缺失的任务信息
- 🧠 **智能推断** - 从自然语言中提取时间和人名
- 🔍 **语义搜索** - 支持"给Paul的任务"这类模糊查询
- 📧 **每日早报** - 每天 09:30 自动发送到手机邮箱
- 🎯 **模糊完成** - "把那个任务划掉"无需ID
- 🔄 **批量清算** - 快速清理已完成任务

## 技术架构

```
Claude Code (Skill Layer)
         ↓
MCP Protocol
         ↓
MCP Server (Railway Cloud)
         ↓
Supabase PostgreSQL (Cloud)
         ↓
GitHub Actions (Scheduled)
         ↓
Email to Phone (Daily Report)
```

## 快速开始

### 1. 创建 Supabase 项目

1. 访问 https://supabase.com 注册并创建项目
2. 在 SQL Editor 中执行 `supabase/schema.sql` 建表
3. 获取项目凭证并填写到 `supabase/config.py`:

```bash
cd supabase
cp config_template.py config.py
# 编辑 config.py 填写凭证
```

**重要**: 使用端口 **5432** (直连) 而非 6543 (池化)

### 2. 测试数据库连接

```bash
python scripts/init_db.py
```

预期输出:
```
✅ 数据库连接成功！
📊 PostgreSQL 版本: PostgreSQL 15.x...
```

### 3. 部署 MCP Server 到 Railway

```bash
# 安装 Railway CLI
npm install -g railway

# 登录
railway login

# 创建项目
railway new

# 设置环境变量
railway variables set DATABASE_URL="postgresql://..."
railway variables set SUPABASE_URL="https://..."
railway variables set SUPABASE_KEY="..."

# 部署
railway up
```

### 4. 配置 GitHub Actions 自动化

在 GitHub 仓库设置中添加 Secrets:

```bash
# 在仓库 Settings → Secrets and variables → Actions
DATABASE_URL          # Supabase 数据库连接串
EMAIL_ADDRESS         # 你的邮箱
EMAIL_PASSWORD        # 邮箱密码/应用专用密码
SMTP_SERVER           # SMTP 服务器
SMTP_PORT             # SMTP 端口 (465)
WORK_EMAIL            # 接收早报的邮箱
```

### 5. 测试每日报告

```bash
# 手动触发 GitHub Actions
gh workflow run daily-report.yml

# 或本地测试
python scripts/daily_report.py
python scripts/send_report_via_email.py
```

## 使用方法

### 在 Claude Code 中使用

现在你可以直接用自然语言管理备忘录：

```
# 创建任务
"提醒我明天给Paul发邮件关于Magner项目"

# 查看待办
"我今天有哪些待办"

# 完成任务
"完成了给Paul发邮件那个任务"

# 搜索任务
"所有关于Magner的任务"

# 批量清算
"清算已完成的任务"
```

### 每日早报

每天早上 09:30，你会收到一封邮件，包含：
- 🔴 逾期任务
- 📋 今日待办
- ✅ 今日已完成

## 项目结构

```
smart-memo-system/
├── .github/workflows/
│   └── daily-report.yml          # 定时任务
├── mcp-server/                   # MCP Server
│   ├── server.py                 # 入口
│   ├── database/                 # 数据库层
│   ├── tools/                    # 工具实现
│   ├── requirements.txt
│   ├── Dockerfile
│   └── railway.json
├── scripts/                      # 自动化脚本
│   ├── init_db.py                # 数据库初始化
│   ├── daily_report.py           # 生成报告
│   └── send_report_via_email.py  # 发送邮件
├── supabase/                     # Supabase 配置
│   ├── schema.sql                # 建表脚本
│   └── config_template.py
└── README.md
```

## 配置说明

### Supabase 配置

```python
# supabase/config.py
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
DATABASE_URL = "postgresql://postgres:pwd@db.xxx.supabase.co:5432/postgres"
```

### Railway 环境变量

```bash
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=your-anon-key
```

### GitHub Secrets

```bash
DATABASE_URL          # 同上
EMAIL_ADDRESS         # zhengyuanzhe@ribaotechnology.com
EMAIL_PASSWORD        # 邮箱密码
SMTP_SERVER           # smtp.qiye.163.com
SMTP_PORT             # 465
WORK_EMAIL            # zhengyuanzhe@ribaotechnology.com
```

## 故障排除

### 数据库连接失败

**问题**: `asyncpg.exceptions.ConnectionDoesNotExistError`

**解决**: 确保使用端口 5432 而非 6543

### MCP Server 无法启动

**问题**: `ModuleNotFoundError: No module named 'mcp'`

**解决**:
```bash
pip install mcp
```

### 邮件发送失败

**问题**: SMTP 认证失败

**解决**: 使用应用专用密码而非账号密码

### 每日报告未发送

**问题**: GitHub Actions 未触发

**解决**:
1. 检查 cron 时区 (UTC 01:30 = CST 09:30)
2. 手动触发: `gh workflow run daily-report.yml`
3. 查看日志: `gh run view [run-id] --log`

## 下一步

- [ ] 创建 Supabase 项目并建表
- [ ] 配置 supabase/config.py
- [ ] 测试数据库连接
- [ ] 部署到 Railway
- [ ] 配置 GitHub Actions
- [ ] 测试每日报告
- [ ] 在 Claude Code 中测试对话

## 许可证

MIT License
