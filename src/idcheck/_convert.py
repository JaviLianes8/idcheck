"""Encoding ULIDs from integers or parts, the monotonic increment, and UUID conversion."""

from __future__ import annotations

from ._errors import Reason, ULIDOverflowError
from ._ulid_codec import (
    MAX_TIMESTAMP,
    MAX_VALUE,
    RANDOM_MASK,
    TIME_SHIFT,
    check_int,
    require_ulid,
    write_ulid,
)
from ._uuid import parse_uuid
from ._uuid_text import format_uuid


def encode_ulid(value: int) -> str:
    """Encode a 128-bit integer as a canonical uppercase ULID string.

    Raises :class:`TypeError` for a non-int and :class:`InvalidULIDError` with
    :attr:`Reason.OUT_OF_RANGE` outside ``0 .. 2**128 - 1``.

    >>> encode_ulid(31)
    '0000000000000000000000000Z'
    """
    return write_ulid(check_int(value, MAX_VALUE, "value"))


def ulid_from_parts(timestamp_ms: int, randomness: int = 0) -> str:
    """Build a ULID from a 48-bit millisecond timestamp and 80 bits of randomness.

    The caller supplies both parts, so this never reads a clock or a random source.
    Raises like :func:`encode_ulid` when a part is out of range.

    >>> ulid_from_parts(1469922850259)
    '01ARZ3NDEK0000000000000000'
    """
    stamp = check_int(timestamp_ms, MAX_TIMESTAMP, "timestamp_ms")
    random_part = check_int(randomness, RANDOM_MASK, "randomness")
    return write_ulid(stamp << TIME_SHIFT | random_part)


def increment_ulid(value: str, *, lenient: bool = False) -> str:
    """Return the next ULID in the same millisecond, per the spec's monotonicity rule.

    The 80-bit randomness is incremented by one in its least significant bit and the
    timestamp is kept. Raises :class:`ULIDOverflowError` when the randomness is already
    all ones, as the spec requires generation to fail rather than wrap.

    >>> increment_ulid("01ARZ3NDEK0000000000000000")
    '01ARZ3NDEK0000000000000001'
    """
    number = require_ulid(value, lenient)
    if number & RANDOM_MASK == RANDOM_MASK:
        raise ULIDOverflowError(Reason.OVERFLOW, value)
    return write_ulid(number + 1)


def uuid_to_ulid(value: str, *, lenient: bool = False) -> str:
    """Convert a UUID string to the ULID with the same 128 bits.

    Lossless. A UUIDv7 keeps its timestamp, because both formats start with 48 bits of
    Unix milliseconds. Raises :class:`InvalidUUIDError` for a bad UUID.

    >>> uuid_to_ulid("017F22E2-79B0-7CC3-98C4-DC0C0C07398F")
    '01FWHE4YDGFK1SHH6W1G60EECF'
    """
    return write_ulid(parse_uuid(value, lenient=lenient))


def ulid_to_uuid(value: str, *, lenient: bool = False) -> str:
    """Convert a ULID string to the canonical lowercase UUID text with the same 128 bits.

    Lossless, but the result usually has no valid RFC 9562 version or variant, since a
    ULID puts randomness where those fields live. Raises :class:`InvalidULIDError`.

    >>> ulid_to_uuid("01ARZ3NDEKTSV4RRFFQ69G5FAV")
    '01563e3a-b5d3-d676-4c61-efb99302bd5b'
    """
    return format_uuid(require_ulid(value, lenient))
