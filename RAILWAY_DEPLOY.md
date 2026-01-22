# Railway 部署指南

## 步骤 1: 登录 Railway

1. 打开浏览器，访问：https://railway.app
2. 点击右上角 **Login** 登录或注册
3. 登录后，在终端执行：
   ```bash
   railway login
   ```
   会打开浏览器让你确认登录

## 步骤 2: 创建新项目

登录后，在 smart-memo-system 目录执行：

```bash
cd C:\Users\matt\smart-memo-system
railway init
```

这会创建一个 `railway.toml` 文件。

## 步骤 3: 部署 MCP Server

```bash
cd mcp-server
railway up
```

Railway 会自动：
- 检测 Dockerfile
- 构建镜像
- 部署服务
- 分配域名

## 步骤 4: 设置环境变量

部署后，在 Railway 项目页面：

1. 点击你的项目
2. 选择 **mcp-server** 服务
3. 点击 **Variables** 标签
4. 添加以下环境变量：

```
DATABASE_URL = postgresql://postgres:Zyz0201afq!@db.lfhbowwktzoaeznfvxky.supabase.co:5432/postgres
SUPABASE_URL = https://lfhbowwktzoaeznfvxky.supabase.co
SUPABASE_KEY = sb_publishable_lV-31rITpkrBfMBKzYca6Q_I25B43HZ
```

5. 点击 **Deploy** 触发重新部署

## 步骤 5: 获取服务 URL

部署完成后，Railway 会分配一个公网 URL，格式类似：
```
https://your-service.railway.app
```

记录这个 URL，后续可能需要。

---

## 如何验证部署成功？

在 Railway 项目页面，你应该看到：
- ✅ 服务状态为 **Running**
- ✅ 有一个公网 URL
- ✅ 日志中没有错误

你可以在 **Logs** 标签查看部署日志。

---

## 完成后告诉我

Railway 部署完成后，告诉我，我会继续帮你配置 GitHub Actions。
