"""Intelligence layer — interpretation, validation, reasoning, hypothesis, explanation.

Each intelligence module is a small, focused component that produces an
:class:`Interpretation` (or registers claims in the Claim Graph) in
response to a question or input. Modules never call BioKit directly;
they consume BioKit outputs that have been registered as evidence in
the Engine.
"""

from __future__ import annotations

from nexus.intelligence.base import IntelligenceModule
from nexus.intelligence.explanation import ExplanationModule
from nexus.intelligence.hypothesis import HypothesisModule
from nexus.intelligence.interpretation import InterpretationModule
from nexus.intelligence.reasoning import ReasoningModule
from nexus.intelligence.validation import ValidationModule

__all__ = [
    "ExplanationModule",
    "HypothesisModule",
    "IntelligenceModule",
    "InterpretationModule",
    "ReasoningModule",
    "ValidationModule",
]
