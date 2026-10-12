"""Rejection reasons and the typed error hierarchy."""

from __future__ import annotations

from enum import Enum


class Reason(str, Enum):
    """Why a value was rejected. The string value is stable and safe to show or log."""

    NOT_A_STRING = "not_a_string"
    """The value is not a ``str``."""
    BAD_LENGTH = "bad_length"
    """The text (after removing an accepted wrapper) has the wrong number of characters."""
    BAD_CHARACTER = "bad_character"
    """A character falls outside the alphabet (hex digits, or Crockford base32)."""
    BAD_LAYOUT = "bad_layout"
    """The UUID hyphens are not at positions 8, 13, 18 and 23."""
    FORM_NOT_ALLOWED = "form_not_allowed"
    """A braced, ``urn:uuid:`` or bare hex UUID was given without ``lenient=True``."""
    WRONG_VARIANT = "wrong_variant"
    """A version was required but the variant bits are not the RFC 9562 ones (``10``)."""
    WRONG_VERSION = "wrong_version"
    """The version nibble differs from the requested version."""
    OUT_OF_RANGE = "out_of_range"
    """The value does not fit: a ULID above ``7ZZZZZZZZZZZZZZZZZZZZZZZZZ`` or a bad integer."""
    NO_TIMESTAMP = "no_timestamp"
    """The UUID is valid but its layout carries no timestamp (only v1, v6 and v7 do)."""
    TIMESTAMP_OUT_OF_RANGE = "timestamp_out_of_range"
    """The instant is valid but outside what :class:`datetime.datetime` can represent."""
    OVERFLOW = "overflow"
    """Incrementing the 80-bit ULID randomness would overflow."""

    @property
    def description(self) -> str:
        """A short human readable sentence for this reason."""
        return _MESSAGES[self]


class IdCheckError(ValueError):
    """Base class of every error raised by idcheck.

    It is a :class:`ValueError`, so ``except ValueError`` keeps working. ``reason`` says
    what went wrong and ``value`` holds the offending input.
    """

    def __init__(self, reason: Reason, value: object, message: str | None = None) -> None:
        shown = repr(value)
        if len(shown) > 60:
            shown = shown[:57] + "..."
        super().__init__(message or f"{reason.description}: {shown}")
        self.reason = reason
        self.value = value


class InvalidUUIDError(IdCheckError):
    """The input is not an acceptable UUID for the requested operation."""


class InvalidULIDError(IdCheckError):
    """The input is not an acceptable ULID (string, integer or parts)."""


class TimestampRangeError(IdCheckError):
    """The decoded instant cannot be expressed as a :class:`datetime.datetime`."""


class ULIDOverflowError(IdCheckError):
    """The ULID randomness is already at its maximum, so it cannot be incremented."""


_MESSAGES = {
    Reason.NOT_A_STRING: "expected a str",
    Reason.BAD_LENGTH: "wrong length",
    Reason.BAD_CHARACTER: "invalid character",
    Reason.BAD_LAYOUT: "hyphens must be at positions 8, 13, 18 and 23",
    Reason.FORM_NOT_ALLOWED: "braced, urn:uuid: and bare hex forms need lenient=True",
    Reason.WRONG_VARIANT: "variant bits are not the RFC 9562 variant",
    Reason.WRONG_VERSION: "version does not match",
    Reason.OUT_OF_RANGE: "value out of range",
    Reason.NO_TIMESTAMP: "this UUID version carries no timestamp",
    Reason.TIMESTAMP_OUT_OF_RANGE: "timestamp outside the datetime range",
    Reason.OVERFLOW: "ULID randomness would overflow",
}
