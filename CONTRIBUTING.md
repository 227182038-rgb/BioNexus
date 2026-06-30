# Contributing to BioKit 2.0

Thank you for your interest in contributing! This document describes the
development workflow and quality standards.

## Development setup

```bash
git clone https://github.com/227182038-rgb/Python-for-Biology.git
cd Python-for-Biology
pip install -e ".[dev,ml,viz,docs]"
pre-commit install
```

## Quality gates

Before opening a PR, all of the following must pass:

```bash
ruff check .
ruff format --check .
pytest --cov=biokit
```

We require 80%+ test coverage for new code.

## Style

- Python 3.10+ with full type hints (PEP 484, PEP 695)
- `@dataclass(slots=True, frozen=True)` for value types
- NumPy-style docstrings with `Examples` sections
- Modules are organised in subpackages (one module per file)
- No circular imports — use runtime imports inside functions when needed

## Pull request checklist

- [ ] Tests pass locally
- [ ] Coverage stays ≥ 80%
- [ ] Ruff is clean
- [ ] Docstrings added/updated for new public API
- [ ] CHANGELOG.md updated
