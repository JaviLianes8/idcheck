"""ULID string validation, parsing and inspection (Crockford base32, no generation)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ._errors import Reason
from ._time import to_datetime
from ._ulid_codec import RANDOM_MASK, TIME_SHIFT, read_ulid, require_ulid, write_ulid

_MS_NS = 1_000_000


@dataclass(frozen=True, slots=True)
class ULIDInfo:
    """Everything idcheck can read from one ULID string. Immutable."""

    value: int
    """The 128-bit integer value."""
    canonical: str
    """Uppercase Crockford base32 text, 26 characters."""
    timestamp_ms: int
    """The first 48 bits: milliseconds since the Unix epoch."""
    randomness: int
    """The last 80 bits."""

    def __str__(self) -> str:
        return self.canonical


def is_ulid(value: str, *, lenient: bool = False) -> bool:
    """Report whether ``value`` is a 26 character Crockford base32 ULID string.

    Case insensitive. Rejects the excluded letters ``I``, ``L``, ``O`` and ``U`` and any
    first character above ``7`` (which would overflow 128 bits). With ``lenient=True``,
    ``I`` and ``L`` are read as ``1`` and ``O`` as ``0``, as Crockford's decoding allows.

    >>> is_ulid("01ARZ3NDEKTSV4RRFFQ69G5FAV")
    True
    >>> is_ulid("8ZZZZZZZZZZZZZZZZZZZZZZZZZ")
    False
    """
    return not isinstance(read_ulid(value, lenient), Reason)


def explain_ulid(value: object, *, lenient: bool = False) -> Reason | None:
    """Return why ``value`` fails :func:`is_ulid` with the same options, or ``None``.

    >>> explain_ulid("01ARZ3NDEKTSV4RRFFQ69G5FAU")
    <Reason.BAD_CHARACTER: 'bad_character'>
    """
    result = read_ulid(value, lenient)
    return result if isinstance(result, Reason) else None


def parse_ulid(value: str, *, lenient: bool = False) -> int:
    """Decode a ULID string into its 128-bit integer value.

    Raises :class:`InvalidULIDError` (a :class:`ValueError`) with a :class:`Reason`.

    >>> parse_ulid("0000000000000000000000000Z")
    31
    """
    return require_ulid(value, lenient)


def inspect_ulid(value: str, *, lenient: bool = False) -> ULIDInfo:
    """Parse ``value`` and return a frozen :class:`ULIDInfo` describing it.

    Raises :class:`InvalidULIDError` with a :class:`Reason`.

    >>> inspect_ulid("01ARZ3NDEKTSV4RRFFQ69G5FAV").timestamp_ms
    1469922850259
    """
    number = require_ulid(value, lenient)
    return ULIDInfo(
        value=number,
        canonical=write_ulid(number),
        timestamp_ms=number >> TIME_SHIFT,
        randomness=number & RANDOM_MASK,
    )


def ulid_timestamp_ms(value: str, *, lenient: bool = False) -> int:
    """Return the 48-bit timestamp of a ULID as integer Unix milliseconds.

    Works over the whole range, including instants past ``datetime.max``.

    >>> ulid_timestamp_ms("7ZZZZZZZZZZZZZZZZZZZZZZZZZ")
    281474976710655
    """
    return require_ulid(value, lenient) >> TIME_SHIFT


def ulid_timestamp(value: str, *, lenient: bool = False) -> datetime:
    """Return the UTC timestamp encoded in a ULID's first 48 bits.

    Raises :class:`InvalidULIDError` for a bad ULID and :class:`TimestampRangeError` when
    the instant is past ``datetime.max`` (the 48-bit range reaches year 10889).

    >>> ulid_timestamp("01ARZ3NDEKTSV4RRFFQ69G5FAV").isoformat()
    '2016-07-30T23:54:10.259000+00:00'
    """
    return to_datetime(ulid_timestamp_ms(value, lenient=lenient) * _MS_NS, value)
