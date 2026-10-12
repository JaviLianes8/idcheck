"""UUID validation, parsing, inspection and timestamps (RFC 9562)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ._errors import InvalidUUIDError, Reason
from ._time import to_datetime, uuid_time_ns
from ._uuid_text import UUIDForm, Variant, format_uuid, read_uuid, variant_of, version_nibble

_VERSIONS = frozenset(range(1, 9))
_MAX = (1 << 128) - 1


@dataclass(frozen=True, slots=True)
class UUIDInfo:
    """Everything idcheck can read from one UUID string. Immutable."""

    value: int
    """The 128-bit integer value."""
    canonical: str
    """Lowercase hyphenated text, the RFC 9562 Section 4 output form."""
    form: UUIDForm
    """The form the input was written in."""
    variant: Variant
    """The variant field (RFC 9562 Section 4.1)."""
    version: int | None
    """The version nibble when the variant is RFC 9562, else ``None`` (like ``uuid.UUID``)."""
    timestamp_ns: int | None
    """Unix epoch nanoseconds for v1, v6 and v7, else ``None``. v7 has millisecond precision."""

    @property
    def is_nil(self) -> bool:
        """True for the nil UUID, all 128 bits zero (RFC 9562 Section 5.9)."""
        return self.value == 0

    @property
    def is_max(self) -> bool:
        """True for the max UUID, all 128 bits one (RFC 9562 Section 5.10)."""
        return self.value == _MAX

    def __str__(self) -> str:
        return self.canonical


def _check_version_argument(version: int | None) -> None:
    if version is None:
        return
    if isinstance(version, bool) or not isinstance(version, int):
        raise TypeError("version must be an int")
    if version not in _VERSIONS:
        raise ValueError("version must be one of 1 through 8")


def _read(value: object, version: int | None, lenient: bool) -> tuple[int, UUIDForm] | Reason:
    _check_version_argument(version)
    result = read_uuid(value, lenient)
    if isinstance(result, Reason) or version is None:
        return result
    if variant_of(result[0]) is not Variant.RFC9562:
        return Reason.WRONG_VARIANT
    if version_nibble(result[0]) != version:
        return Reason.WRONG_VERSION
    return result


def _require(value: object, version: int | None, lenient: bool) -> tuple[int, UUIDForm]:
    result = _read(value, version, lenient)
    if isinstance(result, Reason):
        raise InvalidUUIDError(result, value)
    return result


def is_uuid(value: str, version: int | None = None, *, lenient: bool = False) -> bool:
    """Report whether ``value`` is a UUID string.

    By default only the canonical hyphenated form is accepted (any case). Unlike
    :class:`uuid.UUID`, this rejects braces, the ``urn:uuid:`` prefix and bare hex unless
    ``lenient=True``. With ``version`` given it also checks the version nibble and the
    RFC 9562 variant, so ``is_uuid(s, version=4)`` means a real version 4 UUID.

    Raises :class:`ValueError` if ``version`` is not 1 through 8, and :class:`TypeError`
    if it is not an int (booleans included).

    >>> is_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479", version=4)
    True
    >>> is_uuid("{f47ac10b-58cc-4372-a567-0e02b2c3d479}")
    False
    >>> is_uuid("{f47ac10b-58cc-4372-a567-0e02b2c3d479}", lenient=True)
    True
    """
    return not isinstance(_read(value, version, lenient), Reason)


def explain_uuid(
    value: object, version: int | None = None, *, lenient: bool = False
) -> Reason | None:
    """Return why ``value`` fails :func:`is_uuid` with the same options, or ``None``.

    >>> explain_uuid("f47ac10b58cc4372a5670e02b2c3d479")
    <Reason.FORM_NOT_ALLOWED: 'form_not_allowed'>
    >>> explain_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479") is None
    True
    """
    result = _read(value, version, lenient)
    return result if isinstance(result, Reason) else None


def parse_uuid(value: str, version: int | None = None, *, lenient: bool = False) -> int:
    """Decode a UUID string into its 128-bit integer value.

    Raises :class:`InvalidUUIDError` (a :class:`ValueError`) with a :class:`Reason`.

    >>> hex(parse_uuid("00000000-0000-0000-0000-0000000000ff"))
    '0xff'
    """
    return _require(value, version, lenient)[0]


def inspect_uuid(value: str, *, lenient: bool = False) -> UUIDInfo:
    """Parse ``value`` and return a frozen :class:`UUIDInfo` describing it.

    Raises :class:`InvalidUUIDError` with a :class:`Reason`.

    >>> info = inspect_uuid("017F22E2-79B0-7CC3-98C4-DC0C0C07398F")
    >>> info.version, info.variant.value, info.canonical
    (7, 'rfc9562', '017f22e2-79b0-7cc3-98c4-dc0c0c07398f')
    """
    number, form = _require(value, None, lenient)
    variant = variant_of(number)
    version = version_nibble(number) if variant is Variant.RFC9562 else None
    return UUIDInfo(
        value=number,
        canonical=format_uuid(number),
        form=form,
        variant=variant,
        version=version,
        timestamp_ns=uuid_time_ns(number, version),
    )


def uuid_timestamp_ns(value: str, *, lenient: bool = False) -> int:
    """Return the timestamp of a v1, v6 or v7 UUID as integer Unix nanoseconds.

    Exact: v1 and v6 count 100 ns ticks since 1582-10-15 (RFC 9562 Sections 5.1 and
    5.6), v7 counts Unix milliseconds (Section 5.7). Raises :class:`InvalidUUIDError`,
    with :attr:`Reason.NO_TIMESTAMP` for valid UUIDs of other versions.

    >>> uuid_timestamp_ns("017F22E2-79B0-7CC3-98C4-DC0C0C07398F")
    1645557742000000000
    """
    info = inspect_uuid(value, lenient=lenient)
    if info.timestamp_ns is None:
        raise InvalidUUIDError(Reason.NO_TIMESTAMP, value)
    return info.timestamp_ns


def uuid_timestamp(value: str, *, lenient: bool = False) -> datetime:
    """Return the timestamp of a v1, v6 or v7 UUID as an aware UTC datetime.

    Sub-microsecond ticks of v1 and v6 are floored. Raises :class:`InvalidUUIDError`
    like :func:`uuid_timestamp_ns`, and :class:`TimestampRangeError` when the instant is
    past ``datetime.max`` (possible for v7).

    >>> uuid_timestamp("C232AB00-9414-11EC-B3C8-9F6BDECED846").isoformat()
    '2022-02-22T19:22:22+00:00'
    """
    return to_datetime(uuid_timestamp_ns(value, lenient=lenient), value)
