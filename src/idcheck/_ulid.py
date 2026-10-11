"""ULID string validation and parsing (Crockford base32, no generation)."""

from __future__ import annotations

from datetime import datetime, timezone

_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_DECODE = {char: index for index, char in enumerate(_ALPHABET)}
_LENGTH = 26
_TIME_SHIFT = 80


def is_ulid(value: str) -> bool:
    """Report whether ``value`` is a canonical 26 character Crockford ULID string.

    Case insensitive. Rejects the ambiguous letters ``I``, ``L``, ``O`` and ``U``
    and any first character above ``7`` (which would overflow 128 bits).
    """
    if not isinstance(value, str) or len(value) != _LENGTH:
        return False
    upper = value.upper()
    if any(char not in _DECODE for char in upper):
        return False
    return _DECODE[upper[0]] < 8


def parse_ulid(value: str) -> int:
    """Decode a ULID string into its 128 bit integer value.

    Raises :class:`ValueError` if ``value`` is not a valid ULID.
    """
    if not is_ulid(value):
        raise ValueError("not a valid ULID string")
    result = 0
    for char in value.upper():
        result = result * 32 + _DECODE[char]
    return result


def ulid_timestamp(value: str) -> datetime:
    """Return the UTC timestamp encoded in a ULID's first 48 bits.

    Raises :class:`ValueError` if ``value`` is not a valid ULID.
    """
    milliseconds = parse_ulid(value) >> _TIME_SHIFT
    return datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc)
