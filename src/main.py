"""
Crew CLI — multi-agent support desk (P04 + P05 + P07).

Flow:
  ticket → triage → research(MCP+RAG) → draft → approve?

Run from crew/:
  PYTHONPATH=src python src/main.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
load_dotenv()

# Ensure src imports work when running as a file
SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from crew.graph import run_crew
from mcp_client import call_mcp_tool
from rag.ingest import ingest


SAMPLE = (
    "I was charged twice for March. "
    "What's your refund policy and can I get my money back?"
)


def _print_result(result: dict) -> None:
    triage = result.get("triage") or {}
    research = result.get("research") or {}
    draft = result.get("draft") or ""
    citations = result.get("citations") or research.get("citations") or []

    print("\n" + "=" * 60)
    print("1) TRIAGE")
    print("=" * 60)
    print(json.dumps(triage, indent=2))

    print("\n" + "=" * 60)
    print("2) RESEARCH (citations via MCP docs)")
    print("=" * 60)
    print(research.get("answer") or "(no answer)")
    if citations:
        print("\nSources:", ", ".join(citations))

    print("\n" + "=" * 60)
    print("3) DRAFT (not sent)")
    print("=" * 60)
    print(draft)


def _maybe_save_draft(draft: str) -> None:
    print("\nApprove saving this as an email draft? [yes/no]")
    try:
        choice = input("> ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nSkipped.")
        return
    if choice not in ("y", "yes"):
        print("Draft not saved.")
        return
    saved = call_mcp_tool(
        "create_draft",
        {
            "to": "customer@example.com",
            "subject": "Re: your support request",
            "body": draft,
        },
    )
    print("Saved via MCP:", saved)


def main() -> None:
    print("Crew — triage → research(RAG+MCP) → draft")
    print("Type a support ticket (or press Enter for a sample).")
    print("Type 'quit' to exit.\n")

    # Make sure docs are indexed
    ingest()

    while True:
        try:
            line = input("Ticket > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.lower() in ("q", "quit", "exit"):
            break
        ticket = line or SAMPLE
        if not line:
            print(f"(using sample) {SAMPLE}\n")

        try:
            result = run_crew(ticket)
        except Exception as e:
            print(f"[Error] crew failed: {e}")
            continue

        _print_result(result)
        _maybe_save_draft(result.get("draft") or "")
        print()


if __name__ == "__main__":
    main()
