from __future__ import annotations

from logictool.models.enums import Complexity, Language
from logictool.models.snippet import Snippet
from logictool.repository.sqlite_repo import SQLiteSnippetRepository
from logictool.search.keyword import KeywordSearch
from logictool.search.semantic import SearchResult, SemanticSearch
from logictool.services.embedder import EmbeddingService


class HybridSearch:
    """
    Combines semantic (S-BERT) and keyword (FTS5) search with Reciprocal Rank Fusion.

    Strategy:
    1. Run both semantic and keyword search
    2. Merge results using RRF scoring
    3. Apply metadata filters (domain, language, complexity)
    4. Return top-k combined results

    RRF formula: score = sum(1 / (k + rank_i)) for each ranking list
    This gives fair weight to both exact matches and semantic matches.
    """

    RRF_K = 60  # Standard RRF constant

    def __init__(
        self,
        repo: SQLiteSnippetRepository,
        embedder: EmbeddingService,
    ):
        self._repo = repo
        self._semantic = SemanticSearch(embedder)
        self._keyword = KeywordSearch(repo)
        self._embedder = embedder

    async def _load_snippet_index(self) -> dict[str, Snippet]:
        """Load all snippets into a lookup dict for semantic search."""
        all_snippets = await self._repo.get_all()
        return {s.id: s for s in all_snippets}

    def _reciprocal_rank_fusion(
        self,
        *result_lists: list[SearchResult],
    ) -> list[SearchResult]:
        """
        Merge multiple ranked lists using Reciprocal Rank Fusion.
        Returns a single merged list sorted by combined RRF score.
        """
        rrf_scores: dict[str, float] = {}
        snippet_map: dict[str, Snippet] = {}
        sources: dict[str, set] = {}

        for results in result_lists:
            for rank, result in enumerate(results, start=1):
                sid = result.snippet.id
                rrf_scores[sid] = rrf_scores.get(sid, 0.0) + (1.0 / (self.RRF_K + rank))
                snippet_map[sid] = result.snippet

                if sid not in sources:
                    sources[sid] = set()
                sources[sid].add(result.source)

        # Sort by RRF score descending
        sorted_ids = sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)

        merged = []
        for sid in sorted_ids:
            source_str = "+".join(sorted(sources[sid]))
            merged.append(
                SearchResult(
                    snippet=snippet_map[sid],
                    score=rrf_scores[sid],
                    source=source_str,
                )
            )

        return merged

    def _apply_filters(
        self,
        results: list[SearchResult],
        domain: str | None = None,
        language: Language | None = None,
        complexity: Complexity | None = None,
    ) -> list[SearchResult]:
        """Post-filter results by metadata."""
        filtered = results

        if domain:
            filtered = [r for r in filtered if r.snippet.metadata.domain == domain]
        if language:
            filtered = [r for r in filtered if r.snippet.metadata.language == language]
        if complexity:
            filtered = [r for r in filtered if r.snippet.metadata.complexity == complexity]

        return filtered

    async def search(
        self,
        query: str,
        top_k: int = 10,
        domain: str | None = None,
        language: Language | None = None,
        complexity: Complexity | None = None,
        mode: str = "hybrid",  # "hybrid", "semantic", "keyword"
    ) -> list[SearchResult]:
        """
        Execute search with optional mode and filters.

        Modes:
            - hybrid: Combines semantic + keyword with RRF (default, best quality)
            - semantic: Pure S-BERT cosine similarity (best for natural language queries)
            - keyword: Pure FTS5 (best for exact term matching)
        """
        fetch_k = top_k * 3  # Over-fetch before filtering

        if mode == "keyword":
            results = await self._keyword.search(query, top_k=fetch_k)

        elif mode == "semantic":
            if not self._semantic.is_ready:
                if not self._embedder.load_index():
                    raise RuntimeError(
                        "No embedding index found. Run 'logictool rebuild-index' first."
                    )
            snippet_index = await self._load_snippet_index()
            results = self._semantic.search(query, snippet_index, top_k=fetch_k)

        else:  # hybrid
            # Run keyword search
            keyword_results = await self._keyword.search(query, top_k=fetch_k)

            # Run semantic search if index available
            semantic_results = []
            if self._semantic.is_ready or self._embedder.load_index():
                snippet_index = await self._load_snippet_index()
                semantic_results = self._semantic.search(query, snippet_index, top_k=fetch_k)

            if semantic_results:
                results = self._reciprocal_rank_fusion(keyword_results, semantic_results)
            else:
                results = keyword_results

        # Apply metadata filters
        results = self._apply_filters(results, domain, language, complexity)

        return results[:top_k]