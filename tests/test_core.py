"""Core tests for logictool — run with: uv run pytest tests/ -v"""

import json
import pytest
import asyncio
from pathlib import Path

from logictool.models.enums import Complexity, Language, SnippetType
from logictool.models.snippet import Snippet, SnippetMetadata, SnippetBatch
from logictool.models.domain import DomainDefinition
from logictool.services.validator import SnippetValidator
from logictool.repository.sqlite_repo import SQLiteSnippetRepository
from logictool.repository.json_repo import JSONSnippetExporter
from logictool.llm.factory import LLMFactory
from logictool.config.domains import get_all_domains, get_all_tasks


# ─── FIXTURES ────────────────────────────────────────────────

@pytest.fixture
def sample_snippet():
    return Snippet(
        title="Case insensitive string compare",
        description="Compare two strings ignoring case differences using lower()",
        code='def iequal(a: str, b: str) -> bool:\n    return a.lower() == b.lower()',
        why="lower() normalizes both strings before comparison, avoiding case mismatch",
        metadata=SnippetMetadata(
            domain="strings",
            subdomain="comparison",
            complexity=Complexity.BASIC,
            language=Language.PYTHON,
            snippet_type=SnippetType.SNIPPET,
            tags=["string", "compare", "case-insensitive"],
        ),
    )


@pytest.fixture
def sample_snippet_2():
    return Snippet(
        title="Read CSV with pandas",
        description="Load a CSV file into a DataFrame with common options",
        code='import pandas as pd\ndf = pd.read_csv("data.csv", sep=",", encoding="utf-8")',
        why="read_csv handles file I/O, parsing, and type inference in one call",
        metadata=SnippetMetadata(
            domain="pandas",
            subdomain="io",
            complexity=Complexity.BASIC,
            language=Language.PYTHON,
            tags=["pandas", "csv", "dataframe"],
        ),
    )


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_snippets.db"


@pytest.fixture
def json_dir(tmp_path):
    return tmp_path / "raw"


# ─── MODEL TESTS ─────────────────────────────────────────────

class TestModels:
    def test_snippet_creation(self, sample_snippet):
        assert sample_snippet.title == "Case insensitive string compare"
        assert sample_snippet.metadata.domain == "strings"
        assert sample_snippet.metadata.complexity == Complexity.BASIC
        assert len(sample_snippet.id) == 12

    def test_snippet_search_text(self, sample_snippet):
        text = sample_snippet.search_text
        assert "string" in text
        assert "compare" in text
        assert "strings" in text  # domain

    def test_snippet_tags_from_string(self):
        m = SnippetMetadata(
            domain="test",
            complexity=Complexity.BASIC,
            language=Language.PYTHON,
            tags="foo, bar, baz",
        )
        assert m.tags == ["foo", "bar", "baz"]

    def test_snippet_batch(self, sample_snippet, sample_snippet_2):
        batch = SnippetBatch(
            domain="mixed",
            complexity=Complexity.BASIC,
            language=Language.PYTHON,
            snippets=[sample_snippet, sample_snippet_2],
            generated_by="test",
        )
        assert batch.count == 2

    def test_domain_task_generation(self):
        d = DomainDefinition(
            name="test",
            display_name="Test Domain",
            description="A test",
            applicable_languages=[Language.PYTHON, Language.BASH],
            complexity_hints={
                Complexity.BASIC: ["hint1"],
                Complexity.MEDIUM: ["hint2"],
            },
        )
        tasks = d.get_generation_tasks()
        # 2 languages × 2 complexity levels = 4 tasks
        assert len(tasks) == 4


# ─── VALIDATOR TESTS ─────────────────────────────────────────

class TestValidator:
    def test_extract_json_array(self):
        raw = '```json\n[{"title": "test", "description": "desc"}]\n```'
        result = SnippetValidator.extract_json_array(raw)
        assert len(result) == 1
        assert result[0]["title"] == "test"

    def test_extract_json_with_preamble(self):
        raw = 'Here are the snippets:\n[{"title": "test", "description": "d"}]'
        result = SnippetValidator.extract_json_array(raw)
        assert len(result) == 1

    def test_extract_json_trailing_comma(self):
        raw = '[{"title": "a", "description": "b"},]'
        result = SnippetValidator.extract_json_array(raw)
        assert len(result) == 1

    def test_validate_snippet_success(self):
        raw = {
            "title": "Test Snippet",
            "description": "A test snippet for validation",
            "code": "print('hello')",
            "why": "Simple print demonstrates basic output",
            "tags": ["test"],
            "subdomain": "basic",
        }
        s = SnippetValidator.validate_snippet(
            raw, "test", Language.PYTHON, Complexity.BASIC
        )
        assert s is not None
        assert s.title == "Test Snippet"
        assert s.metadata.domain == "test"

    def test_validate_snippet_missing_fields(self):
        raw = {"title": "No Code"}
        s = SnippetValidator.validate_snippet(
            raw, "test", Language.PYTHON, Complexity.BASIC
        )
        assert s is None

    def test_parse_llm_response_full(self):
        response = json.dumps([
            {
                "title": "Snippet One",
                "description": "First test snippet for validation",
                "code": "x = 1\ny = 2\nprint(x + y)",
                "why": "Basic arithmetic demonstrates variable usage",
                "tags": ["math", "basic"],
                "subdomain": None,
            }
        ])
        snippets = SnippetValidator.parse_llm_response(
            response, "numbers", Language.PYTHON, Complexity.BASIC
        )
        assert len(snippets) == 1
        assert snippets[0].metadata.language == Language.PYTHON


