"""BioSequence: BioKit's canonical sequence value type.

A :class:`BioSequence` is a frozen, hashable, type-safe wrapper around a
biological sequence string. Subclasses :class:`DNA`, :class:`RNA` and
:class:`Protein` add alphabet validation and operations specific to each
molecule type.

The design is intentionally lightweight — we don't try to replace Biopython's
:class:`Seq` / :class:`SeqRecord`, but rather provide a small, fast, well-typed
value object for use inside BioKit. Interop with Biopython is provided via
:meth:`BioSequence.to_seqrecord`.

Example
-------
>>> from biokit.sequence import DNA, RNA, Protein
>>> dna = DNA("ATGGCAGGTGACCCGTGA")
>>> dna.gc_content
0.5555555555555556
>>> dna.transcribe().sequence
'AUGGCAGGUGACCCGUGA'
>>> dna.translate().sequence
'MAGDP'
"""

from __future__ import annotations

from biokit.sequence.dna import DNA
from biokit.sequence.protein import Protein
from biokit.sequence.rna import RNA
from biokit.sequence.sequence import BioSequence, SequenceType
from biokit.sequence.validation import (
    is_dna,
    is_protein,
    is_rna,
    validate_dna,
    validate_protein,
    validate_rna,
)

__all__ = [
    "DNA",
    "RNA",
    "BioSequence",
    "Protein",
    "SequenceType",
    "is_dna",
    "is_protein",
    "is_rna",
    "validate_dna",
    "validate_protein",
    "validate_rna",
]
