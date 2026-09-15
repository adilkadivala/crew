"""
Research agent — answers using company docs via MCP search_docs.

P05: citations (source filenames)
P04: retrieval goes through MCP, not a direct rag import here
"""

from __future__ import annotations

import ast
import json

from langchain.messages import HumanMessage, SystemMessage

from llm import get_model
from mcp_client import call_mcp_tool

SYSTEM = """
You are the research agent for Acme Support.
You receive a customer ticket, a triage summary, and retrieved doc snippets.
Write a short factual answer for the support team.
Rules:
- Use ONLY the provided snippets for policy facts.
- End with a Citations section listing source filenames like: - refund-policy.md
- If snippets are weak, say what is missing.
Keep it under 180 words.
"""


def _parse_hits(raw: str) -> list:
    """Turn MCP tool output into a list of hit dicts."""
    text = (raw or "").strip()
    if not text:
        return []
    for parser in (json.loads, ast.literal_eval):
        try:
            data = parser(text)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return [data]
        except Exception:
            continue
    return [{"text": text, "source": "unknown", "score": 0}]


def run_research(ticket: str, triage: dict) -> dict:
    """
    Call MCP search_docs, then ask the model to write an answer with citations.
    Returns {answer, citations, raw_hits}.
    """
    query = f"{triage.get('summary', '')} {ticket}"
    raw = call_mcp_tool("search_docs", {"query": query, "k": 3})
    hits = _parse_hits(raw)

    citations: list[str] = []
    snippet_lines: list[str] = []
    for hit in hits:
        if not isinstance(hit, dict):
            snippet_lines.append(str(hit))
            continue
        source = str(hit.get("source") or "unknown")
        if source not in citations:
            citations.append(source)
        snippet_lines.append(f"[{source}] {hit.get('text', '')}")

    snippets = "\n\n".join(snippet_lines) or "(no docs found)"

    model = get_model()
    prompt = (
        f"Ticket:\n{ticket}\n\n"
        f"Triage: {json.dumps(triage)}\n\n"
        f"Doc snippets:\n{snippets}\n"
    )
    response = model.invoke(
        [
            SystemMessage(content=SYSTEM),
            HumanMessage(content=prompt),
        ]
    )
    content = response.content
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    answer = str(content).strip()

    if citations and "citation" not in answer.lower():
        answer += "\n\nCitations:\n" + "\n".join(f"- {c}" for c in citations)

    return {"answer": answer, "citations": citations, "raw_hits": hits}
