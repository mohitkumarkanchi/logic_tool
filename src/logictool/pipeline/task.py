from __future__ import annotations

from dataclasses import dataclass, field

from logictool.models.enums import Complexity, Language


@dataclass
class GenerationTask:
    """A single unit of work for the generation pipeline."""

    domain: str
    display_name: str
    description: str
    language: Language
    complexity: Complexity
    hints: list[str] = field(default_factory=list)
    subdomains: list[dict] = field(default_factory=list)

    # Status tracking
    status: str = "pending"  # pending | running | completed | failed
    error: str | None = None
    snippets_generated: int = 0
    retries: int = 0

    @property
    def task_id(self) -> str:
        return f"{self.domain}__{self.language}__{self.complexity}"

    def __repr__(self) -> str:
        return (
            f"Task({self.domain}/{self.language}/{self.complexity} "
            f"status={self.status} snippets={self.snippets_generated})"
        )