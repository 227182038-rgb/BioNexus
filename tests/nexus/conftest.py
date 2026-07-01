"""Shared test fixtures."""

from __future__ import annotations

import pytest
from nexus.core.biokit import InProcessBioKit
from nexus.core.engine import Engine
from nexus.providers.dummy import DummyProvider
from nexus.rag.indexing import InMemoryIndex
from nexus.rag.retrieval import Retriever


@pytest.fixture
def biokit() -> InProcessBioKit:
    return InProcessBioKit()


@pytest.fixture
def engine(biokit: InProcessBioKit) -> Engine:
    return Engine(biokit=biokit)


@pytest.fixture
def provider() -> DummyProvider:
    # Echo responder for predictable test outputs.
    return DummyProvider(responder=lambda msgs: "Test answer.")


@pytest.fixture
def retriever() -> Retriever:
    return Retriever(InMemoryIndex())
