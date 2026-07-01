# Architecture

Nexus is a layered, modular platform. This page describes the major layers and how they interact.

## Layered view

```
                    ┌──────────────────────────────┐
                    │   User (SDK / CLI / API / Web)│
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │       Orchestrator           │
                    │  (multi-agent coordination)  │
                    └──────┬───────────────┬───────┘
                           │               │
              ┌────────────▼──┐       ┌────▼────────────┐
              │  Agents       │       │  Intelligence   │
              │  literature   │       │  interpretation │
              │  validation   │       │  validation     │
              │  experiment   │       │  reasoning      │
              │  workflow     │       │  hypothesis     │
              │  report       │       │  explanation    │
              └────┬──────────┘       └────┬────────────┘
                   │                       │
              ┌────▼───────────────────────▼────┐
              │              Engine              │
              │  (Kernel: evidence ledger,       │
              │   claim graph, provenance,        │
              │   uncertainty, gates)             │
              └────┬───────────────────────┬─────┘
                   │                       │
        ┌──────────▼─────────┐   ┌─────────▼──────────┐
        │       RAG          │   │     Providers      │
        │  indexing          │   │  openai            │
        │  retrieval         │   │  anthropic         │
        │  ranking           │   │  gemini            │
        │  citation          │   │  glm / ollama      │
        └──────────┬─────────┘   │  openrouter        │
                   │             └────────────────────┘
        ┌──────────▼─────────┐
        │    Knowledge       │
        │  pubmed / ncbi     │
        │  uniprot / pdb     │
        │  ensembl / go      │
        └────────────────────┘

                    ┌──────────────────────────────┐
                    │          BioKit              │  ◀── deterministic
                    │  (alignment, structure,      │      substrate
                    │   ADMET phys-chem, variants) │      (NOT Nexus)
                    └──────────────────────────────┘
```

## The Prime Directive, enforced

The Prime Directive — *never replace deterministic biological computation* — is enforced by the [`BioKit`](api/core.md#nexus.core.biokit.BioKit) interface:

- `BioKitOutput` is tagged `deterministic=True` and carries no `Uncertainty` envelope. Its uncertainty is zero by construction.
- `BioKitOutput` enters the Evidence Ledger as `EvidenceClass.DETERMINISTIC`, the only class whose confidence does not decay over time.
- AI modules may consume `BioKitOutput` as evidence but may not overwrite it. Any attempt to register an AI-modified BioKit output raises `DeterministicBoundaryViolation`.
- The Engine refuses to register a deterministic claim that carries an uncertainty envelope, and refuses to register an AI-assisted claim that lacks one.

These invariants are checked at runtime by the [`Engine`](api/core.md#nexus.core.engine.Engine).

## The Engine — central intelligence kernel

The [`Engine`](api/core.md#nexus.core.engine.Engine) is the load-bearing layer of the platform. It owns:

- **Evidence Ledger** — append-only, content-addressed log of every observation, computation, and publication reference that has entered the system.
- **Claim Graph** — directed graph of claims (nodes) and inferential relationships (edges: supports, contradicts, refines, supersedes).
- **Provenance Chain** — DAG tracing every claim back to source artifacts (DOIs, assay files, model fingerprints, code commits, environment hashes).
- **Uncertainty Envelope** — typed uncertainty object attached to every AI-assisted claim, with sub-types for aleatoric, epistemic, and model-form uncertainty.
- **Gate State** — record of every gate evaluation (calibration, benchmark, replication, adversarial, shadow) performed on a subject.

The Engine does *not* reason. It enforces the invariants under which reasoning modules operate.

## The Orchestrator

The [`Orchestrator`](api/core.md#nexus.core.orchestrator.Orchestrator) coordinates specialized agents through the shared Engine. It:

- Holds a registry of agents
- Routes a user request to the appropriate agent
- Sequences multi-step workflows (`invoke_sequence`)
- Records every agent invocation in a history list

The Orchestrator does not reason. It dispatches.

## Intelligence modules

Five intelligence modules implement the actual AI reasoning:

- [`InterpretationModule`](api/intelligence.md) — turn BioKit output into a human-readable interpretation
- [`ValidationModule`](api/intelligence.md) — validate computational results against literature
- [`ReasoningModule`](api/intelligence.md) — mechanistic and causal reasoning over claims
- [`HypothesisModule`](api/intelligence.md) — generate novel, testable hypotheses
- [`ExplanationModule`](api/intelligence.md) — explain at multiple audience levels (beginner → expert)

Every module produces an [`Interpretation`](api/core.md#nexus.core.types.Interpretation) — the canonical AI output contract — with explicit evidence IDs, uncertainty, confidence, alternatives, contradictions, and a recommended next step.

## Agents

Five specialized agents compose modules, RAG, and knowledge sources:

- `LiteratureAgent` — retrieve and synthesize literature
- `ValidationAgent` — validate a claim against retrieved evidence
- `ExperimentAgent` — propose and prioritize experiments
- `WorkflowAgent` — coordinate multi-step workflows
- `ReportAgent` — generate publication-quality reports

## RAG

The RAG framework indexes scientific sources and retrieves cited passages. Every retrieval result carries a [`Citation`](api/rag.md) with provenance. The default index is in-memory TF-IDF; production deployments can plug in a vector-store-backed index via the plugin system.

## Knowledge sources

Typed async HTTP clients for PubMed, NCBI, UniProt, PDB, Ensembl, and Gene Ontology. Each client returns `KnowledgeRecord` objects that the RAG framework can index.

## Providers

LLM providers are pluggable. Nexus ships with adapters for OpenAI, Anthropic, Gemini, GLM (Zhipu), Ollama, and OpenRouter. Provider SDKs are imported lazily — a provider can be configured without its SDK being installed; the SDK is only imported when the provider is actually invoked.

## Memory

Three distinct memory stores:

- `ResearchMemory` — long-term, backed by the Engine's Claim Graph
- `ConversationMemory` — short-term, with a configurable window
- `ProjectMemory` — per-project, persisted as JSON

## Engineering standards

Nexus follows:

- **SOLID** principles
- **Clean / Hexagonal Architecture** where appropriate
- **Dependency Injection** for providers, knowledge sources, memory
- **Strict typing** — every public API passes `mypy --strict`
- **Composition over inheritance**

## Quality gates

```bash
ruff check . --fix      # lint
ruff format .           # format
python -m mypy nexus    # strict typing
python -m pytest        # tests
mkdocs build            # docs
```

All five gates must pass for a pull request to be mergeable.
