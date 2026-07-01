# BioNexus Changelog

## 1.0.0 (2025-07-30) — Initial unified release

BioNexus 1.0.0 unifies two previously-separate projects into a single
Apache-2.0 platform:

- **BioKit 2.0** — 30 deterministic bioinformatics modules organised in 22
  subpackages (sequence, alignment, assembly, BLAST, primer, CRISPR, popgen,
  structural, phylogeny, machine_learning, etc.)
- **NEXUS Ω** — Biological Interpretation Intelligence platform with 10
  subpackages (core engine, intelligence modules, RAG, knowledge sources,
  LLM providers, agents, memory, reports, plugins, REST API)
- **Bridge** — 23 BioKitProgram adapters that wrap every BioKit module as
  a NEXUS deterministic computation program

### Highlights

- **23 BioKit programs registered** with NEXUS via the bridge — including
  `gc_content`, `find_orfs`, `smith_waterman`, `design_primer`,
  `design_guides`, `parse_blast_xml`, `hardy_weinberg_test`, `fst`, etc.
- **275 tests passing** (157 BioKit + 88 NEXUS + 30 bridge/integration)
- **72% test coverage** across the unified codebase
- **4 LLM providers wired** into the eval harness (OpenAI, Anthropic, GLM,
  Ollama) — configurable via environment variables
- **Unified CLI** — `bionexus biokit <cmd>`, `bionexus nexus <cmd>`,
  `bionexus run <program>`, `bionexus programs`, `bionexus version`
- **Prime Directive enforced** — BioKit computations stay deterministic
  and content-addressed; NEXUS agents consume their outputs as evidence
  but may not modify them
- **Apache-2.0 license** — single license across the entire platform

### Migration from BioKit 2.0 standalone

BioKit 2.0 is now a subpackage of BioNexus. Existing code continues to work:

```python
# Before (BioKit 2.0 standalone)
from biokit.sequence import DNA

# After (BioNexus 1.0) — same import
from biokit.sequence import DNA
```

New integration code uses the bridge:

```python
from bridge import quickstart

nx = quickstart()
output = nx.run_biokit("gc_content", {"sequence": "ATGGCAGGT"})
result = nx.interpret("What does this GC content mean?", agent="literature",
                     context={"biokit_output": output.outputs})
```

### Architecture

```
                User (CLI / SDK / API / Web)
                              │
                ┌─────────────▼─────────────┐
                │     NEXUS Orchestrator    │
                │  (5 agents, intelligence, │
                │   RAG, memory, reports)   │
                └─────────────┬─────────────┘
                              │
                ┌─────────────▼─────────────┐
                │       Bridge Layer        │
                │  (23 BioKitProgram        │
                │   adapters)               │
                └─────────────┬─────────────┘
                              │
                ┌─────────────▼─────────────┐
                │       BioKit 2.0          │
                │  (30 deterministic        │
                │   bioinformatics modules) │
                └───────────────────────────┘
```
