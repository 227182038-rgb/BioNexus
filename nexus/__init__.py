"""Nexus Ω — Biological Interpretation Intelligence (BII) platform.

Nexus is the AI-native scientific operating system for biology. It orchestrates
deterministic bioinformatics (BioKit), scientific knowledge bases, and large
language models into a single interpretation layer that augments — never
replaces — scientifically validated computation.

Prime Directive
---------------
Never replace deterministic biological computation. All biological calculations
remain inside BioKit or other validated scientific software. Nexus exists to
interpret, validate, explain, reason, retrieve evidence, generate reports,
quantify uncertainty, orchestrate workflows, and assist researchers.

Public API
----------
- :class:`Nexus` — top-level entry point (see :mod:`nexus.sdk`)
- :class:`Engine` — central intelligence kernel (see :mod:`nexus.core.engine`)
- :class:`Orchestrator` — multi-agent coordinator (see :mod:`nexus.core.orchestrator`)
- :class:`BioKit` — deterministic computation boundary (see :mod:`nexus.core.biokit`)
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["__version__"]
