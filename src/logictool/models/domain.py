from __future__ import annotations

from pydantic import BaseModel, Field

from logictool.models.enums import Complexity, Language


class SubDomain(BaseModel):
    """A specific area within a domain."""

    name: str
    description: str
    example_topics: list[str] = Field(default_factory=list)


class DomainDefinition(BaseModel):
    """
    Complete definition of a snippet domain.
    Used as input config for the generation pipeline.
    """

    name: str = Field(..., description="Domain identifier e.g. 'strings', 'pandas'")
    display_name: str = Field(..., description="Human readable e.g. 'String & Text Manipulation'")
    description: str
    subdomains: list[SubDomain] = Field(default_factory=list)
    applicable_languages: list[Language]
    complexity_hints: dict[Complexity, list[str]] = Field(
        default_factory=dict,
        description="Hints per complexity level to guide LLM generation",
    )
    estimated_snippets: int = Field(
        default=20,
        description="Approximate number of snippets expected for this domain",
    )

    def get_generation_tasks(self) -> list[dict]:
        """Explode into individual generation tasks (domain × complexity × language)."""
        tasks = []
        for lang in self.applicable_languages:
            for complexity in Complexity:
                if complexity in self.complexity_hints:
                    tasks.append(
                        {
                            "domain": self.name,
                            "display_name": self.display_name,
                            "description": self.description,
                            "language": lang,
                            "complexity": complexity,
                            "hints": self.complexity_hints[complexity],
                            "subdomains": [s.model_dump() for s in self.subdomains],
                        }
                    )
        return tasks