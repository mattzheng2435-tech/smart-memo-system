FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露健康检查端口
EXPOSE 8000

# 健康检查端点
RUN echo '#!/usr/bin/env python3\n\
from aiohttp import web\n\
async def health(request):\n\
    return web.json_response({"status": "healthy", "service": "smart-memo-mcp-server"})\n\
app = web.Application()\n\
app.router.add_get("/health", health)\n\
if __name__ == "__main__":\n\
    web.run_app(app, host="0.0.0.0", port=8000)\n\
' > /app/health_server.py && chmod +x /app/health_server.py

# 启动脚本
RUN echo '#!/bin/bash\n\
echo "Starting MCP Server..."\n\
# 启动健康检查服务器\n\
python /app/health_server.py &\n\
# 启动 MCP Server\n\
python -m mcp_server.server\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
