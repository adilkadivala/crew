"""Triage agent — classify the support ticket (no tools)."""

from __future__ import annotations

import json
import re

from langchain.messages import HumanMessage, SystemMessage

from llm import get_model

SYSTEM = """
You are the triage agent for Acme Support.
Read the customer ticket and return ONLY valid JSON with keys:
  category: one of billing | shipping | pricing | technical | other
  urgency: one of low | medium | high
  summary: one short sentence
No markdown. No extra text.
"""


def _parse_json(text: str) -> dict:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return {
        "category": "other",
        "urgency": "medium",
        "summary": text[:200] or "Could not triage",
    }


def run_triage(ticket: str) -> dict:
    """Return {category, urgency, summary}."""
    model = get_model()
    response = model.invoke(
        [
            SystemMessage(content=SYSTEM),
            HumanMessage(content=ticket),
        ]
    )
    content = response.content
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return _parse_json(str(content))
