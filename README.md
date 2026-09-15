# Crew

One project that covers **P04 + P05 + P07** from the workplace-agent portfolio plan:

| Plan | Skill | In Crew |
|------|--------|---------|
| **P07** | Multi-agent | Triage → Research → Draft (LangGraph) |
| **P05** | RAG + citations | Company docs retrieved with source filenames |
| **P04** | MCP | `search_docs` / `create_draft` over a local MCP server |

**v1 = CLI.** Slack comes later.

```text
Ticket (CLI)
  → Triage agent
  → Research agent  ──MCP──► search_docs ──► RAG over docs/
  → Draft agent
  → You approve before “save draft”
```

---

## Quick start

```bash
cd ~/school/prectices/crew
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit LLM_PROVIDER / LLM_MODEL_NAME / LLM_API_KEY

PYTHONPATH=src python -m rag.ingest
PYTHONPATH=src python src/main.py
```

Press **Enter** at the prompt to run the sample double-charge ticket.

---

## Demo checks

```bash
# RAG only (citations)
PYTHONPATH=src python -m rag.retrieve "refund policy"

# MCP only
PYTHONPATH=src python -m mcp_client
```

---

## Layout

```text
crew/
├── docs/                 # company knowledge (refund, shipping, pricing)
├── data/                 # generated chunks (gitignored)
└── src/
    ├── main.py           # CLI
    ├── llm.py
    ├── mcp_client.py     # stdio client
    ├── rag/              # ingest + retrieve
    ├── mcp_server/       # MCPServer tools
    ├── agents/           # triage, research, draft
    └── crew/graph.py     # LangGraph pipeline
```

---

## Safety

- Drafts are saved only after you type `yes`.
- `create_draft` never sends mail (mock for now).

---

## Portfolio mapping

- **Buddy** ≈ P01 (Slack inbox)
- **Kitty** ≈ P02 (Notion meeting agent)
- **Crew** ≈ P04 + P05 + P07 (MCP + RAG + multi-agent)
