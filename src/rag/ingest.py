"""
Step 1 of RAG: turn a file into small text pieces (chunks).

Supports: .md  .txt  .pdf
Saves everything into: data/chunks.json

Try:
  PYTHONPATH=src python -m rag.ingest ~/some-file.pdf
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# crew/ folder (two levels up from this file)
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CHUNKS_FILE = DATA_DIR / "chunks.json"

OK_TYPES = {".md", ".txt", ".pdf", ".markdown"}


# ---------- helpers ----------

def make_chunks(text: str, source: str, size: int = 800) -> list[dict]:
    """Cut long text into small pieces. Each piece remembers its source file."""
    text = (text or "").strip()
    if not text:
        return []

    # split on blank lines first
    parts = re.split(r"\n\s*\n", text)
    chunks = []
    bucket = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # fits in current bucket?
        if len(bucket) + len(part) + 2 <= size:
            bucket = (bucket + "\n\n" + part).strip() if bucket else part
            continue

        # save old bucket
        if bucket:
            chunks.append({"text": bucket, "source": source})

        # part itself is huge → hard cut
        while len(part) > size:
            chunks.append({"text": part[:size], "source": source})
            part = part[size:]
        bucket = part

    if bucket:
        chunks.append({"text": bucket, "source": source})
    return chunks


def read_pdf(path: Path) -> str:
    """Pull text out of a PDF."""
    from pypdf import PdfReader

    pages = []
    for i, page in enumerate(PdfReader(str(path)).pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"--- page {i + 1} ---\n{text}")
    return "\n\n".join(pages)


def read_any_file(path: Path) -> str:
    """Read .md / .txt / .pdf into one big string."""
    if path.suffix.lower() == ".pdf":
        return read_pdf(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def list_files(path: Path) -> list[Path]:
    """If path is a file → [file]. If folder → all ok files inside."""
    if path.is_file():
        return [path]
    if path.is_dir():
        return [
            p
            for p in sorted(path.rglob("*"))
            if p.is_file() and p.suffix.lower() in OK_TYPES
        ]
    raise FileNotFoundError(f"Not found: {path}")


def load_chunks() -> list[dict]:
    """Read data/chunks.json (or empty list)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CHUNKS_FILE.exists():
        return []
    return json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))


def save_chunks(chunks: list[dict]) -> None:
    """Write data/chunks.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_FILE.write_text(json.dumps(chunks, indent=2), encoding="utf-8")


# ---------- main function you care about ----------

def ingest_path(path: str) -> dict:
    """
    User gives a path → we chunk it → save to data/chunks.json.

    Example:
      ingest_path("~/school/ai-stuff/full-pdf/loop-engineering.pdf")
    """
    # clean path: remove quotes, expand ~
    clean = (path or "").strip().strip("'\"")
    target = Path(clean).expanduser().resolve()

    files = list_files(target)
    if not files:
        return {"ok": False, "error": f"No .md/.txt/.pdf under {target}"}

    # keep old chunks from OTHER files; replace chunks for these files
    names = {f.name for f in files}
    full_paths = {str(f) for f in files}
    old = [
        c
        for c in load_chunks()
        if c.get("source") not in full_paths
        and Path(str(c.get("source", ""))).name not in names
    ]

    new = []
    errors = []
    for f in files:
        try:
            text = read_any_file(f)
            new.extend(make_chunks(text, source=str(f)))
        except Exception as e:
            errors.append(f"{f.name}: {e}")

    all_chunks = old + new
    save_chunks(all_chunks)

    return {
        "ok": True,
        "files": [f.name for f in files],
        "new_chunks": len(new),
        "total_chunks": len(all_chunks),
        "errors": errors,
    }


def get_file_text(name: str, max_chars: int = 12000) -> str:
    """
    After ingest, get lots of text from one file (for summaries).
    `name` can be a filename like "loop-engineering.pdf".
    """
    key = (name or "").strip().lower()
    matched = [c for c in load_chunks() if key in str(c.get("source", "")).lower()]
    if not matched:
        return f"No data for {name!r}. Call ingest_file first."

    out = []
    used = 0
    for c in matched:
        t = c.get("text") or ""
        if used + len(t) > max_chars:
            out.append(t[: max_chars - used])
            out.append("\n\n[truncated]")
            break
        out.append(t)
        used += len(t)

    return f"Source: {matched[0]['source']} ({len(matched)} chunks)\n\n" + "\n\n".join(out)


if __name__ == "__main__":
    # CLI: python -m rag.ingest /path/to/file
    arg = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "docs")
    print(json.dumps(ingest_path(arg), indent=2))
