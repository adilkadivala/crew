"""
Start here.

  cd ~/school/prectices/crew
  uv run src/main.py
"""

from crew.main_agent import run_main_agent


def main() -> None:
    print("Crew (simple)")
    print("Type quit to exit.\n")

    while True:
        try:
            query = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not query:
            continue
        if query.lower() in ("q", "quit", "exit"):
            break

        try:
            print("\nCrew >", run_main_agent(query), "\n")
        except Exception as e:
            print(f"[Error] {e}\n")


if __name__ == "__main__":
    main()
