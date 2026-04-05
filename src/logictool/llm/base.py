from __future__ import annotations

from abc import ABC, abstractmethod

from logictool.models.snippet import SnippetBatch


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers. All providers must implement this."""

    name: str

    @abstractmethod
    async def generate_snippets(self, prompt: str, system: str) -> str:
        """Send prompt to LLM and return raw text response."""
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model identifier string."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Cleanup resources (close HTTP clients etc)."""
        ...