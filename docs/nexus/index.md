# Nexus Ω — Biological Interpretation Intelligence

> **BioKit computes. Nexus understands.**

Nexus is an AI-native scientific operating system for biology. It orchestrates deterministic bioinformatics (BioKit), scientific knowledge bases, and large language models into a single interpretation layer that augments — never replaces — scientifically validated computation.

## Prime Directive

> Never replace deterministic biological computation. All biological calculations remain inside BioKit or other validated scientific software. Nexus exists to interpret, validate, explain, reason, retrieve evidence, generate reports, quantify uncertainty, orchestrate workflows, and assist researchers. Never fabricate biological knowledge. Never present speculation as fact.

This directive is enforced architecturally by the [`BioKit`](api/core.md#nexus.core.biokit.BioKit) interface, the only legal boundary between deterministic computation and AI-assisted reasoning in Nexus.

## What Nexus is

- An AI-native scientific OS for biology
- An interpretation layer over BioKit
- A literature-grounded reasoning system
- A multi-agent orchestration platform
- A reproducibility-first research tool

## What Nexus is not

- A chatbot
- A general-purpose LLM wrapper
- A bioinformatics toolkit (BioKit is)
- A molecular prediction system
- A replacement for scientific judgment

## Quick links

- [Architecture overview](architecture.md)
- [Quickstart guide](quickstart.md)
- [CLI reference](cli.md)
- [REST API reference](rest_api.md)
- [Contributing](contributing.md)

## Installation

```bash
pip install nexus-bii

# Or with specific LLM providers:
pip install "nexus-bii[openai,anthropic]"

# Or from source for development:
git clone https://github.com/nexus-bii/nexus.git
cd nexus
pip install -e ".[dev]"
```

## Quickstart

```python
from nexus.sdk import quickstart
from nexus.providers.dummy import DummyProvider

nx = quickstart(provider=DummyProvider())
result = nx.interpret("What is known about BRCA1?")
print(result.answer)
print(f"Confidence: {result.confidence.value:.2f}")
for citation in result.citations:
    print(f"  - {citation}")
```

## License

Apache License 2.0. See [the repository](https://github.com/nexus-bii/nexus) for the full text.
