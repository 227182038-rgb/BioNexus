# Installation

BioKit 2.0 requires Python 3.10 or newer.

## From source (recommended for development)

```bash
git clone https://github.com/227182038-rgb/Python-for-Biology.git
cd Python-for-Biology
pip install -e ".[dev,ml,viz,docs]"
```

## Optional extras

| Extra | Installs |
| --- | --- |
| `dev` | pytest, pytest-cov, pytest-xdist, pytest-benchmark, hypothesis, ruff, mypy, pre-commit |
| `ml` | scikit-learn, pandas |
| `viz` | reportlab, seaborn |
| `docs` | mkdocs, mkdocs-material, mkdocstrings, mike |

Install all extras with:

```bash
pip install -e ".[all]"
```

## Verify the installation

```bash
python -c "import biokit; print(biokit.__version__)"
pytest
```
