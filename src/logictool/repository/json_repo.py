from __future__ import annotations

import json
from pathlib import Path

from logictool.models.snippet import Snippet, SnippetBatch


class JSONSnippetExporter:
    """
    JSON file-based export/import for snippet batches.
    Used as intermediate storage during generation pipeline
    before importing into SQLite.
    """

    def __init__(self, base_dir: str | Path):
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _file_path(self, domain: str, language: str, complexity: str) -> Path:
        return self._base_dir / f"{domain}__{language}__{complexity}.json"

    def save_batch(self, batch: SnippetBatch) -> Path:
        """Save a generated batch to a JSON file. Returns the file path."""
        path = self._file_path(batch.domain, batch.language, batch.complexity)

        data = {
            "domain": batch.domain,
            "language": batch.language,
            "complexity": batch.complexity,
            "generated_by": batch.generated_by,
            "generated_at": batch.generated_at.isoformat(),
            "count": batch.count,
            "snippets": [s.model_dump(mode="json") for s in batch.snippets],
        }

        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def load_batch(self, path: Path) -> list[Snippet]:
        """Load snippets from a JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        snippets = []
        for item in data.get("snippets", []):
            try:
                snippets.append(Snippet.model_validate(item))
            except Exception as e:
                print(f"[WARN] Skipping invalid snippet in {path.name}: {e}")
        return snippets

    def load_all(self) -> list[Snippet]:
        """Load all snippets from all JSON files in the directory."""
        all_snippets = []
        for path in sorted(self._base_dir.glob("*.json")):
            all_snippets.extend(self.load_batch(path))
        return all_snippets

    def list_files(self) -> list[Path]:
        return sorted(self._base_dir.glob("*.json"))

    def stats(self) -> dict[str, int]:
        """Return count of snippets per file."""
        result = {}
        for path in self.list_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            result[path.stem] = data.get("count", 0)
        return result