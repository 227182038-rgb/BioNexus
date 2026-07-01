"""Nexus CLI — Typer-based command-line interface.

Commands:

- ``nexus interpret`` — ask Nexus a question
- ``nexus validate`` — validate a claim or BioKit output
- ``nexus report`` — generate a report from a project
- ``nexus index`` — index a document into the RAG retriever
- ``nexus search`` — search the RAG index
- ``nexus providers`` — list available LLM providers
- ``nexus agents`` — list registered agents
- ``nexus biokit`` — run a BioKit program (if registered)
- ``nexus serve`` — start the REST API server
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nexus import __version__
from nexus.core.types import Interpretation
from nexus.providers.base import LLMProvider
from nexus.providers.registry import get_registry
from nexus.sdk import Nexus

app = typer.Typer(
    name="nexus",
    help="Nexus Ω — Biological Interpretation Intelligence (BII) platform.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()


def _build_nexus(provider_name: str | None = None, model: str | None = None) -> Nexus:
    """Build a Nexus instance with the specified provider."""
    registry = get_registry()
    if provider_name is None:
        # Auto-detect: pick the first provider with an API key set.
        for name in registry.list_providers():
            if name == "dummy":
                continue
            provider = _try_create(registry, name, model)
            if provider is not None:
                return Nexus(provider=provider)
        # Fall back to dummy.
        return Nexus(provider=registry.create("dummy", model=model))
    provider = _try_create(registry, provider_name, model)
    if provider is None:
        console.print(
            f"[red]Could not create provider {provider_name!r}. Is the API key set?[/red]"
        )
        raise typer.Exit(code=1)
    return Nexus(provider=provider)


def _try_create(registry: Any, name: str, model: str | None) -> LLMProvider | None:
    """Attempt to create a provider; return None on failure."""
    try:
        provider: LLMProvider = registry.create(name, model=model)
        return provider
    except Exception:
        return None


def _print_interpretation(interp: Interpretation) -> None:
    console.print(Panel(interp.answer, title="Answer", border_style="blue"))
    table = Table(show_header=False, box=None)
    table.add_column("key", style="cyan", no_wrap=True)
    table.add_column("value")
    table.add_row("Confidence", f"{interp.confidence.value:.2f}")
    table.add_row("Provider", interp.provider_model or "unknown")
    if interp.recommended_next_step:
        table.add_row("Next step", interp.recommended_next_step)
    console.print(table)

    if interp.citations:
        console.print("\n[bold]Citations:[/bold]")
        for i, c in enumerate(interp.citations, 1):
            console.print(f"  {i}. {c}")

    if interp.contradictions:
        console.print("\n[bold red]Contradictions / caveats:[/bold red]")
        for c in interp.contradictions:
            console.print(f"  - {c}")


# ──────────────────────────────────────────────────────────────────────
# Commands
# ──────────────────────────────────────────────────────────────────────


@app.command()
def version() -> None:
    """Print the Nexus version."""
    console.print(f"Nexus Ω v{__version__}")


@app.command()
def providers() -> None:
    """List available LLM providers."""
    registry = get_registry()
    table = Table(title="Available LLM providers")
    table.add_column("name", style="cyan")
    table.add_column("default model", style="green")
    for name in registry.list_providers():
        provider = _try_create(registry, name, None)
        model = provider.model if provider else "?"
        table.add_row(name, model)
    console.print(table)


@app.command()
def agents() -> None:
    """List registered agents."""
    nx = _build_nexus()
    table = Table(title="Registered agents")
    table.add_column("name", style="cyan")
    for name in nx.list_agents():
        table.add_row(name)
    console.print(table)


@app.command()
def interpret(
    question: str = typer.Option(..., "--question", "-q", help="The question to ask."),
    agent: str = typer.Option("literature", "--agent", "-a", help="Agent to use."),
    provider: str | None = typer.Option(None, "--provider", "-p", help="LLM provider."),
    model: str | None = typer.Option(None, "--model", "-m", help="LLM model."),
) -> None:
    """Ask Nexus a question."""
    nx = _build_nexus(provider, model)
    try:
        result = nx.interpret(question, agent=agent)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    _print_interpretation(result)


@app.command()
def validate(
    claim: str = typer.Option(..., "--claim", "-c", help="The claim to validate."),
    provider: str | None = typer.Option(None, "--provider", "-p"),
    model: str | None = typer.Option(None, "--model", "-m"),
) -> None:
    """Validate a claim against literature."""
    nx = _build_nexus(provider, model)
    try:
        result = nx.interpret(claim, agent="validation")
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    _print_interpretation(result)


@app.command()
def report(
    title: str = typer.Option("Nexus report", "--title", "-t"),
    output: Path = typer.Option(Path("nexus_report.md"), "--output", "-o"),
    questions: list[str] = typer.Option(
        ...,
        "--question",
        "-q",
        help="Questions to ask (can be specified multiple times).",
    ),
    provider: str | None = typer.Option(None, "--provider", "-p"),
    model: str | None = typer.Option(None, "--model", "-m"),
) -> None:
    """Generate a publication-quality report from a set of questions."""
    nx = _build_nexus(provider, model)
    interpretations = []
    for q in questions:
        try:
            interpretations.append(nx.interpret(q, agent="literature"))
        except Exception as exc:
            console.print(f"[yellow]Skipping question {q!r}: {exc}[/yellow]")
    report_obj = nx.generate_report(title, interpretations)
    output.write_text(report_obj.to_markdown(), encoding="utf-8")
    console.print(f"[green]Report written to[/green] {output}")


@app.command()
def index(
    source_uri: str = typer.Option(..., "--uri", help="Source URI for the document."),
    title: str = typer.Option(..., "--title", help="Document title."),
    content: str = typer.Option(..., "--content", help="Document content (or @file for file)."),
    metadata_json: str | None = typer.Option(None, "--metadata", help="JSON metadata."),
) -> None:
    """Index a document into the RAG retriever."""
    nx = _build_nexus()
    metadata: dict[str, Any] = {}
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
        except json.JSONDecodeError as exc:
            console.print(f"[red]Invalid metadata JSON:[/red] {exc}")
            raise typer.Exit(code=1) from exc
    if content.startswith("@"):
        content = Path(content[1:]).read_text(encoding="utf-8")
    nx.index_text(source_uri, title, content, metadata)
    console.print(f"[green]Indexed[/green] {title!r} ({source_uri})")


@app.command()
def search(
    query: str = typer.Option(..., "--query", "-q"),
    limit: int = typer.Option(5, "--limit", "-n"),
) -> None:
    """Search the RAG index."""
    nx = _build_nexus()
    results = nx.retriever.retrieve(query, limit=limit)
    if not results:
        console.print("[yellow]No results.[/yellow]")
        return
    table = Table(title=f"Search results for {query!r}")
    table.add_column("score", style="cyan")
    table.add_column("title")
    table.add_column("source")
    for r in results:
        table.add_row(f"{r.score:.3f}", r.document.title, r.document.source_uri)
    console.print(table)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    provider: str | None = typer.Option(None, "--provider", "-p"),
    model: str | None = typer.Option(None, "--model", "-m"),
) -> None:
    """Start the Nexus REST API server."""
    try:
        import uvicorn
    except ImportError as exc:
        console.print(f"[red]uvicorn not installed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    # Build the Nexus instance and pass it to the API app via env var.
    nx = _build_nexus(provider, model)
    # Stash the instance on the API module before importing it.
    from nexus.api import app as api_app
    from nexus.api import set_nexus

    set_nexus(nx)
    console.print(f"[green]Starting Nexus API on[/green] http://{host}:{port}")
    uvicorn.run(api_app, host=host, port=port, log_level="info")


@app.command()
def biokit(
    program: str = typer.Option(..., "--program", help="BioKit program name."),
    inputs_json: str = typer.Option(..., "--inputs", help="JSON-encoded inputs."),
) -> None:
    """Run a BioKit program (if registered)."""
    nx = _build_nexus()
    try:
        inputs = json.loads(inputs_json)
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid inputs JSON:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    if program not in nx.biokit.list_programs():
        console.print(
            f"[red]BioKit program {program!r} not registered. "
            f"Available: {nx.biokit.list_programs()}[/red]"
        )
        raise typer.Exit(code=1)
    output = nx.run_biokit(program, inputs)
    console.print_json(data=output.outputs)


if __name__ == "__main__":
    app()
