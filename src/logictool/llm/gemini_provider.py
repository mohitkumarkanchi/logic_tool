from __future__ import annotations

from google import genai
from google.genai import types

from logictool.llm.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider."""

    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self._model = model
        self._client = genai.Client(api_key=api_key)

    def get_model_name(self) -> str:
        return self._model

    async def generate_snippets(self, prompt: str, system: str) -> str:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=4096,
                temperature=0.3,
            ),
        )

        return response.text

    async def close(self) -> None:
        # google-genai client doesn't require explicit cleanup
        pass