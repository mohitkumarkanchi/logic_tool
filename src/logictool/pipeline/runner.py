from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.table import Table

from logictool.llm.base import BaseLLMProvider
from logictool.models.enums import Complexity, Language
from logictool.models.snippet import Snippet, SnippetBatch
from logictool.pipeline.prompts import SYSTEM_PROMPT, build_generation_prompt
from logictool.pipeline.task import GenerationTask
from logictool.repository.json_repo import JSONSnippetExporter
from logictool.services.validator import SnippetValidator

console = Console()


@dataclass
class PipelineConfig:
    max_concurrent: int = 10
    max_retries: int = 3
    retry_delay: float = 2.0
    output_dir: str = "data/raw"


@dataclass
class PipelineResult:
    total_tasks: int = 0
    completed: int = 0
    failed: int = 0
    total_snippets: int = 0
    elapsed_seconds: float = 0.0
    failed_tasks: list[GenerationTask] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Tasks: {self.completed}/{self.total_tasks} completed, {self.failed} failed\n"
            f"Snippets generated: {self.total_snippets}\n"
            f"Time: {self.elapsed_seconds:.1f}s"
        )


class PipelineRunner:
    """
    Orchestrates parallel snippet generation across domains.

    Uses asyncio.Semaphore to limit concurrent LLM calls.
    Saves results as JSON batches via JSONSnippetExporter.
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        config: PipelineConfig | None = None,
    ):
        self._provider = provider
        self._config = config or PipelineConfig()
        self._exporter = JSONSnippetExporter(self._config.output_dir)
        self._semaphore = asyncio.Semaphore(self._config.max_concurrent)
        self._validator = SnippetValidator()

    async def _execute_task(self, task: GenerationTask) -> list[Snippet]:
        """Execute a single generation task with retry logic."""
        async with self._semaphore:
            for attempt in range(1, self._config.max_retries + 1):
                task.status = "running"
                try:
                    prompt = build_generation_prompt(
                        domain=task.domain,
                        display_name=task.display_name,
                        description=task.description,
                        language=task.language.value,
                        complexity=task.complexity.value,
                        hints=task.hints,
                        subdomains=task.subdomains,
                    )

                    raw = await self._provider.generate_snippets(
                        prompt=prompt,
                        system=SYSTEM_PROMPT,
                    )

                    snippets = self._validator.parse_llm_response(
                        raw_response=raw,
                        domain=task.domain,
                        language=Language(task.language),
                        complexity=Complexity(task.complexity),
                    )

                    if not snippets:
                        raise ValueError("No valid snippets parsed from response")

                    # Save batch to JSON
                    batch = SnippetBatch(
                        domain=task.domain,
                        complexity=task.complexity,
                        language=task.language,
                        snippets=snippets,
                        generated_by=self._provider.get_model_name(),
                    )
                    self._exporter.save_batch(batch)

                    task.status = "completed"
                    task.snippets_generated = len(snippets)
                    return snippets

                except Exception as e:
                    task.retries = attempt
                    task.error = str(e)
                    if attempt < self._config.max_retries:
                        await asyncio.sleep(self._config.retry_delay * attempt)
                    else:
                        task.status = "failed"
                        console.print(
                            f"  [red]✗[/red] {task.task_id} failed after {attempt} attempts: {e}"
                        )

            return []

    async def run(self, tasks: list[GenerationTask]) -> PipelineResult:
        """Run all generation tasks in parallel with progress tracking."""
        result = PipelineResult(total_tasks=len(tasks))
        start = time.time()

        console.print(f"\n[bold]Starting pipeline: {len(tasks)} tasks[/bold]")
        console.print(f"Provider: {self._provider.get_model_name()}")
        console.print(f"Concurrency: {self._config.max_concurrent}")
        console.print(f"Output: {self._config.output_dir}\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            console=console,
        ) as progress:
            progress_task = progress.add_task("Generating snippets...", total=len(tasks))

            async def tracked_execute(task: GenerationTask) -> list[Snippet]:
                snippets = await self._execute_task(task)
                progress.advance(progress_task)

                status = "[green]✓[/green]" if task.status == "completed" else "[red]✗[/red]"
                progress.console.print(
                    f"  {status} {task.task_id} → {task.snippets_generated} snippets"
                )
                return snippets

            # Fire all tasks concurrently (semaphore limits actual concurrency)
            all_results = await asyncio.gather(
                *[tracked_execute(t) for t in tasks],
                return_exceptions=True,
            )

        # Collect results
        for task, snippets in zip(tasks, all_results):
            if isinstance(snippets, Exception):
                result.failed += 1
                result.failed_tasks.append(task)
            elif task.status == "completed":
                result.completed += 1
                result.total_snippets += len(snippets)
            else:
                result.failed += 1
                result.failed_tasks.append(task)

        result.elapsed_seconds = time.time() - start

        # Print summary
        console.print(f"\n[bold]Pipeline Complete[/bold]")
        console.print(result.summary())

        if result.failed_tasks:
            table = Table(title="Failed Tasks")
            table.add_column("Task ID")
            table.add_column("Error")
            table.add_column("Retries")
            for t in result.failed_tasks:
                table.add_row(t.task_id, t.error or "Unknown", str(t.retries))
            console.print(table)

        return result