"""
Crew MCP CLIENT — talks to mcp_server/work_mcp.py over stdio.

Research agent uses call_mcp_tool("search_docs", ...) so tools
really go through MCP (P04), not a hidden direct import.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from mcp import StdioServerParameters
from mcp.client.client import Client

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent


def _server() -> StdioServerParameters:
    env = os.environ.copy()
    # Child process must import rag/ and mcp_server/
    env["PYTHONPATH"] = str(SRC) + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.work_mcp"],
        cwd=str(ROOT),
        env=env,
    )


def _text_from_result(result) -> str:
    """Normalize MCP CallToolResult into a plain string (often JSON)."""
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        # Some MCP servers wrap as {"result": "<json string>"}
        if isinstance(structured, dict) and "result" in structured and len(structured) == 1:
            return str(structured["result"])
        if isinstance(structured, (dict, list)):
            import json

            return json.dumps(structured)
        return str(structured)

    parts = []
    for block in result.content or []:
        text = getattr(block, "text", None)
        parts.append(text if text is not None else str(block))
    return "\n".join(parts) if parts else str(result)


async def _list_tools_async() -> list[str]:
    async with Client(_server()) as client:
        listed = await client.list_tools()
        return [t.name for t in listed.tools]


async def _call_tool_async(name: str, arguments: dict) -> str:
    async with Client(_server()) as client:
        result = await client.call_tool(name, arguments or {})
        return _text_from_result(result)


def list_tool_names() -> list[str]:
    return asyncio.run(_list_tools_async())


def call_mcp_tool(name: str, arguments: dict | None = None) -> str:
    """Call one MCP tool and return plain text / stringified JSON."""
    return asyncio.run(_call_tool_async(name, arguments or {}))


if __name__ == "__main__":
    print("Tools:", list_tool_names())
    print()
    print(call_mcp_tool("search_docs", {"query": "refund", "k": 2}))
