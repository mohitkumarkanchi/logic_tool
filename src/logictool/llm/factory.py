from __future__ import annotations

from logictool.llm.base import BaseLLMProvider
from logictool.llm.claude_provider import ClaudeProvider
from logictool.llm.gemini_provider import GeminiProvider
from logictool.models.enums import LLMProvider


class LLMFactory:
    """
    Factory pattern for creating LLM provider instances.

    Usage:
        provider = LLMFactory.create("claude", api_key="sk-...")
        provider = LLMFactory.create("gemini", api_key="AIza...")
    """

    _registry: dict[str, type[BaseLLMProvider]] = {
        LLMProvider.CLAUDE: ClaudeProvider,
        LLMProvider.GEMINI: GeminiProvider,
    }

    @classmethod
    def create(
        cls,
        provider_name: str,
        api_key: str,
        model: str | None = None,
    ) -> BaseLLMProvider:
        provider_name = provider_name.lower()
        if provider_name not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Unknown LLM provider: '{provider_name}'. Available: {available}"
            )

        provider_cls = cls._registry[provider_name]

        kwargs: dict = {"api_key": api_key}
        if model:
            kwargs["model"] = model

        return provider_cls(**kwargs)

    @classmethod
    def register(cls, name: str, provider_cls: type[BaseLLMProvider]) -> None:
        """Register a custom LLM provider at runtime."""
        cls._registry[name] = provider_cls

    @classmethod
    def available_providers(cls) -> list[str]:
        return list(cls._registry.keys())