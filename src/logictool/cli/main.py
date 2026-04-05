from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from logictool.config.domains import (
    get_all_domains,
    get_all_tasks,
    get_domain_by_name,
    print_domain_summary,
)
from logictool.config.settings import Settings
from logictool.llm.factory import LLMFactory
from logictool.models.enums import Complexity, Language, LLMProvider
from logictool.pipeline.runner import PipelineConfig, PipelineRunner
from logictool.pipeline.task import GenerationTask
from logictool.repository.json_repo import JSONSnippetExporter
from logictool.repository.sqlite_repo import SQLiteSnippetRepository

app = typer.Typer(name="logictool", help="Offline semantic code snippet manager")
console = Console()


# ─── GENERATE ────────────────────────────────────────────────


@app.command()
def generate(
    provider: str = typer.Option("claude", help="LLM provider: claude or gemini"),
    domain: str = typer.Option(None, help="Generate for specific domain only"),
    concurrency: int = typer.Option(10, help="Max parallel API calls"),
    output_dir: str = typer.Option("data/raw", help="Output directory for JSON files"),
):
    """Generate snippets using LLM API calls in parallel."""
    settings = Settings()

    # Build provider
    api_key = settings.get_api_key(provider)
    model = settings.get_model(provider)
    llm = LLMFactory.create(provider, api_key=api_key, model=model)

    console.print(f"[bold]Provider:[/bold] {llm.get_model_name()}")

    # Build tasks
    if domain:
        d = get_domain_by_name(domain)
        if not d:
            console.print(f"[red]Unknown domain: {domain}[/red]")
            available = [dom.name for dom in get_all_domains()]
            console.print(f"Available: {', '.join(available)}")
            raise typer.Exit(1)
        raw_tasks = d.get_generation_tasks()
    else:
        raw_tasks = get_all_tasks()

    tasks = [
        GenerationTask(
            domain=t["domain"],
            display_name=t["display_name"],
            description=t["description"],
            language=Language(t["language"]),
            complexity=Complexity(t["complexity"]),
            hints=t["hints"],
            subdomains=t.get("subdomains", []),
        )
        for t in raw_tasks
    ]

    console.print(f"[bold]Tasks to execute:[/bold] {len(tasks)}")

    config = PipelineConfig(
        max_concurrent=concurrency,
        output_dir=output_dir,
    )
    runner = PipelineRunner(provider=llm, config=config)

    result = asyncio.run(runner.run(tasks))

    # Cleanup
    asyncio.run(llm.close())


# ─── IMPORT ──────────────────────────────────────────────────


@app.command(name="import")
def import_to_db(
    source_dir: str = typer.Option("data/raw", help="Directory with generated JSON files"),
    db_path: str = typer.Option("data/snippets.db", help="SQLite database path"),
):
    """Import generated JSON snippets into SQLite database."""

    async def _import():
        repo = SQLiteSnippetRepository(db_path)
        await repo.init()

        exporter = JSONSnippetExporter(source_dir)
        files = exporter.list_files()

        if not files:
            console.print(f"[yellow]No JSON files found in {source_dir}[/yellow]")
            return

        total = 0
        for path in files:
            snippets = exporter.load_batch(path)
            count = await repo.insert_batch(snippets)
            total += count
            console.print(f"  [green]✓[/green] {path.name} → {count} snippets imported")

        console.print(f"\n[bold]Total imported: {total} snippets[/bold]")
        console.print(f"Database: {db_path}")

        await repo.close()

    asyncio.run(_import())


# ─── SEARCH ──────────────────────────────────────────────────


@app.command()
def search(
    query: str = typer.Argument(..., help="Natural language search query"),
    lang: str = typer.Option(None, "--lang", "-l", help="Filter by language"),
    domain_filter: str = typer.Option(None, "--domain", "-d", help="Filter by domain"),
    limit: int = typer.Option(5, "--limit", "-n", help="Number of results"),
    db_path: str = typer.Option("data/snippets.db", help="SQLite database path"),
):
    """Search snippets using keyword or semantic search."""

    async def _search():
        repo = SQLiteSnippetRepository(db_path)
        await repo.init()

        # First try FTS keyword search
        results = await repo.search_by_text(query, limit=limit)

        if not results and domain_filter:
            # Fallback to filtered browse
            results = await repo.filter(
                domain=domain_filter,
                language=Language(lang) if lang else None,
                limit=limit,
            )

        if not results:
            console.print("[yellow]No results found. Try different keywords.[/yellow]")
            await repo.close()
            return

        for i, s in enumerate(results, 1):
            m = s.metadata
            console.print(f"\n[bold cyan]━━━ {i}. {s.title} ━━━[/bold cyan]")
            console.print(f"[dim]{m.domain} / {m.subdomain or '-'} / {m.complexity} / {m.language}[/dim]")
            console.print(f"{s.description}")
            console.print(f"[italic green]Why: {s.why}[/italic green]")
            console.print(f"[dim]Tags: {', '.join(m.tags)}[/dim]")
            console.print()

            # Syntax highlighted code output
            from rich.syntax import Syntax

            lang_map = {"python": "python", "cpp": "cpp", "bash": "bash", "javascript": "javascript", "html": "html"}
            syntax = Syntax(s.code, lang_map.get(m.language, "text"), theme="monokai", line_numbers=True)
            console.print(syntax)

        await repo.close()

    asyncio.run(_search())


# ─── STATS ───────────────────────────────────────────────────


@app.command()
def stats(
    db_path: str = typer.Option("data/snippets.db", help="SQLite database path"),
):
    """Show statistics about the snippet library."""

    async def _stats():
        repo = SQLiteSnippetRepository(db_path)
        await repo.init()

        total = await repo.count()
        domains = await repo.get_domains()

        table = Table(title=f"Snippet Library — {total} total snippets")
        table.add_column("Domain", style="cyan")
        table.add_column("Count", justify="right")

        for d in domains:
            count = await repo.count(domain=d)
            table.add_row(d, str(count))

        console.print(table)
        await repo.close()

    asyncio.run(_stats())


# ─── DOMAINS ─────────────────────────────────────────────────


@app.command()
def domains():
    """List all configured domains and estimated snippet counts."""
    print_domain_summary()


# ─── EXPORT ──────────────────────────────────────────────────


@app.command()
def export(
    output_dir: str = typer.Option("data/export", help="Export directory"),
    db_path: str = typer.Option("data/snippets.db", help="SQLite database path"),
):
    """Export all snippets from database to JSON files."""

    async def _export():
        repo = SQLiteSnippetRepository(db_path)
        await repo.init()

        exporter = JSONSnippetExporter(output_dir)
        snippets = await repo.get_all()

        # Group by domain
        from collections import defaultdict

        by_domain = defaultdict(list)
        for s in snippets:
            by_domain[s.metadata.domain].append(s)

        import json

        for domain, items in by_domain.items():
            path = Path(output_dir) / f"{domain}.json"
            data = [s.model_dump(mode="json") for s in items]
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            console.print(f"  [green]✓[/green] {path.name} → {len(items)} snippets")

        console.print(f"\n[bold]Exported {len(snippets)} snippets to {output_dir}[/bold]")
        await repo.close()

    asyncio.run(_export())


if __name__ == "__main__":
    app()