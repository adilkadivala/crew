"""
Crew MCP SERVER — exposes company-doc search (and a mock draft tool).

This is the P04 piece: tools over MCP stdio.

Run alone (waits for a client):
  PYTHONPATH=src python -m mcp_server.work_mcp
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow "from rag..." when launched as a child process
ROOT_SRC = Path(__file__).resolve().parents[1]
if str(ROOT_SRC) not in sys.path:
    sys.path.insert(0, str(ROOT_SRC))

import json

from mcp.server.mcpserver import MCPServer

from rag.retrieve import retrieve

mcp = MCPServer("crew-work")


@mcp.tool(description="Search company docs. Returns JSON list of {text, source, score} for citations.")
def search_docs(query: str, k: int = 3) -> str:
    # Return JSON text so the client always gets a stable string
    return json.dumps(retrieve(query, k=k))


@mcp.tool(description="Save an email DRAFT only. Does NOT send.")
def create_draft(to: str, subject: str, body: str) -> str:
    return json.dumps(
        {
            "status": "draft_saved_not_sent",
            "to": to,
            "subject": subject,
            "body": body,
        }
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
