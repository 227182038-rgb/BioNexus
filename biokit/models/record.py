"""Generic record base class."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Record:
    """A generic record with an ID and optional description."""

    id: str
    description: str = ""


__all__ = ["Record"]
