"""BioNexus bridge — the integration layer between BioKit 2.0 and NEXUS.

This package is the *only* place where NEXUS learns about BioKit's concrete
API. Adding a new BioKit module to NEXUS = adding one entry in
:mod:`bridge.biokit_programs`.

The bridge enforces the Prime Directive (Critical Review Finding F6):
BioKit computations stay deterministic and content-addressed; NEXUS agents
may consume their outputs as evidence but may not modify them.

Public API
----------
- :func:`quickstart` — one-call setup that returns a fully-wired
  :class:`nexus.Nexus` instance with all BioKit programs registered.
- :func:`register_all` — register every BioKit 2.0 module as a Nexus
  ``BioKitProgram`` on an existing :class:`nexus.core.biokit.InProcessBioKit`.
- :class:`BioKitProgramRegistry` — convenience registry mapping program
  names to their wrapper classes.
"""

from __future__ import annotations

from bridge.biokit_programs import (
    PROGRAMS,
    BioKitProgramRegistry,
    register_all,
)
from bridge.prelude import list_biokit_programs, quickstart

__all__ = [
    "BioKitProgramRegistry",
    "PROGRAMS",
    "register_all",
    "quickstart",
    "list_biokit_programs",
]

__version__ = "1.0.0"
