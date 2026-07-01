"""Report generator — produce publication-quality reports from interpretations."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from nexus.core.types import Interpretation


@dataclass
class ReportSection:
    """A single section of a report."""

    title: str
    body: str
    citations: list[str] = field(default_factory=list)
    confidence: float | None = None


@dataclass
class Report:
    """A structured report composed of sections."""

    title: str
    sections: list[ReportSection] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_markdown(self) -> str:
        """Render the report as Markdown."""
        lines: list[str] = [f"# {self.title}", ""]
        for section in self.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            lines.append(section.body)
            if section.confidence is not None:
                lines.append("")
                lines.append(f"*Confidence: {section.confidence:.2f}*")
            if section.citations:
                lines.append("")
                lines.append("**Citations:**")
                for i, c in enumerate(section.citations, 1):
                    lines.append(f"{i}. {c}")
            lines.append("")
        return "\n".join(lines)

    def to_text(self) -> str:
        """Render the report as plain text."""
        lines: list[str] = [self.title, "=" * len(self.title), ""]
        for section in self.sections:
            lines.append(section.title)
            lines.append("-" * len(section.title))
            lines.append(section.body)
            if section.confidence is not None:
                lines.append(f"Confidence: {section.confidence:.2f}")
            if section.citations:
                lines.append("Citations:")
                for i, c in enumerate(section.citations, 1):
                    lines.append(f"  {i}. {c}")
            lines.append("")
        return "\n".join(lines)


class ReportGenerator:
    """Builds a :class:`Report` from one or more :class:`Interpretation` objects."""

    def generate(
        self,
        title: str,
        interpretations: list[Interpretation],
        metadata: dict[str, Any] | None = None,
    ) -> Report:
        sections: list[ReportSection] = []

        # Summary section.
        summary_parts: list[str] = []
        for i, interp in enumerate(interpretations, 1):
            summary_parts.append(f"{i}. {interp.answer}")
        sections.append(
            ReportSection(
                title="Summary",
                body="\n".join(summary_parts) or "No findings to report.",
            )
        )

        # Per-interpretation sections.
        for i, interp in enumerate(interpretations, 1):
            body_parts: list[str] = []
            if interp.inference:
                body_parts.append(f"Inference: {interp.inference}")
            if interp.explanation:
                body_parts.append(f"Explanation: {interp.explanation}")
            if interp.alternatives:
                body_parts.append("Alternatives considered:")
                for alt in interp.alternatives:
                    body_parts.append(f"  - {alt}")
            if interp.contradictions:
                body_parts.append("Contradictions / caveats:")
                for c in interp.contradictions:
                    body_parts.append(f"  - {c}")
            if interp.recommended_next_step:
                body_parts.append(f"Recommended next step: {interp.recommended_next_step}")

            sections.append(
                ReportSection(
                    title=f"Finding {i}",
                    body="\n".join(body_parts),
                    citations=interp.citations,
                    confidence=interp.confidence.value,
                )
            )

        # Methods section.
        methods_parts: list[str] = []
        provider_models = list(
            {interp.provider_model for interp in interpretations if interp.provider_model}
        )
        if provider_models:
            methods_parts.append("LLM providers/models used:")
            for pm in provider_models:
                methods_parts.append(f"  - {pm}")
        methods_parts.append(
            f"Total interpretations: {len(interpretations)}; "
            f"total evidence entries cited: "
            f"{sum(len(i.evidence_ids) for i in interpretations)}."
        )
        sections.append(ReportSection(title="Methods", body="\n".join(methods_parts)))

        return Report(
            title=title,
            sections=sections,
            metadata=metadata or {},
        )


__all__ = ["Report", "ReportGenerator", "ReportSection"]
