"""Reading UUID text: accepted forms, layout checks and the bit fields (RFC 9562)."""

from __future__ import annotations

from enum import Enum

from ._errors import Reason

_HEX = frozenset("0123456789abcdefABCDEF")
_HYPHENS = (8, 13, 18, 23)
_URN = "urn:uuid:"
_CANONICAL_LENGTH = 36
_HEX_LENGTH = 32


class UUIDForm(str, Enum):
    """The textual form a UUID was written in."""

    CANONICAL = "canonical"
    """``f47ac10b-58cc-4372-a567-0e02b2c3d479``: RFC 9562 Section 4, the only strict form."""
    BRACED = "braced"
    """``{f47ac10b-58cc-4372-a567-0e02b2c3d479}``: the registry style GUID form."""
    URN = "urn"
    """``urn:uuid:f47ac10b-58cc-4372-a567-0e02b2c3d479``: the URN namespace form."""
    HEX = "hex"
    """``f47ac10b58cc4372a5670e02b2c3d479``: 32 hex digits, no hyphens."""

    def __str__(self) -> str:
        return self.value


class Variant(str, Enum):
    """The variant field: the top bits of octet 8 (RFC 9562 Section 4.1)."""

    NCS = "ncs"
    """``0xxx``: reserved, NCS backward compatibility. The nil UUID has this variant."""
    RFC9562 = "rfc9562"
    """``10xx``: the variant defined by RFC 9562 (and RFC 4122 before it)."""
    MICROSOFT = "microsoft"
    """``110x``: reserved, Microsoft backward compatibility."""
    FUTURE = "future"
    """``111x``: reserved for future definition. The max UUID has this variant."""

    def __str__(self) -> str:
        return self.value


def read_uuid(value: object, lenient: bool) -> tuple[int, UUIDForm] | Reason:
    """Return the integer value and form of ``value``, or the first reason it fails."""
    if not isinstance(value, str):
        return Reason.NOT_A_STRING
    form, body = _unwrap(value)
    if form is UUIDForm.CANONICAL and len(body) == _HEX_LENGTH and "-" not in body:
        form = UUIDForm.HEX
        problem = None if all(char in _HEX for char in body) else Reason.BAD_CHARACTER
    elif len(body) == _CANONICAL_LENGTH:
        problem = _check_canonical(body)
    else:
        problem = Reason.BAD_LENGTH
    if problem is not None:
        return problem
    if form is not UUIDForm.CANONICAL and not lenient:
        return Reason.FORM_NOT_ALLOWED
    return int(body.replace("-", ""), 16), form


def _unwrap(value: str) -> tuple[UUIDForm, str]:
    if len(value) >= 2 and value[0] == "{" and value[-1] == "}":
        return UUIDForm.BRACED, value[1:-1]
    if value[: len(_URN)].lower() == _URN:
        return UUIDForm.URN, value[len(_URN) :]
    return UUIDForm.CANONICAL, value


def _check_canonical(body: str) -> Reason | None:
    if any(char not in _HEX and char != "-" for char in body):
        return Reason.BAD_CHARACTER
    hyphens = tuple(index for index, char in enumerate(body) if char == "-")
    if hyphens != _HYPHENS:
        return Reason.BAD_LAYOUT
    return None


def format_uuid(value: int) -> str:
    """Return the canonical lowercase hyphenated text of a 128-bit integer."""
    digits = f"{value:032x}"
    return f"{digits[:8]}-{digits[8:12]}-{digits[12:16]}-{digits[16:20]}-{digits[20:]}"


def variant_of(value: int) -> Variant:
    """Decode the variant from the top three bits of octet 8."""
    top = (value >> 61) & 0b111
    if top < 0b100:
        return Variant.NCS
    if top < 0b110:
        return Variant.RFC9562
    if top == 0b110:
        return Variant.MICROSOFT
    return Variant.FUTURE


def version_nibble(value: int) -> int:
    """Return the four version bits (the high nibble of octet 6)."""
    return (value >> 76) & 0xF
