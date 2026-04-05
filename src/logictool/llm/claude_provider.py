from __future__ import annotations

import anthropic

from logictool.llm.base import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""

    name = "claude"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self._model = model
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    def get_model_name(self) -> str:
        return self._model

    async def generate_snippets(self, prompt: str, system: str) -> str:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from response content blocks
        text_parts = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)

        return "\n".join(text_parts)

    async def close(self) -> None:
        await self._client.close()