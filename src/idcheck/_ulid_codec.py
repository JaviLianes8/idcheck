"""Crockford base32 reading and writing for 128-bit ULID values."""

from __future__ import annotations

from ._errors import InvalidULIDError, Reason

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
LENGTH = 26
TIME_SHIFT = 80
RANDOM_MASK = (1 << 80) - 1
MAX_TIMESTAMP = (1 << 48) - 1
MAX_VALUE = (1 << 128) - 1
_DECODE = {char: index for index, char in enumerate(ALPHABET)}
# Crockford's decoding aliases: I and L read as 1, O reads as 0.
_ALIASES = {"I": "1", "L": "1", "O": "0"}


def read_ulid(value: object, lenient: bool) -> int | Reason:
    """Return the 128-bit value of ``value``, or the first reason it is not a ULID."""
    if not isinstance(value, str):
        return Reason.NOT_A_STRING
    if len(value) != LENGTH:
        return Reason.BAD_LENGTH
    if not value.isascii():
        # str.upper() maps some non-ASCII letters onto the alphabet (for example U+017F).
        return Reason.BAD_CHARACTER
    upper = value.upper()
    if lenient:
        upper = "".join(_ALIASES.get(char, char) for char in upper)
    result = 0
    for char in upper:
        digit = _DECODE.get(char)
        if digit is None:
            return Reason.BAD_CHARACTER
        result = result * 32 + digit
    if result > MAX_VALUE:
        return Reason.OUT_OF_RANGE
    return result


def require_ulid(value: object, lenient: bool) -> int:
    """Like :func:`read_ulid`, but raise :class:`InvalidULIDError` on failure."""
    result = read_ulid(value, lenient)
    if isinstance(result, Reason):
        raise InvalidULIDError(result, value)
    return result


def check_int(value: object, maximum: int, name: str) -> int:
    """Return ``value`` if it is an int in ``0..maximum``, else raise."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int")
    if not 0 <= value <= maximum:
        raise InvalidULIDError(Reason.OUT_OF_RANGE, value, f"{name} out of range")
    return value


def write_ulid(value: int) -> str:
    """Encode an in-range integer as 26 uppercase Crockford base32 characters."""
    chars = []
    for _ in range(LENGTH):
        chars.append(ALPHABET[value & 31])
        value >>= 5
    return "".join(reversed(chars))
