"""BioKit 2.0 command-line interface."""

from __future__ import annotations

import sys
from typing import Annotated

try:
    import typer
    from typer import Option
except ImportError:  # pragma: no cover
    # If typer is not installed, fall back to a stub.
    typer = None  # type: ignore[assignment]

    def Option(*args, **kwargs):  # type: ignore[no-redef]
        return None


if typer is not None:
    app = typer.Typer(
        name="biokit",
        help="BioKit 2.0 — a market-competitive Python toolkit for biology.",
        no_args_is_help=True,
        rich_markup_mode="rich",
    )
else:
    app = None  # type: ignore[assignment]


def _register_commands() -> None:
    if typer is None:
        return

    @app.command()
    def gc(
        sequence: Annotated[str, Option("--sequence", "-s", help="DNA sequence")],
        window: Annotated[int, Option("--window", "-w", help="Window size")] = 100,
    ) -> None:
        """Compute GC content of a sequence."""
        from rich.console import Console

        from biokit.statistics.sequence_stats import gc_fraction

        console = Console()
        console.print(f"[bold]Total GC:[/bold] {gc_fraction(sequence) * 100:.2f}%")

    @app.command()
    def orfs(
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

    @app.command(name="translate")
    def translate_cmd(
        sequence: Annotated[str, Option("--sequence", "-s", help="DNA sequence")],
        frame: Annotated[int, Option("--frame", "-f", help="Reading frame 1/2/3")] = 1,
    ) -> None:
        """Translate a DNA sequence to a protein."""
        from rich.console import Console

        from biokit.translation import Translator

        console = Console()
        protein = Translator().translate(sequence, frame=frame)
        console.print(f"[bold]Protein:[/bold] {protein}")

    @app.command()
    def version() -> None:
        """Print the BioKit version."""
        from rich.console import Console

        from biokit import __version__

        Console().print(f"BioKit [bold]{__version__}[/bold]")


_register_commands()


def main() -> None:
    """Entry point for ``python -m biokit``."""
    if typer is None:
        print("Error: typer is not installed. Run `pip install typer rich`.")
        sys.exit(1)
    app()


if __name__ == "__main__":
    main()
