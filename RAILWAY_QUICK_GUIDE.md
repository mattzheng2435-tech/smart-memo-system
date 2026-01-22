# Railway 部署 - 快速指南

## 第一步：登录 Railway

在终端执行：
```bash
railway login
```
这会打开浏览器，点击 **Confirm** 确认登录。

---

## 第二步：初始化项目

登录后执行：
```bash
cd C:\Users\matt\smart-memo-system
railway init
```

---

## 第三步：部署 MCP Server

```bash
cd mcp-server
railway up
```

这会自动：
- 检测 Dockerfile
- 构建镜像
- 部署到云端
- 分配公网 URL

---

## 第四步：设置环境变量

部署完成后，在 Railway 项目页面：

1. 点击你的项目
2. 点击 **Variables** 标签
3. 点击 **New Variable** 添加以下变量：

```
DATABASE_URL = postgresql://postgres:Zyz0201afq!@db.lfhbowwktzoaeznfvxky.supabase.co:5432/postgres
```

```
SUPABASE_URL = https://lfhbowwktzoaeznfvxky.supabase.co
```

```
SUPABASE_KEY = sb_publishable_lV-31rITpkrBfMBKzYca6Q_I25B43HZ
```

4. 点击 **Deploy** 重新部署

---

## 第五步：验证成功

在 Railway 控制台：
- ✅ 服务状态为 **Running**（绿色）
- ✅ 有一个公网 URL（例如：`https://xxx.up.railway.app`）
- ✅ 日志中没有错误

---

## 完成后告诉我

Railway 部署完成后，告诉我：
1. 服务状态是否显示 "Running"？
2. 有没有分配公网 URL？

我会帮你验证配置，然后继续配置 GitHub Actions。
