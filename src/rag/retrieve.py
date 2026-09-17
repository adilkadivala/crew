"""
Step 2 of RAG: search the chunks we saved.

Simple beginner version = keyword overlap (no embeddings).

Try:
  PYTHONPATH=src python -m rag.retrieve "refund policy"
"""

from __future__ import annotations

import re
import sys

from rag.ingest import load_chunks


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def retrieve(query: str, k: int = 5) -> list[dict]:
    """
    Find the best matching chunks for a query.
    Returns: [{"text": "...", "source": "...", "score": 0.5}, ...]
    """
    q = words(query)
    if not q:
        return []

    scored = []
    for chunk in load_chunks():
        overlap = len(q & words(chunk.get("text") or ""))
        if overlap == 0:
            continue
        scored.append(
            {
                "text": chunk["text"],
                "source": chunk["source"],
                "score": round(overlap / len(q), 3),
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "refund"
    hits = retrieve(query)
    print(f"Query: {query!r}\n")
    if not hits:
        print("No hits. Ingest a file first.")
    for i, h in enumerate(hits, 1):
        print(f"[{i}] {h['source']} (score={h['score']})")
        print(h["text"][:250], "\n")
