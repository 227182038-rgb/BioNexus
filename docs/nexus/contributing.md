# Contributing to Nexus

Thank you for your interest in contributing to Nexus. This document describes how to set up a development environment and the standards we expect from contributions.

## Development setup

```bash
git clone https://github.com/nexus-bii/nexus.git
cd nexus
pip install -e ".[dev]"
```

This installs Nexus in editable mode along with all development dependencies (ruff, mypy, pytest, mkdocs).

## Quality gates

All contributions must pass all five quality gates:

```bash
ruff check . --fix      # lint
ruff format .           # format
python -m mypy nexus    # strict typing
python -m pytest        # tests
mkdocs build            # docs
```

You can run them all in one go:

```bash
ruff check . --fix && ruff format . && python -m mypy nexus && python -m pytest && mkdocs build
```

If any gate fails, fix the issue before opening a pull request.

## Architectural principles

1. **The Prime Directive is non-negotiable.** Never replace deterministic biological computation. All biological calculations live in BioKit; Nexus interprets, validates, explains, reasons, retrieves evidence, generates reports, quantifies uncertainty, orchestrates workflows, and assists researchers.

2. **The Engine is the kernel.** All modules communicate through the Engine. Do not introduce direct module-to-module communication.

3. **Strict typing.** Every public API must be fully type-hinted and pass `mypy --strict`.

4. **Composition over inheritance.** Prefer small, focused classes composed at runtime.

5. **Documentation-first.** Every public API must have a docstring, an example, and declared exceptions.

6. **No placeholder implementations.** No `pass`, no `TODO`, no `NotImplementedError` in production code paths.

## Pull request process

1. Fork the repository and create a feature branch.
2. Write tests for your changes. Tests must pass `pytest`.
3. Ensure all quality gates pass.
4. Update the changelog if your change is user-facing.
5. Open a pull request with a clear description of the change and the motivation.

## Reporting bugs

Open a [GitHub issue](https://github.com/nexus-bii/nexus/issues) with:

- A minimal reproducible example
- The exact Nexus version
- The Python version and operating system
- The expected behavior and the actual behavior

## Code of conduct

Be respectful. Be scientific. Be honest about uncertainty.
