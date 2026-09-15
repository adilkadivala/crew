"""
Load docs/*.md into simple text chunks with source names.

v1 uses keyword scoring (no embedding API required).
Run:
  PYTHONPATH=src python -m rag.ingest
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs"
DATA_DIR = ROOT / "data"
CHUNKS_PATH = DATA_DIR / "chunks.json"


def _chunk_markdown(text: str, source: str, max_chars: int = 500) -> list[dict]:
    """Split a markdown file into small chunks with source metadata."""
    parts = re.split(r"\n\s*\n", text.strip())
    chunks: list[dict] = []
    buf = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(buf) + len(part) + 2 <= max_chars:
            buf = f"{buf}\n\n{part}".strip() if buf else part
        else:
            if buf:
                chunks.append({"text": buf, "source": source})
            buf = part
    if buf:
        chunks.append({"text": buf, "source": source})
    return chunks


def ingest() -> list[dict]:
    """Read all markdown docs and write data/chunks.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    chunks: list[dict] = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        chunks.extend(_chunk_markdown(text, source=path.name))
    CHUNKS_PATH.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    print(f"[RAG] ingested {len(chunks)} chunks from {DOCS_DIR} → {CHUNKS_PATH}")
    return chunks


def load_chunks() -> list[dict]:
    """Load chunks from disk (ingest first if missing)."""
    if not CHUNKS_PATH.exists():
        return ingest()
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    ingest()
