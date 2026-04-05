from __future__ import annotations

from pathlib import Path

import numpy as np
from rich.console import Console
from rich.progress import track
from sentence_transformers import SentenceTransformer

from logictool.models.snippet import Snippet

console = Console()


class EmbeddingService:
    """
    Manages S-BERT embeddings for semantic search.

    Handles:
    - Loading the embedding model (lazy, cached)
    - Generating embeddings for snippets
    - Saving/loading embedding index to/from disk
    - Single query embedding for search
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        embeddings_path: str | Path = "data/embeddings.npz",
    ):
        self._model_name = model_name
        self._embeddings_path = Path(embeddings_path)
        self._model: SentenceTransformer | None = None

        # In-memory index
        self._vectors: np.ndarray | None = None  # shape: (n_snippets, embedding_dim)
        self._ids: list[str] = []  # snippet ids aligned with vectors

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model on first use."""
        if self._model is None:
            console.print(f"[dim]Loading embedding model: {self._model_name}...[/dim]")
            self._model = SentenceTransformer(self._model_name)
            console.print(f"[dim]Model loaded. Embedding dim: {self._model.get_sentence_embedding_dimension()}[/dim]")
        return self._model

    @property
    def embedding_dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    @property
    def is_loaded(self) -> bool:
        return self._vectors is not None and len(self._ids) > 0

    @property
    def count(self) -> int:
        return len(self._ids)

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text string. Returns 1D vector."""
        return self.model.encode(text, normalize_embeddings=True)

    def embed_texts(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        """Embed multiple texts. Returns 2D array (n_texts, dim)."""
        return self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

    def build_index(self, snippets: list[Snippet]) -> int:
        """
        Build embedding index from snippets.
        Embeds all snippet search_text and stores in memory.
        Returns count of indexed snippets.
        """
        if not snippets:
            console.print("[yellow]No snippets to index.[/yellow]")
            return 0

        console.print(f"[bold]Building embedding index for {len(snippets)} snippets...[/bold]")

        texts = [s.search_text for s in snippets]
        ids = [s.id for s in snippets]

        vectors = self.embed_texts(texts)

        self._vectors = vectors
        self._ids = ids

        console.print(
            f"[green]Index built: {len(ids)} vectors, "
            f"dim={vectors.shape[1]}, "
            f"size={vectors.nbytes / 1024:.1f} KB[/green]"
        )

        return len(ids)

    def save_index(self) -> Path:
        """Save embedding index to disk as compressed numpy file."""
        if self._vectors is None:
            raise RuntimeError("No index to save. Call build_index first.")

        self._embeddings_path.parent.mkdir(parents=True, exist_ok=True)

        np.savez_compressed(
            self._embeddings_path,
            vectors=self._vectors,
            ids=np.array(self._ids, dtype=object),
        )

        size_kb = self._embeddings_path.stat().st_size / 1024
        console.print(f"[green]Index saved: {self._embeddings_path} ({size_kb:.1f} KB)[/green]")
        return self._embeddings_path

    def load_index(self) -> bool:
        """Load embedding index from disk. Returns True if loaded successfully."""
        if not self._embeddings_path.exists():
            console.print(f"[yellow]No index file found at {self._embeddings_path}[/yellow]")
            return False

        data = np.load(self._embeddings_path, allow_pickle=True)
        self._vectors = data["vectors"]
        self._ids = data["ids"].tolist()

        console.print(
            f"[dim]Index loaded: {len(self._ids)} vectors from {self._embeddings_path}[/dim]"
        )
        return True

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """
        Semantic search: embed query, cosine similarity against index.

        Returns list of (snippet_id, score) tuples, sorted by score descending.
        """
        if not self.is_loaded:
            raise RuntimeError("No index loaded. Call build_index or load_index first.")

        query_vec = self.embed_text(query)  # (dim,)

        # Cosine similarity — vectors are already normalized, so dot product = cosine sim
        scores = self._vectors @ query_vec  # (n_snippets,)

        # Top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append((self._ids[idx], float(scores[idx])))

        return results

    def add_to_index(self, snippet: Snippet) -> None:
        """Add a single snippet to the in-memory index (for incremental adds)."""
        vec = self.embed_text(snippet.search_text)

        if self._vectors is None:
            self._vectors = vec.reshape(1, -1)
            self._ids = [snippet.id]
        else:
            self._vectors = np.vstack([self._vectors, vec.reshape(1, -1)])
            self._ids.append(snippet.id)

    def remove_from_index(self, snippet_id: str) -> bool:
        """Remove a snippet from the in-memory index."""
        if snippet_id not in self._ids:
            return False

        idx = self._ids.index(snippet_id)
        self._vectors = np.delete(self._vectors, idx, axis=0)
        self._ids.pop(idx)
        return True