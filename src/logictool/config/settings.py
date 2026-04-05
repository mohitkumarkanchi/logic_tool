from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Keys
    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    # Model preferences
    claude_model: str = "claude-sonnet-4-20250514"
    gemini_model: str = "gemini-2.5-flash"

    # Paths
    db_path: Path = Path("data/snippets.db")
    raw_output_dir: Path = Path("data/raw")
    embeddings_path: Path = Path("data/embeddings.npz")

    # Pipeline
    max_concurrent: int = 10
    max_retries: int = 3

    # Search
    embedding_model: str = "all-MiniLM-L6-v2"
    search_top_k: int = 10

    def get_api_key(self, provider: str) -> str:
        if provider == "claude":
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in .env")
            return self.anthropic_api_key
        elif provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not set in .env")
            return self.gemini_api_key
        raise ValueError(f"Unknown provider: {provider}")

    def get_model(self, provider: str) -> str:
        if provider == "claude":
            return self.claude_model
        elif provider == "gemini":
            return self.gemini_model
        raise ValueError(f"Unknown provider: {provider}")