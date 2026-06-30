"""Shared exception hierarchy for BioKit 2.0.

All BioKit exceptions inherit from :class:`BioKitError` so callers can
catch any BioKit failure with a single ``except`` clause while still
being able to distinguish module-specific issues.

Hierarchy::

    BioKitError
    ├── InvalidFormatError       # file/string not in expected format
    ├── InvalidSequenceError     # alphabet violation
    ├── AnnotationError          # malformed feature/location
    ├── AssemblyError            # assembly cannot produce contigs
    ├── BlastError               # BLAST parsing or invocation failure
    ├── PrimerError              # no primer satisfies constraints
    ├── RNAError                 # transcription/translation input invalid
    ├── StructuralError          # malformed PDB input
    ├── PopGenError              # invalid population genetics input
    ├── CRISPRError              # invalid guide / scoring failure
    ├── VisualizationError       # plotting failure
    └── Machine-learning
        ├── ValidationError      # ML input validation failure
        ├── NotFittedError       # transform/predict before fit
        ├── ConvergenceError     # iterative algorithm did not converge
        └── EncodingError        # sequence/label encoding failure
"""

from __future__ import annotations


class BioKitError(Exception):
    """Base class for every BioKit-specific exception."""


# Bioinformatics exceptions --------------------------------------------------


class InvalidFormatError(BioKitError):
    """Raised when a file or string does not match the expected format."""


class InvalidSequenceError(BioKitError):
    """Raised when a sequence contains characters outside the expected alphabet."""


class AnnotationError(BioKitError):
    """Raised by the annotation module for malformed features or locations."""


class AssemblyError(BioKitError):
    """Raised by the assembly module when contigs cannot be produced."""


class BlastError(BioKitError):
    """Raised by the BLAST module for parsing or invocation failures."""


class PrimerError(BioKitError):
    """Raised by the primer module when no primer satisfies the constraints."""


class RNAError(BioKitError):
    """Raised by the RNA module for invalid transcription/translation input."""


class StructuralError(BioKitError):
    """Raised by the structural module for malformed PDB input."""


class PopGenError(BioKitError):
    """Raised by the population genetics module for invalid input data."""


class CRISPRError(BioKitError):
    """Raised by the CRISPR module for invalid guide input or scoring failure."""


class VisualizationError(BioKitError):
    """Raised by the visualization module when plotting fails."""


# Machine-learning exceptions -----------------------------------------------


class ValidationError(BioKitError):
    """Raised when ML input fails validation (wrong shape, dtype, NaN, etc.)."""


class NotFittedError(BioKitError):
    """Raised when ``transform``/``predict`` is called before ``fit``.

    Mirrors :class:`sklearn.exceptions.NotFittedError` so callers that
    already catch the sklearn version can also catch this one by name.
    """


class ConvergenceError(BioKitError):
    """Raised when an iterative ML algorithm fails to converge."""


class EncodingError(BioKitError):
    """Raised by sequence/label encoders when the input cannot be encoded."""


__all__ = [
    "AnnotationError",
    "AssemblyError",
    "BioKitError",
    "BlastError",
    "CRISPRError",
    "ConvergenceError",
    "EncodingError",
    "InvalidFormatError",
    "InvalidSequenceError",
    "NotFittedError",
    "PopGenError",
    "PrimerError",
    "RNAError",
    "StructuralError",
    "ValidationError",
    "VisualizationError",
]
