from __future__ import annotations

import json

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

from llm import BOSS_PROMPT, RESEARCHER_PROMPT, WRITER_PROMPT, model
from rag.ingest import ROOT, get_file_text, ingest_path
from rag.retrieve import retrieve

# preload local docs/ so refund/shipping questions work immediately
try:
    docs = ROOT / "docs"
    if docs.exists():
        ingest_path(str(docs))
except Exception as e:
    print(f"[rag] docs preload skipped: {e}")


def last_message(result) -> str:
    """Pull plain text from an agent result."""
    messages = result.get("messages") or []
    if not messages:
        return str(result)
    content = messages[-1].content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        bits = []
        for part in content:
            if isinstance(part, str):
                bits.append(part)
            elif isinstance(part, dict) and part.get("text"):
                bits.append(str(part["text"]))
        return "".join(bits)
    return str(content)


def run_agent(system_prompt: str, tools: list, user_text: str) -> str:
    """Create one agent, ask one question, return the answer."""
    agent = create_agent(
        model=model,
        system_prompt=system_prompt,
        tools=tools,
        checkpointer=InMemorySaver(),
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_text}]},
        config={"configurable": {"thread_id": str(uuid7())}},
    )
    return last_message(result)


# ========== tools (plain Python the agents can call) ==========

@tool
def ingest_file(path: str) -> str:
    """Read a file/folder path and save chunks. Supports .md .txt .pdf."""
    print(f"[tool] ingest_file → {path}")
    return json.dumps(ingest_path(path))


@tool
def search_docs(query: str) -> str:
    """Search ingested chunks by keywords."""
    print(f"[tool] search_docs → {query}")
    return json.dumps(retrieve(query, k=5))


@tool
def get_file_text_tool(name: str) -> str:
    """Get lots of text from one ingested file (for summaries)."""
    print(f"[tool] get_file_text → {name}")
    return get_file_text(name)


# ========== boss spawns sub-agents with these tools ==========

@tool
def ask_researcher(query: str) -> str:
    """Spawn a research sub-agent to search or summarize ingested files."""
    print(f"[boss] spawn researcher → {query}")
    answer = run_agent(
        RESEARCHER_PROMPT,
        tools=[search_docs, get_file_text_tool],
        user_text=query,
    )
    print("[boss] researcher done")
    return answer


@tool
def ask_writer(brief: str) -> str:
    """Spawn a writer sub-agent to write content (email, FAQ, post...)."""
    print(f"[boss] spawn writer → {brief[:60]}...")
    answer = run_agent(
        WRITER_PROMPT,
        tools=[],
        user_text=brief,
    )
    print("[boss] writer done")
    return answer


# ========== entry used by main.py ==========

def run_main_agent(query: str) -> str:
    """User talks only to the boss."""
    return run_agent(
        BOSS_PROMPT,
        tools=[ingest_file, ask_researcher, ask_writer],
        user_text=query,
    )
