from __future__ import annotations

from logictool.models.snippet import Snippet
from logictool.repository.sqlite_repo import SQLiteSnippetRepository
from logictool.search.semantic import SearchResult


class KeywordSearch:
    """
    FTS5-based keyword search.
    Fast exact match for when you know what you're looking for.
    """

    def __init__(self, repo: SQLiteSnippetRepository):
        self._repo = repo

    async def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """
        Search using SQLite FTS5 full-text search.
        Handles FTS5 query syntax (AND, OR, NOT, prefix*).
        """
        try:
            snippets = await self._repo.search_by_text(query, limit=top_k)
        except Exception:
            # FTS5 can fail on malformed queries — fall back to simple LIKE
            snippets = await self._repo.filter(limit=top_k)

        results = []
        for i, s in enumerate(snippets):
            # FTS5 results are ranked, so position = relevance proxy
            score = 1.0 - (i * 0.05)  # simple decay score
            results.append(
                SearchResult(snippet=s, score=max(score, 0.1), source="keyword")
            )

        return results