# ─── REPOSITORY TESTS ────────────────────────────────────────

class TestSQLiteRepo:
    @pytest.fixture
    async def repo(self, db_path):
        r = SQLiteSnippetRepository(db_path)
        await r.init()
        yield r
        await r.close()

    @pytest.mark.asyncio
    async def test_insert_and_get(self, repo, sample_snippet):
        sid = await repo.insert(sample_snippet)
        retrieved = await repo.get_by_id(sid)
        assert retrieved is not None
        assert retrieved.title == sample_snippet.title

    @pytest.mark.asyncio
    async def test_insert_batch(self, repo, sample_snippet, sample_snippet_2):
        count = await repo.insert_batch([sample_snippet, sample_snippet_2])
        assert count == 2
        total = await repo.count()
        assert total == 2

    @pytest.mark.asyncio
    async def test_filter_by_domain(self, repo, sample_snippet, sample_snippet_2):
        await repo.insert_batch([sample_snippet, sample_snippet_2])
        results = await repo.filter(domain="strings")
        assert len(results) == 1
        assert results[0].metadata.domain == "strings"

    @pytest.mark.asyncio
    async def test_filter_by_language(self, repo, sample_snippet):
        await repo.insert(sample_snippet)
        results = await repo.filter(language=Language.PYTHON)
        assert len(results) == 1
        results = await repo.filter(language=Language.CPP)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_fts_search(self, repo, sample_snippet, sample_snippet_2):
        await repo.insert_batch([sample_snippet, sample_snippet_2])
        results = await repo.search_by_text("CSV pandas", limit=5)
        assert len(results) >= 1
        assert results[0].metadata.domain == "pandas"

    @pytest.mark.asyncio
    async def test_delete(self, repo, sample_snippet):
        sid = await repo.insert(sample_snippet)
        assert await repo.count() == 1
        deleted = await repo.delete(sid)
        assert deleted is True
        assert await repo.count() == 0

    @pytest.mark.asyncio
    async def test_get_domains(self, repo, sample_snippet, sample_snippet_2):
        await repo.insert_batch([sample_snippet, sample_snippet_2])
        domains = await repo.get_domains()
        assert "strings" in domains
        assert "pandas" in domains


class TestJSONExporter:
    def test_save_and_load(self, json_dir, sample_snippet, sample_snippet_2):
        exporter = JSONSnippetExporter(json_dir)

        batch = SnippetBatch(
            domain="strings",
            complexity=Complexity.BASIC,
            language=Language.PYTHON,
            snippets=[sample_snippet, sample_snippet_2],
            generated_by="test",
        )
        path = exporter.save_batch(batch)
        assert path.exists()

        loaded = exporter.load_batch(path)
        assert len(loaded) == 2

    def test_load_all(self, json_dir, sample_snippet):
        exporter = JSONSnippetExporter(json_dir)

        for complexity in [Complexity.BASIC, Complexity.MEDIUM]:
            batch = SnippetBatch(
                domain="strings",
                complexity=complexity,
                language=Language.PYTHON,
                snippets=[sample_snippet],
                generated_by="test",
            )
            exporter.save_batch(batch)

        all_snippets = exporter.load_all()
        assert len(all_snippets) == 2

    def test_stats(self, json_dir, sample_snippet):
        exporter = JSONSnippetExporter(json_dir)
        batch = SnippetBatch(
            domain="strings",
            complexity=Complexity.BASIC,
            language=Language.PYTHON,
            snippets=[sample_snippet],
            generated_by="test",
        )
        exporter.save_batch(batch)
        s = exporter.stats()
        assert "strings__python__basic" in s


# ─── FACTORY TESTS ───────────────────────────────────────────

class TestLLMFactory:
    def test_available_providers(self):
        providers = LLMFactory.available_providers()
        assert "claude" in providers
        assert "gemini" in providers

    def test_create_claude(self):
        provider = LLMFactory.create("claude", api_key="test-key")
        assert provider.name == "claude"
        assert "claude" in provider.get_model_name().lower() or "sonnet" in provider.get_model_name().lower()

    def test_create_gemini(self):
        provider = LLMFactory.create("gemini", api_key="test-key")
        assert provider.name == "gemini"

    def test_unknown_provider(self):
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            LLMFactory.create("openai", api_key="test")

    def test_custom_model(self):
        provider = LLMFactory.create("claude", api_key="test", model="claude-opus-4-20250514")
        assert provider.get_model_name() == "claude-opus-4-20250514"


# ─── DOMAIN CONFIG TESTS ─────────────────────────────────────

class TestDomainConfig:
    def test_all_domains_valid(self):
        domains = get_all_domains()
        assert len(domains) > 20  # We defined ~30+ domains

        for d in domains:
            assert d.name, f"Domain missing name"
            assert d.display_name, f"{d.name} missing display_name"
            assert len(d.applicable_languages) > 0, f"{d.name} has no languages"
            assert len(d.complexity_hints) > 0, f"{d.name} has no complexity hints"

    def test_all_tasks_generated(self):
        tasks = get_all_tasks()
        assert len(tasks) > 100  # Should be 300+

    def test_no_duplicate_domain_names(self):
        domains = get_all_domains()
        names = [d.name for d in domains]
        assert len(names) == len(set(names)), "Duplicate domain names found"