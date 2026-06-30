"""Local BLAST+ runner."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

from biokit.exceptions import BlastError


def run_blast_local(
    query: str | Path,
    db: str,
    outfmt: int = 5,
    extra_args: Sequence[str] | None = None,
    blast_executable: str = "blastn",
    output_path: str | Path | None = None,
) -> str:
    """Run a local BLAST+ executable.

    Raises
    ------
    BlastError
        If the executable is not found or returns a non-zero exit code.
    """
    if shutil.which(blast_executable) is None:
        raise BlastError(
            f"executable not found on PATH: {blast_executable!r}. "
            "Install BLAST+ and ensure it is reachable from the shell."
        )
    cmd: list[str] = [
        blast_executable,
        "-query",
        str(query),
        "-db",
        db,
        "-outfmt",
        str(outfmt),
    ]
    if extra_args:
        cmd.extend(extra_args)
    if output_path is not None:
        cmd.extend(["-out", str(output_path)])
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603
    except subprocess.CalledProcessError as exc:
        raise BlastError(f"BLAST failed (exit {exc.returncode}): {exc.stderr.strip()}") from exc
    if output_path is None:
        return result.stdout
    return Path(output_path).read_text()


__all__ = ["run_blast_local"]
