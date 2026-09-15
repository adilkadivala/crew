"""
Chat model for Crew.

Set in .env:
  LLM_PROVIDER = ollama | groq | openrouter
  LLM_MODEL_NAME = ...
  LLM_API_KEY = ...  (groq / openrouter)
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


def get_model():
    """Return one LangChain chat model from .env."""
    provider = (os.getenv("LLM_PROVIDER") or "ollama").strip().lower()
    model_name = os.getenv("LLM_MODEL_NAME") or "llama3.1"
    api_key = os.getenv("LLM_API_KEY")

    if provider == "openrouter":
        from langchain_openrouter import ChatOpenRouter

        return ChatOpenRouter(
            model=model_name,
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
            app_title="Crew",
        )

    if provider == "groq":
        return init_chat_model(
            model=model_name or "llama-3.3-70b-versatile",
            model_provider="groq",
            api_key=api_key or os.getenv("GROQ_API_KEY"),
        )

    return init_chat_model(
        model=model_name,
        model_provider="ollama",
    )
