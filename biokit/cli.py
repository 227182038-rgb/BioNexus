"""BioKit 2.0 command-line interface.

Typer is an optional dependency; if it is not installed, the CLI module
still imports cleanly and :func:`main` prints a helpful error message.

The Typer ``@app.command()`` decorator erases function types at the
mypy level (it returns ``CommandFunctionType`` which mypy treats as
``Any``). To preserve strict typing inside this module we define each
command body as a typed function and register them with Typer via
``app.command()(fn)`` rather than using the decorator syntax.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Annotated, Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def _no_typer_option(*args: Any, **kwargs: Any) -> None:
    """Stub for :func:`typer.Option` when typer is not installed."""
    return None


typer: Any = None
Option: Any = _no_typer_option
try:
    import typer as _typer_mod
    from typer import Option as _typer_option

    typer = _typer_mod
    Option = _typer_option
except ImportError:  # pragma: no cover
    pass


if typer is not None:
    app: Any = typer.Typer(
        name="biokit",
        help="BioKit 2.0 — a market-competitive Python toolkit for biology.",
        no_args_is_help=True,
        rich_markup_mode="rich",
    )
else:
    app = None


# ---------------------------------------------------------------------------
# Command implementations (typed, no decorator)
# ---------------------------------------------------------------------------


def _gc(
    sequence: Annotated[str, Option("--sequence", "-s", help="DNA sequence")],
    window: Annotated[int, Option("--window", "-w", help="Window size")] = 100,
) -> None:
    """Compute GC content of a sequence."""
    from rich.console import Console

    from biokit.statistics.sequence_stats import gc_fraction

    console = Console()
    console.print(f"[bold]Total GC:[/bold] {gc_fraction(sequence) * 100:.2f}%")


def _orfs(
    sequence: Annotated[str, Option("--sequence", "-s", help="DNA sequence")],
    min_length: Annotated[int, Option("--min-length", "-m", help="Minimum ORF length")] = 30,
) -> None:
    """Find ORFs in a sequence."""
    from rich.console import Console
    from rich.table import Table

    from biokit.orf import ORFFinder

    finder = ORFFinder(minimum_length=min_length)
    results = finder.find(sequence)
    console = Console()
    table = Table(title="ORFs")
    table.add_column("Start", justify="right")
    table.add_column("End", justify="right")
    table.add_column("Frame", justify="right")
    table.add_column("Strand")
    table.add_column("Protein")
    for orf in results:
        table.add_row(
            str(orf.start), str(orf.end), str(orf.frame), orf.strand, orf.protein_sequence
        )
    console.print(table)


def _translate_cmd(
    sequence: Annotated[str, Option("--sequence", "-s", help="DNA sequence")],
    frame: Annotated[int, Option("--frame", "-f", help="Reading frame 1/2/3")] = 1,
) -> None:
    """Translate a DNA sequence to a protein."""
    from rich.console import Console

    from biokit.translation import Translator

    console = Console()
    protein = Translator().translate(sequence, frame=frame)
    console.print(f"[bold]Protein:[/bold] {protein}")


def _version() -> None:
    """Print the BioKit version."""
    from rich.console import Console

    from biokit import __version__

    Console().print(f"BioKit [bold]{__version__}[/bold]")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def _register_commands() -> None:
    """Register every command implementation with the Typer ``app``."""
    if typer is None or app is None:
        return
    app.command()(_gc)
    app.command()(_orfs)
    app.command(name="translate")(_translate_cmd)
    app.command()(_version)


_register_commands()


def main() -> None:
    """Entry point for ``python -m biokit``."""
    if typer is None:
        print("Error: typer is not installed. Run `pip install typer rich`.")
        sys.exit(1)
    app()


if __name__ == "__main__":
    main()
