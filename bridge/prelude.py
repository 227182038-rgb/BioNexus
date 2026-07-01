"""One-call prelude: wire NEXUS + BioKit 2.0 together with a single import.

Example
-------
>>> from bridge import quickstart
>>> from nexus.providers import DummyProvider
>>> nx = quickstart(provider=DummyProvider())
>>> output = nx.run_biokit("gc_content", {"sequence": "ATGGCAGGTGACCCGTGA"})
>>> output.outputs["gc_percentage"]
55.56
"""

from __future__ import annotations

from nexus.core.biokit import InProcessBioKit
from nexus.providers.base import LLMProvider
from nexus.providers.dummy import DummyProvider
from nexus.sdk import Nexus

from bridge.biokit_programs import register_all


def quickstart(
    provider: LLMProvider | None = None,
    biokit: InProcessBioKit | None = None,
) -> Nexus:
    """Return a fully-wired :class:`Nexus` with every BioKit program registered.

    Parameters
    ----------
    provider : LLMProvider, optional
        The LLM provider to use. Defaults to :class:`DummyProvider` which
        returns canned responses — perfect for tests and demos without
        burning real LLM tokens.
    biokit : InProcessBioKit, optional
        A pre-configured BioKit facade. If omitted, a fresh
        :class:`InProcessBioKit` is created and every BioKit 2.0 program
        is registered on it via :func:`bridge.register_all`.

    Returns
    -------
    Nexus
        A Nexus instance whose ``run_biokit`` method can invoke any of
        the 22+ registered BioKit programs by name.

    Example
    -------
    >>> from bridge import quickstart
    >>> nx = quickstart()
    >>> nx.list_agents()  # literature, validation, experiment, workflow, report
    ['experiment', 'literature', 'report', 'validation', 'workflow']
    >>> output = nx.run_biokit("find_orfs", {"sequence": "ATGGCAGGTGACCCGTGA", "minimum_length": 6})
    >>> output.outputs["count"] >= 1
    True
    """
    if biokit is None:
        biokit = InProcessBioKit()
        register_all(biokit)
    return Nexus(provider=provider or DummyProvider(), biokit=biokit)


def list_biokit_programs() -> list[str]:
    """Return the sorted list of BioKit program names registered by ``quickstart``."""
    from bridge.biokit_programs import BioKitProgramRegistry

    return BioKitProgramRegistry.list_programs()


__all__ = ["quickstart", "list_biokit_programs"]
