
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import StdioServerParameters
from mcp.client.client import Client

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent


def _server() -> StdioServerParameters:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.work_mcp"],
        cwd=str(ROOT),
        env=env,
    )


def _to_text(result) -> str:
    data = getattr(result, "structured_content", None)
    if isinstance(data, dict) and "result" in data and len(data) == 1:
        return str(data["result"])
    if isinstance(data, (dict, list)):
        return json.dumps(data)
    if data is not None:
        return str(data)
    parts = [getattr(b, "text", None) or str(b) for b in (result.content or [])]
    return "\n".join(parts)


async def _call(name: str, args: dict) -> str:
    async with Client(_server()) as client:
        return _to_text(await client.call_tool(name, args or {}))


def call_mcp_tool(name: str, arguments: dict | None = None) -> str:
    return asyncio.run(_call(name, arguments or {}))


if __name__ == "__main__":
    print(call_mcp_tool("search_docs", {"query": "refund", "k": 2}))
