"""BioNexus evaluation harness — run end-to-end benchmarks across LLM providers.

This harness exercises the full BioNexus stack (BioKit 2.0 + NEXUS agents)
with multiple LLM providers and reports deterministic quality metrics.

It is designed for the research article's evaluation section: golden
questions + golden BioKit outputs + measurable answer quality.

Usage
-----
    # Run the full eval harness with all configured providers
    python -m tests.eval.run_eval --providers all --output eval_results.json

    # Run with a specific provider only
    python -m tests.eval.run_eval --providers openai --output eval_results.json

    # Run without any real LLM (DummyProvider only — for CI)
    python -m tests.eval.run_eval --providers dummy --output eval_results.json

LLM credentials
---------------
Set the following environment variables before running:

- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- ZHIPUAI_API_KEY (for GLM)
- OLLAMA_HOST (default http://localhost:11434)

Providers without credentials are skipped automatically.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from bridge import quickstart
from nexus.providers.base import LLMProvider
from nexus.providers.dummy import DummyProvider

# ---------------------------------------------------------------------------
# Golden dataset
# ---------------------------------------------------------------------------


@dataclass
class GoldenQuestion:
    """A single evaluation question with its golden BioKit computation."""

    id: str
    agent: str
    question: str
    biokit_program: str
    biokit_inputs: dict[str, Any]
    golden_answer_keywords: list[str]
    """Lowercase substrings that should appear in a correct answer."""
    min_confidence: float = 0.0
    """Minimum acceptable confidence (0..1)."""


#: The 5 golden questions used in the research article evaluation.
GOLDEN_QUESTIONS: list[GoldenQuestion] = [
    GoldenQuestion(
        id="q1_gc_content",
        agent="literature",
        question="What does this GC content suggest about the origin of the sequence?",
        biokit_program="gc_content",
        biokit_inputs={"sequence": "ATGGCAGGTGACCCGTGAATGAAACGTACGTTAAGGATGCAA"},
        golden_answer_keywords=["gc", "content"],
        min_confidence=0.0,
    ),
    GoldenQuestion(
        id="q2_orf_interpretation",
        agent="literature",
        question="What can you infer from these open reading frames?",
        biokit_program="find_orfs",
        biokit_inputs={
            "sequence": "ATGGCAGGTGACCCGTGAATGAAACGTACGTTAAGGATGCAA",
            "minimum_length": 6,
        },
        golden_answer_keywords=["orf", "protein"],
        min_confidence=0.0,
    ),
    GoldenQuestion(
        id="q3_primer_design",
        agent="validation",
        question="Are these primers suitable for PCR? Explain why or why not.",
        biokit_program="design_primer",
        biokit_inputs={
            "template": "ATGGCAGGTGACCCGTTGACCGTACGTAACGCATGCAGT",
            "length": 20,
        },
        golden_answer_keywords=["primer", "tm"],
        min_confidence=0.0,
    ),
    GoldenQuestion(
        id="q4_crispr_guides",
        agent="validation",
        question="Evaluate the quality of these CRISPR guide RNAs.",
        biokit_program="design_guides",
        biokit_inputs={
            "sequence": "ATGGCAGGTGACCCGTTGACCGGTAACGCATGCAGTGGACCTAGG",
        },
        golden_answer_keywords=["guide", "pam"],
        min_confidence=0.0,
    ),
    GoldenQuestion(
        id="q5_alignment",
        agent="literature",
        question="What does this sequence alignment tell us about conservation?",
        biokit_program="smith_waterman",
        biokit_inputs={"seq1": "ACGTACGTACGT", "seq2": "ACGTACGT"},
        golden_answer_keywords=["alignment", "match"],
        min_confidence=0.0,
    ),
]


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------


def make_provider(name: str) -> LLMProvider | None:
    """Construct a provider by name. Returns None if credentials are missing."""
    name = name.lower()
    if name == "dummy":
        return DummyProvider()
    if name == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            from nexus.providers.openai_provider import OpenAIProvider

            return OpenAIProvider(model="gpt-4o-mini", api_key=api_key)
        except Exception:
            return None
    if name == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        try:
            from nexus.providers.anthropic_provider import AnthropicProvider

            return AnthropicProvider(model="claude-3-5-haiku-20241022", api_key=api_key)
        except Exception:
            return None
    if name == "glm":
        api_key = os.environ.get("ZHIPUAI_API_KEY")
        if not api_key:
            return None
        try:
            from nexus.providers.glm_provider import GLMProvider

            return GLMProvider(model="glm-4-flash", api_key=api_key)
        except Exception:
            return None
    if name == "ollama":
        try:
            from nexus.providers.ollama_provider import OllamaProvider

            return OllamaProvider(
                model="llama3.1", host=os.environ.get("OLLAMA_HOST", "http://localhost:11434")
            )
        except Exception:
            return None
    return None


ALL_PROVIDER_NAMES = ["dummy", "openai", "anthropic", "glm", "ollama"]


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


@dataclass
class QuestionResult:
    """Result of evaluating one question with one provider."""

    question_id: str
    provider: str
    answer: str
    confidence: float
    elapsed_seconds: float
    keywords_found: list[str]
    keywords_missing: list[str]
    passed: bool
    error: str | None = None


@dataclass
class EvalReport:
    """Top-level evaluation report."""

    providers: list[str] = field(default_factory=list)
    results: list[QuestionResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "providers": self.providers,
            "pass_rate": self.pass_rate,
            "num_questions": len(self.results),
            "results": [asdict(r) for r in self.results],
        }


def evaluate_question(
    provider: LLMProvider,
    provider_name: str,
    question: GoldenQuestion,
) -> QuestionResult:
    """Run one golden question against one provider."""
    nx = quickstart(provider=provider)
    start = time.time()
    try:
        biokit_out = nx.run_biokit(question.biokit_program, question.biokit_inputs)
        result = nx.interpret(
            question.question,
            agent=question.agent,
            context={"biokit_output": biokit_out.outputs},
        )
        elapsed = time.time() - start
        answer_lower = result.answer.lower()
        keywords_found = [k for k in question.golden_answer_keywords if k in answer_lower]
        keywords_missing = [k for k in question.golden_answer_keywords if k not in answer_lower]
        passed = not keywords_missing and result.confidence.value >= question.min_confidence
        return QuestionResult(
            question_id=question.id,
            provider=provider_name,
            answer=result.answer,
            confidence=result.confidence.value,
            elapsed_seconds=elapsed,
            keywords_found=keywords_found,
            keywords_missing=keywords_missing,
            passed=passed,
        )
    except Exception as exc:
        return QuestionResult(
            question_id=question.id,
            provider=provider_name,
            answer="",
            confidence=0.0,
            elapsed_seconds=time.time() - start,
            keywords_found=[],
            keywords_missing=question.golden_answer_keywords,
            passed=False,
            error=str(exc),
        )


def run_eval(providers: list[str] | None = None) -> EvalReport:
    """Run the full eval harness.

    Parameters
    ----------
    providers : list[str], optional
        Provider names to evaluate. Defaults to all configured providers.
        Providers with missing credentials are silently skipped.

    Returns
    -------
    EvalReport
        The full evaluation report.
    """
    if providers is None or providers == ["all"]:
        providers = ALL_PROVIDER_NAMES

    report = EvalReport()
    for provider_name in providers:
        provider = make_provider(provider_name)
        if provider is None:
            continue
        report.providers.append(provider_name)
        for question in GOLDEN_QUESTIONS:
            result = evaluate_question(provider, provider_name, question)
            report.results.append(result)
    return report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point: ``python -m tests.eval.run_eval``."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the BioNexus eval harness")
    parser.add_argument(
        "--providers",
        nargs="+",
        default=["dummy"],
        help="Provider names (dummy, openai, anthropic, glm, ollama, all)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("eval_results.json"),
        help="Output JSON file path",
    )
    args = parser.parse_args()

    print(f"Running eval with providers: {args.providers}")
    report = run_eval(providers=args.providers)
    args.output.write_text(json.dumps(report.to_dict(), indent=2))
    print(f"\nResults written to {args.output}")
    print(f"Providers evaluated: {report.providers}")
    print(f"Questions per provider: {len(GOLDEN_QUESTIONS)}")
    print(f"Total results: {len(report.results)}")
    print(f"Pass rate: {report.pass_rate:.2%}")


if __name__ == "__main__":
    main()
