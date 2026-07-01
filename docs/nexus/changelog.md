# Changelog

All notable changes to Nexus will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-06-30

### Added

- Initial release of Nexus Ω — Biological Interpretation Intelligence (BII).
- Core kernel: `Engine`, `Orchestrator`, `Scheduler`, `BioKit` boundary.
- Typed data model: `Evidence`, `Claim`, `ClaimGraph`, `Provenance`, `Uncertainty`, `Confidence`, `Interpretation`, `GateState`.
- Five intelligence modules: `InterpretationModule`, `ValidationModule`, `ReasoningModule`, `HypothesisModule`, `ExplanationModule`.
- RAG framework: `InMemoryIndex`, `Indexer`, `Retriever`, `TfidfRanker`, `CitationBuilder`.
- Knowledge clients: PubMed, NCBI, UniProt, PDB, Ensembl, Gene Ontology.
- LLM providers (lazy SDK import): OpenAI, Anthropic, Gemini, GLM, Ollama, OpenRouter, plus a built-in `DummyProvider`.
- Five specialized agents: Literature, Validation, Experiment, Workflow, Report.
- Three memory stores: Research, Conversation, Project.
- Plugin system with entry-point discovery.
- Publication-quality report generator (Markdown + plain text).
- Python SDK (`Nexus` class).
- Typer-based CLI (`nexus` command).
- FastAPI REST API.
- Minimal web UI.
- mkdocs-material documentation site.
- Full test suite covering core, intelligence, providers, RAG, agents, memory, SDK, API, CLI.
- Quality gates: ruff (lint + format), mypy strict, pytest, mkdocs build — all passing.

[0.1.0]: https://github.com/nexus-bii/nexus/releases/tag/v0.1.0
