from __future__ import annotations

from dataclasses import dataclass

from logictool.models.snippet import Snippet
from logictool.services.embedder import EmbeddingService


@dataclass
class SearchResult:
    """A single search result with score and source information."""

    snippet: Snippet
    score: float
    source: str  # "semantic", "keyword", or "hybrid"

    def __repr__(self) -> str:
        return f"SearchResult({self.snippet.title}, score={self.score:.3f}, source={self.source})"


class SemanticSearch:
    """
    Pure semantic search using S-BERT embeddings.
    Wraps EmbeddingService to return full Snippet objects.
    """

    def __init__(self, embedder: EmbeddingService):
        self._embedder = embedder

    @property
    def is_ready(self) -> bool:
        return self._embedder.is_loaded

    def search(
        self,
        query: str,
        snippets_by_id: dict[str, Snippet],
        top_k: int = 10,
    ) -> list[SearchResult]:
        """
        Search for snippets matching the query semantically.

        Args:
            query: Natural language search query
            snippets_by_id: Dict mapping snippet id -> Snippet (from repo)
            top_k: Number of results to return

        Returns:
            List of SearchResult sorted by relevance score
        """
        raw_results = self._embedder.search(query, top_k=top_k * 2)  # over-fetch for filtering

        results = []
        for snippet_id, score in raw_results:
            if snippet_id in snippets_by_id:
                results.append(
                    SearchResult(
                        snippet=snippets_by_id[snippet_id],
                        score=score,
                        source="semantic",
                    )
                )

            if len(results) >= top_k:
                break

        return results