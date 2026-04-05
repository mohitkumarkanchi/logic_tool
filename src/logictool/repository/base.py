from __future__ import annotations

from abc import ABC, abstractmethod

from logictool.models.enums import Complexity, Language
from logictool.models.snippet import Snippet


class BaseSnippetRepository(ABC):
    """
    Abstract repository interface for snippet persistence.
    Concrete implementations: SQLite, JSON files.
    """

    @abstractmethod
    async def init(self) -> None:
        """Initialize storage (create tables, dirs, etc)."""
        ...

    @abstractmethod
    async def insert(self, snippet: Snippet) -> str:
        """Insert a single snippet. Returns the snippet id."""
        ...

    @abstractmethod
    async def insert_batch(self, snippets: list[Snippet]) -> int:
        """Insert multiple snippets. Returns count inserted."""
        ...

    @abstractmethod
    async def get_by_id(self, snippet_id: str) -> Snippet | None:
        """Retrieve a snippet by its unique id."""
        ...

    @abstractmethod
    async def search_by_text(self, query: str, limit: int = 10) -> list[Snippet]:
        """Full-text keyword search."""
        ...

    @abstractmethod
    async def filter(
        self,
        domain: str | None = None,
        language: Language | None = None,
        complexity: Complexity | None = None,
        tags: list[str] | None = None,
        limit: int = 50,
    ) -> list[Snippet]:
        """Filter snippets by metadata fields."""
        ...

    @abstractmethod
    async def get_all(self) -> list[Snippet]:
        """Retrieve all snippets (for embedding rebuild)."""
        ...

    @abstractmethod
    async def count(self, domain: str | None = None) -> int:
        """Count snippets, optionally filtered by domain."""
        ...

    @abstractmethod
    async def delete(self, snippet_id: str) -> bool:
        """Delete a snippet by id. Returns True if deleted."""
        ...

    @abstractmethod
    async def get_domains(self) -> list[str]:
        """Get list of all distinct domains in the repository."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Cleanup resources."""
        ...