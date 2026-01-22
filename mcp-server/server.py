#!/usr/bin/env python3
"""
智能备忘录 MCP Server
提供备忘录 CRUD、语义搜索、批量操作等工具
"""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

from .database import get_pool
from .tools import create_memo, search_memos, complete_memo, list_pending, batch_clear

# 创建 MCP Server 实例
app = Server("smart-memo-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="create_memo",
            description="创建备忘录，支持追问式补全缺失字段(what/when/who)。",
            inputSchema={
                "type": "object",
                "properties": {
                    "what": {
                        "type": "string",
                        "description": "任务内容（必需）"
                    },
                    "when": {
                        "type": "string",
                        "description": "截止时间 (可选)。支持 ISO 8601 格式或自然语言，例如: '2026-01-23T10:00:00', 'tomorrow 3pm', '下周五', '明天上午10点'"
                    },
                    "who": {
                        "type": "string",
                        "description": "相关人员 (可选)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "normal", "low"],
                        "description": "优先级 (默认: normal)",
                        "default": "normal"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "标签数组 (可选)"
                    },
                    "context": {
                        "type": "string",
                        "description": "补充上下文 (可选)"
                    }
                },
                "required": ["what"]
            }
        ),
        Tool(
            name="search_memos",
            description="模糊语义搜索备忘录，支持自然语言查询。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询（必需）。支持自然语言，例如: 'Paul Magner', '关于招标的'"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "all"],
                        "description": "过滤状态 (默认: pending)",
                        "default": "pending"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制 (默认: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="complete_memo",
            description="完成指定的备忘录。支持 ID 或模糊匹配。",
            inputSchema={
                "type": "object",
                "properties": {
                    "memo_id": {
                        "type": "string",
                        "description": "备忘录 ID 或模糊匹配文本（必需）。可以是完整 UUID，或任务描述如 '给老板做演示'"
                    }
                },
                "required": ["memo_id"]
            }
        ),
        Tool(
            name="list_pending",
            description="列出当前待办事项。",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制 (默认: 20)",
                        "default": 20
                    },
                    "category": {
                        "type": "string",
                        "description": "过滤分类 (可选)。例如: 'work', 'personal'"
                    }
                }
            }
        ),
        Tool(
            name="batch_clear",
            description="批量清算已完成或符合条件的备忘录。",
            inputSchema={
                "type": "object",
                "properties": {
                    "criteria": {
                        "type": "string",
                        "description": "匹配条件（必需）。例如: '已完成', '逾期', '低优先级', 或包含的关键词"
                    },
                    "preview_only": {
                        "type": "boolean",
                        "description": "预览模式 (默认: true)。true=仅预览不执行, false=实际执行",
                        "default": true
                    }
                },
                "required": ["criteria"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    处理工具调用

    Args:
        name: 工具名称
        arguments: 工具参数

    Returns:
        list[TextContent]: 返回结果
    """
    pool = await get_pool()

    # 工具处理器映射
    handlers = {
        "create_memo": create_memo.handle,
        "search_memos": search_memos.handle,
        "complete_memo": complete_memo.handle,
        "list_pending": list_pending.handle,
        "batch_clear": batch_clear.handle
    }

    if name not in handlers:
        return [TextContent(
            type="text",
            text=f"❌ 未知工具: {name}\n\n可用工具: {', '.join(handlers.keys())}"
        )]

    try:
        result = await handlers[name](pool, arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 执行工具 {name} 时出错: {str(e)}"
        )]


async def main():
    """启动 MCP 服务器"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
