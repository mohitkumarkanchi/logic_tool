from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from logictool.models.snippet import Snippet
from logictool.search.semantic import SearchResult

console = Console()

LANG_MAP = {
    "python": "python",
    "cpp": "cpp",
    "bash": "bash",
    "javascript": "javascript",
    "html": "html",
}


def display_snippet(snippet: Snippet, index: int = 0, show_score: float | None = None) -> None:
    """Render a single snippet with syntax highlighting."""
    m = snippet.metadata

    # Header
    title_parts = [f"[bold cyan]{index}. {snippet.title}[/bold cyan]"]
    if show_score is not None:
        title_parts.append(f"  [dim]score: {show_score:.3f}[/dim]")

    console.print("".join(title_parts))

    # Metadata line
    meta_parts = [
        f"[magenta]{m.domain}[/magenta]",
        f"[blue]{m.language}[/blue]",
        f"[yellow]{m.complexity}[/yellow]",
    ]
    if m.subdomain:
        meta_parts.insert(1, f"[dim]{m.subdomain}[/dim]")

    console.print("  " + " · ".join(meta_parts))

    # Description and why
    console.print(f"  {snippet.description}")
    console.print(f"  [italic green]→ {snippet.why}[/italic green]")

    # Tags
    if m.tags:
        tag_str = " ".join(f"[dim]#{t}[/dim]" for t in m.tags)
        console.print(f"  {tag_str}")

    # Code
    syntax = Syntax(
        snippet.code,
        LANG_MAP.get(m.language, "text"),
        theme="monokai",
        line_numbers=True,
        padding=(0, 1),
    )
    console.print(Panel(syntax, border_style="dim", expand=False))
    console.print()


def display_results(results: list[SearchResult], query: str) -> None:
    """Render a list of search results."""
    if not results:
        console.print(f"\n[yellow]No results found for:[/yellow] {query}")
        console.print("[dim]Try different keywords or use broader terms.[/dim]")
        return

    console.print(f"\n[bold]Found {len(results)} results for:[/bold] [cyan]{query}[/cyan]\n")

    for i, r in enumerate(results, 1):
        display_snippet(r.snippet, index=i, show_score=r.score)


def display_stats_table(domain_counts: dict[str, int], total: int) -> None:
    """Render domain statistics table."""
    table = Table(
        title=f"[bold]Snippet Library — {total} total[/bold]",
        show_lines=False,
        border_style="dim",
    )
    table.add_column("Domain", style="cyan", min_width=20)
    table.add_column("Snippets", justify="right", style="bold")
    table.add_column("Bar", min_width=30)

    max_count = max(domain_counts.values()) if domain_counts else 1

    for domain, count in sorted(domain_counts.items()):
        bar_len = int((count / max_count) * 25)
        bar = "█" * bar_len + "░" * (25 - bar_len)
        table.add_row(domain, str(count), f"[green]{bar}[/green]")

    console.print(table)


def display_snippet_compact(snippet: Snippet) -> None:
    """One-line compact display for browse mode."""
    m = snippet.metadata
    console.print(
        f"  [{m.complexity}] "
        f"[cyan]{snippet.title:40s}[/cyan] "
        f"[dim]{m.language:10s} {m.domain}/{m.subdomain or '-'}[/dim]"
    )