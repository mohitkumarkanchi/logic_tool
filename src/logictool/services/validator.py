from __future__ import annotations

import json
import re

from logictool.models.enums import Complexity, Language, SnippetType
from logictool.models.snippet import Snippet, SnippetMetadata


class SnippetValidator:
    """Validates and parses raw LLM output into Snippet models."""

    @staticmethod
    def extract_json_array(raw: str) -> list[dict]:
        """
        Extract JSON array from LLM response.
        Handles common issues: markdown fences, preamble text, trailing commas.
        """
        # Strip markdown code fences
        cleaned = re.sub(r"```json\s*", "", raw)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.strip()

        # Try to find array boundaries
        start = cleaned.find("[")
        end = cleaned.rfind("]")

        if start == -1 or end == -1:
            raise ValueError("No JSON array found in LLM response")

        json_str = cleaned[start : end + 1]

        # Remove trailing commas before ] (common LLM mistake)
        json_str = re.sub(r",\s*]", "]", json_str)
        json_str = re.sub(r",\s*}", "}", json_str)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from LLM: {e}") from e

        if not isinstance(data, list):
            raise ValueError(f"Expected JSON array, got {type(data)}")

        return data

    @staticmethod
    def validate_snippet(
        raw_item: dict,
        domain: str,
        language: Language,
        complexity: Complexity,
    ) -> Snippet | None:
        """
        Validate a single raw dict from LLM output and convert to Snippet.
        Returns None if validation fails.
        """
        required = {"title", "description", "code", "why"}
        missing = required - set(raw_item.keys())
        if missing:
            print(f"[WARN] Missing fields {missing} in snippet: {raw_item.get('title', '?')}")
            return None

        # Basic quality checks
        if len(raw_item["code"].strip()) < 5:
            print(f"[WARN] Code too short: {raw_item['title']}")
            return None

        if len(raw_item["description"]) < 10:
            raw_item["description"] = f"{raw_item['title']} - {domain} primitive in {language}"

        if len(raw_item["why"]) < 10:
            raw_item["why"] = f"Standard {complexity} pattern for {raw_item['title']}"

        # Determine snippet type based on code length
        code_lines = raw_item["code"].count("\n") + 1
        stype = SnippetType.BOILERPLATE if code_lines > 30 else SnippetType.SNIPPET

        tags = raw_item.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        try:
            return Snippet(
                title=raw_item["title"],
                description=raw_item["description"],
                code=raw_item["code"],
                why=raw_item["why"],
                metadata=SnippetMetadata(
                    domain=domain,
                    subdomain=raw_item.get("subdomain"),
                    complexity=complexity,
                    language=language,
                    snippet_type=stype,
                    tags=tags,
                ),
            )
        except Exception as e:
            print(f"[WARN] Validation failed for '{raw_item.get('title')}': {e}")
            return None

    @classmethod
    def parse_llm_response(
        cls,
        raw_response: str,
        domain: str,
        language: Language,
        complexity: Complexity,
    ) -> list[Snippet]:
        """Full pipeline: raw LLM text -> list of validated Snippets."""
        try:
            items = cls.extract_json_array(raw_response)
        except ValueError as e:
            print(f"[ERROR] Failed to parse response for {domain}/{language}/{complexity}: {e}")
            return []

        snippets = []
        for item in items:
            s = cls.validate_snippet(item, domain, language, complexity)
            if s:
                snippets.append(s)

        return snippets