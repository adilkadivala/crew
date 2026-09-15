"""
LangGraph crew pipeline (P07):

  triage → research → draft → END

Fixed order on purpose — easy to demo and debug.
"""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from agents.draft import run_draft
from agents.research import run_research
from agents.triage import run_triage


class CrewState(TypedDict, total=False):
    ticket: str
    triage: dict
    research: dict
    draft: str
    citations: list


def _node_triage(state: CrewState) -> CrewState:
    print("[Crew] triage…")
    triage = run_triage(state["ticket"])
    return {"triage": triage}


def _node_research(state: CrewState) -> CrewState:
    print("[Crew] research (via MCP search_docs)…")
    research = run_research(state["ticket"], state.get("triage") or {})
    return {
        "research": research,
        "citations": research.get("citations") or [],
    }


def _node_draft(state: CrewState) -> CrewState:
    print("[Crew] draft…")
    draft = run_draft(
        state["ticket"],
        state.get("triage") or {},
        state.get("research") or {},
    )
    return {"draft": draft}


def build_graph():
    graph = StateGraph(CrewState)
    graph.add_node("triage", _node_triage)
    graph.add_node("research", _node_research)
    graph.add_node("draft", _node_draft)
    graph.set_entry_point("triage")
    graph.add_edge("triage", "research")
    graph.add_edge("research", "draft")
    graph.add_edge("draft", END)
    return graph.compile()


_APP = None


def run_crew(ticket: str) -> CrewState:
    """Run the full multi-agent pipeline on one ticket."""
    global _APP
    if _APP is None:
        _APP = build_graph()
    return _APP.invoke({"ticket": ticket})
