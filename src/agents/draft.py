"""Draft agent — write a customer reply (never sends)."""

from __future__ import annotations

import json

from langchain.messages import HumanMessage, SystemMessage

from llm import get_model

SYSTEM = """
You are the draft agent for Acme Support.
Write a polite, clear customer email reply using the research notes.
Rules:
- Do not invent policies.
- Do not claim a refund was already issued.
- Keep it under 160 words.
- Sign off as: Acme Support
Return ONLY the email body text (no subject line unless useful).
"""


def run_draft(ticket: str, triage: dict, research: dict) -> str:
    """Return a customer-facing draft reply string."""
    model = get_model()
    prompt = (
        f"Ticket:\n{ticket}\n\n"
        f"Triage: {json.dumps(triage)}\n\n"
        f"Research notes:\n{research.get('answer', '')}\n"
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
    return str(content).strip()
