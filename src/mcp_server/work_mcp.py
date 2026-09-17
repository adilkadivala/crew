"""
Optional MCP server (advanced / P04).

Beginner path uses rag/ directly from main_agent.
This file exposes the same functions over MCP stdio.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp.server.mcpserver import MCPServer

from rag.ingest import get_file_text, ingest_path
from rag.retrieve import retrieve

mcp = MCPServer("crew")


@mcp.tool(description="Ingest a file or folder (.md .txt .pdf)")
def ingest_file(path: str) -> str:
    return json.dumps(ingest_path(path))


@mcp.tool(description="Search ingested chunks")
def search_docs(query: str, k: int = 5) -> str:
    return json.dumps(retrieve(query, k=k))


@mcp.tool(description="Get text from one ingested file for summaries")
def get_document_text(name_or_path: str) -> str:
    return get_file_text(name_or_path)


if __name__ == "__main__":
    mcp.run(transport="stdio")
