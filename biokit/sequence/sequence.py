"""The :class:`BioSequence` base class."""

from __future__ import annotations

from collections.abc import Iterator
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, TypeVar

from biokit.exceptions import InvalidSequenceError
from biokit.statistics.sequence_stats import gc_fraction, molecular_weight_daltons

if TYPE_CHECKING:
    from Bio.SeqRecord import SeqRecord

#: Type variable bound to :class:`BioSequence`, used for ``__getitem__`` and
#: other methods that return ``type(self)`` rather than the base class.
T = TypeVar("T", bound="BioSequence")


class SequenceType(str, Enum):
    """Inferred sequence type."""

    DNA = "DNA"
    RNA = "RNA"
    PROTEIN = "PROTEIN"
    UNKNOWN = "UNKNOWN"


class BioSequence:
    """A biological sequence value type.

    Wraps a string sequence with type information and common operations.
    Subclasses :class:`DNA`, :class:`RNA`, :class:`Protein` add
    alphabet-specific validation and operations.

    Parameters
    ----------
    sequence : str
        The biological sequence. Will be upper-cased.
    id : str, optional
        Identifier for the sequence (e.g. accession number).
    description : str, optional
        Human-readable description.

    Examples
    --------
    >>> from biokit.sequence import DNA
    >>> seq = DNA("ATGGCAGGT")
    >>> seq.length
    9
    >>> seq.gc_content
    0.5555555555555556
    >>> str(seq)
    'ATGGCAGGT'
    """

    # ``__dict__`` is required for ``functools.cached_property`` to work
    # (gc_content, molecular_weight). ``__weakref__`` is required for the
    # weak-reference pattern used by some downstream consumers.
    __slots__ = ("__dict__", "__weakref__", "_description", "_id", "_sequence")

    #: Subclasses override this with the IUPAC alphabet (frozenset of valid chars).
    alphabet: frozenset[str] = frozenset()

    def __init__(self, sequence: str, *, id: str = "", description: str = "") -> None:
        if not isinstance(sequence, str):
            raise TypeError(f"sequence must be str, got {type(sequence).__name__}")
        if not sequence:
            raise InvalidSequenceError("sequence must be non-empty")
        seq_upper = sequence.upper()
        self._validate_alphabet(seq_upper)
        self._sequence: str = seq_upper
        self._id: str = id
        self._description: str = description

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @classmethod
    def _validate_alphabet(cls, sequence: str) -> None:
        """Validate that ``sequence`` only contains characters in ``cls.alphabet``."""
        if not cls.alphabet:
            return  # Base class — no validation
        invalid = set(sequence) - cls.alphabet
        if invalid:
            raise InvalidSequenceError(f"invalid character(s) for {cls.__name__}: {invalid!r}")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def sequence(self) -> str:
        """The raw sequence string."""
        return self._sequence

    @property
    def id(self) -> str:
        """Sequence identifier."""
        return self._id

    @property
    def description(self) -> str:
        """Human-readable description."""
        return self._description

    @property
    def length(self) -> int:
        """Sequence length."""
        return len(self._sequence)

    @cached_property
    def gc_content(self) -> float:
        """GC fraction in ``[0, 1]``. Returns 0.0 for non-nucleotide sequences."""
        return gc_fraction(self._sequence)

    @cached_property
    def molecular_weight(self) -> float:
        """Molecular weight in Daltons (approximate)."""
        return molecular_weight_daltons(self._sequence)

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return self._sequence

    def __repr__(self) -> str:
        return f"{type(self).__name__}(sequence={self._sequence!r}, id={self._id!r})"

    def __len__(self) -> int:
        return len(self._sequence)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BioSequence):
            return NotImplemented
        return type(self) is type(other) and self._sequence == other._sequence

    def __hash__(self) -> int:
        return hash((type(self).__name__, self._sequence))

    def __iter__(self) -> Iterator[str]:
        return iter(self._sequence)

    def __getitem__(self: T, index: int | slice) -> T:
        return type(self)(self._sequence[index], id=self._id, description=self._description)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def count(self, sub: str) -> int:
        """Count non-overlapping occurrences of ``sub``."""
        return self._sequence.count(sub.upper())

    def to_seqrecord(self) -> SeqRecord:
        """Convert to a Biopython :class:`SeqRecord`."""
        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord

        return SeqRecord(
            Seq(self._sequence), id=self._id or "biokit", description=self._description
        )

    def to_fasta(self, line_width: int = 70) -> str:
        """Render as FASTA text."""
        header = f">{self._id or 'biokit'}" + (f" {self._description}" if self._description else "")
        seq = self._sequence
        lines = [seq[i : i + line_width] for i in range(0, len(seq), line_width)]
        return header + "\n" + "\n".join(lines) + "\n"


__all__ = ["BioSequence", "SequenceType"]
