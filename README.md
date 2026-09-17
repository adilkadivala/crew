# Crew (beginner version)

One **boss agent**. It can:

1. **Ingest** a file path (chunk `.md` / `.txt` / `.pdf`)
2. **Spawn a researcher** sub-agent (search / summarize)
3. **Spawn a writer** sub-agent (email, FAQ, post…)

```text
You
 → main.py
    → main_agent (boss)
         ├─ ingest_file      → rag/ingest.py
         ├─ ask_researcher   → new sub-agent
         └─ ask_writer       → new sub-agent
```

## Run

```bash
cd ~/school/prectices/crew
uv run src/main.py
```

Examples:

```text
You > ingest ~/school/ai-stuff/full-pdf/loop-engineering.pdf then summarize
You > write a short FAQ about refunds using docs/
```

## Folders

| Path | What it is |
|------|------------|
| `src/main.py` | CLI |
| `src/llm.py` | model + prompts |
| `src/crew/main_agent.py` | boss + sub-agents |
| `src/rag/` | chunk files + search |
| `src/mcp_*` | optional advanced (P04) — not needed for the simple path |

## .env

```env
LLM_PROVIDER=ollama
LLM_MODEL=gpt-oss:120b-cloud
```
