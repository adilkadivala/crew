from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
load_dotenv()


from crew.main_agent import run_main_agent

def main() -> None:
    print("Type 'quit' to exit.\n")


    while True:
        try:
            query = input("Query > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.lower() in ("q", "quit", "exit"):
            break
        try:
            result = run_main_agent(query)
            print(result)
        except Exception as e:
            print(f"[Error] failed: {e}")
            continue


if __name__ == "__main__":
    main()
