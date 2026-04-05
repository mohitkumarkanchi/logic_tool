from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator

from logictool.models.enums import Complexity, Language, SnippetType


class SnippetMetadata(BaseModel):
    """Metadata attached to every snippet for filtering and organization."""

    domain: str = Field(..., description="Top-level domain e.g. 'strings', 'pandas', 'opencv'")
    subdomain: str | None = Field(None, description="e.g. 'groupby', 'bounding_box', 'arima'")
    complexity: Complexity
    language: Language
    snippet_type: SnippetType = SnippetType.SNIPPET
    tags: list[str] = Field(default_factory=list)


class Snippet(BaseModel):
    """Core data model for a single code snippet or boilerplate."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=500)
    code: str = Field(..., min_length=5)
    why: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="One-line explanation of WHY this works — reinforces understanding",
    )
    metadata: SnippetMetadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("tags", mode="before", check_fields=False)
    @classmethod
    def _parse_tags(cls, v):
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        return v

    @property
    def search_text(self) -> str:
        """Combined text used for embedding generation."""
        parts = [
            self.title,
            self.description,
            self.metadata.domain,
            self.metadata.subdomain or "",
            " ".join(self.metadata.tags),
        ]
        return " ".join(p for p in parts if p)


class SnippetBatch(BaseModel):
    """A batch of snippets returned from LLM generation."""

    domain: str
    complexity: Complexity
    language: Language
    snippets: list[Snippet]
    generated_by: str = ""  # e.g. "claude-sonnet-4-20250514"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def count(self) -> int:
        return len(self.snippets)