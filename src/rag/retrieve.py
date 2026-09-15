"""
Retrieve top-k doc chunks for a query (with citations).

Uses simple keyword overlap so it works offline without embeddings.
Citations always include the source filename.

Run:
  PYTHONPATH=src python -m rag.retrieve "refund policy"
"""

from __future__ import annotations

import re
import sys

from rag.ingest import load_chunks


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def retrieve(query: str, k: int = 3) -> list[dict]:
    """
    Return up to k chunks:
      [{"text": "...", "source": "refund-policy.md", "score": 0.42}, ...]
    """
    chunks = load_chunks()
    q = _tokens(query)
    if not q:
        return []

    scored = []
    for chunk in chunks:
        c = _tokens(chunk["text"])
        overlap = len(q & c)
        if overlap == 0:
            continue
        score = overlap / max(len(q), 1)
        scored.append(
            {
                "text": chunk["text"],
                "source": chunk["source"],
                "score": round(score, 3),
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "refund policy"
    hits = retrieve(query)
    print(f"Query: {query!r}\n")
    if not hits:
        print("No hits.")
    for i, hit in enumerate(hits, 1):
        print(f"[{i}] source={hit['source']} score={hit['score']}")
        print(hit["text"][:300], "\n")
