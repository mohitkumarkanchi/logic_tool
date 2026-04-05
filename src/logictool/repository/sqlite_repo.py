from __future__ import annotations

import json
from pathlib import Path

import aiosqlite

from logictool.models.enums import Complexity, Language, SnippetType
from logictool.models.snippet import Snippet, SnippetMetadata
from logictool.repository.base import BaseSnippetRepository

SCHEMA = """
CREATE TABLE IF NOT EXISTS snippets (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    code TEXT NOT NULL,
    why TEXT NOT NULL,
    domain TEXT NOT NULL,
    subdomain TEXT,
    complexity TEXT NOT NULL,
    language TEXT NOT NULL,
    snippet_type TEXT NOT NULL DEFAULT 'snippet',
    tags TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_domain ON snippets(domain);
CREATE INDEX IF NOT EXISTS idx_language ON snippets(language);
CREATE INDEX IF NOT EXISTS idx_complexity ON snippets(complexity);
CREATE INDEX IF NOT EXISTS idx_domain_lang ON snippets(domain, language);

CREATE VIRTUAL TABLE IF NOT EXISTS snippets_fts USING fts5(
    title, description, tags, domain, subdomain,
    content='snippets',
    content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS snippets_ai AFTER INSERT ON snippets BEGIN
    INSERT INTO snippets_fts(rowid, title, description, tags, domain, subdomain)
    VALUES (new.rowid, new.title, new.description, new.tags, new.domain, new.subdomain);
END;

CREATE TRIGGER IF NOT EXISTS snippets_ad AFTER DELETE ON snippets BEGIN
    INSERT INTO snippets_fts(snippets_fts, rowid, title, description, tags, domain, subdomain)
    VALUES ('delete', old.rowid, old.title, old.description, old.tags, old.domain, old.subdomain);
END;
"""


class SQLiteSnippetRepository(BaseSnippetRepository):
    """SQLite-backed snippet repository with FTS5 full-text search."""

    def __init__(self, db_path: str | Path):
        self._db_path = Path(db_path)
        self._conn: aiosqlite.Connection | None = None

    async def init(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self._db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Repository not initialized. Call init() first.")
        return self._conn

    def _row_to_snippet(self, row: aiosqlite.Row) -> Snippet:
        tags = json.loads(row["tags"]) if row["tags"] else []
        return Snippet(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            code=row["code"],
            why=row["why"],
            metadata=SnippetMetadata(
                domain=row["domain"],
                subdomain=row["subdomain"],
                complexity=Complexity(row["complexity"]),
                language=Language(row["language"]),
                snippet_type=SnippetType(row["snippet_type"]),
                tags=tags,
            ),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def insert(self, snippet: Snippet) -> str:
        m = snippet.metadata
        await self.conn.execute(
            """INSERT OR REPLACE INTO snippets
            (id, title, description, code, why, domain, subdomain,
             complexity, language, snippet_type, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                snippet.id,
                snippet.title,
                snippet.description,
                snippet.code,
                snippet.why,
                m.domain,
                m.subdomain,
                m.complexity.value,
                m.language.value,
                m.snippet_type.value,
                json.dumps(m.tags),
                snippet.created_at.isoformat(),
                snippet.updated_at.isoformat(),
            ),
        )
        await self.conn.commit()
        return snippet.id

    async def insert_batch(self, snippets: list[Snippet]) -> int:
        count = 0
        for s in snippets:
            try:
                await self.insert(s)
                count += 1
            except Exception as e:
                print(f"[WARN] Failed to insert '{s.title}': {e}")
        return count

    async def get_by_id(self, snippet_id: str) -> Snippet | None:
        async with self.conn.execute(
            "SELECT * FROM snippets WHERE id = ?", (snippet_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return self._row_to_snippet(row) if row else None

    async def search_by_text(self, query: str, limit: int = 10) -> list[Snippet]:
        sql = """
            SELECT s.* FROM snippets s
            JOIN snippets_fts fts ON s.rowid = fts.rowid
            WHERE snippets_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """
        async with self.conn.execute(sql, (query, limit)) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_snippet(r) for r in rows]

    async def filter(
        self,
        domain: str | None = None,
        language: Language | None = None,
        complexity: Complexity | None = None,
        tags: list[str] | None = None,
        limit: int = 50,
    ) -> list[Snippet]:
        conditions, params = [], []

        if domain:
            conditions.append("domain = ?")
            params.append(domain)
        if language:
            conditions.append("language = ?")
            params.append(language.value)
        if complexity:
            conditions.append("complexity = ?")
            params.append(complexity.value)
        if tags:
            for tag in tags:
                conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")

        where = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM snippets WHERE {where} ORDER BY domain, complexity LIMIT ?"
        params.append(limit)

        async with self.conn.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_snippet(r) for r in rows]

    async def get_all(self) -> list[Snippet]:
        async with self.conn.execute("SELECT * FROM snippets ORDER BY domain, complexity") as cur:
            rows = await cur.fetchall()
            return [self._row_to_snippet(r) for r in rows]

    async def count(self, domain: str | None = None) -> int:
        if domain:
            sql, params = "SELECT COUNT(*) FROM snippets WHERE domain = ?", (domain,)
        else:
            sql, params = "SELECT COUNT(*) FROM snippets", ()
        async with self.conn.execute(sql, params) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def delete(self, snippet_id: str) -> bool:
        cursor = await self.conn.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
        await self.conn.commit()
        return cursor.rowcount > 0

    async def get_domains(self) -> list[str]:
        async with self.conn.execute("SELECT DISTINCT domain FROM snippets ORDER BY domain") as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()