"""Timestamp layouts of UUID v1, v6 and v7 (RFC 9562 Section 5) and datetime conversion."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ._errors import Reason, TimestampRangeError

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
# 100 ns ticks between the Gregorian epoch (1582-10-15) and the Unix epoch.
_GREGORIAN_OFFSET = 0x01B21DD213814000
_TICK_NS = 100
_MS_NS = 1_000_000


def uuid_time_ns(value: int, version: int | None) -> int | None:
    """Return Unix nanoseconds for a v1, v6 or v7 UUID integer, else ``None``."""
    if version == 1:
        ticks = ((value >> 64) & 0xFFF) << 48 | ((value >> 80) & 0xFFFF) << 32 | value >> 96
    elif version == 6:
        ticks = (value >> 96) << 28 | ((value >> 80) & 0xFFFF) << 12 | (value >> 64) & 0xFFF
    elif version == 7:
        return (value >> 80) * _MS_NS
    else:
        return None
    return (ticks - _GREGORIAN_OFFSET) * _TICK_NS


def to_datetime(nanoseconds: int, value: object) -> datetime:
    """Convert Unix nanoseconds to an aware UTC datetime, flooring to microseconds."""
    try:
        return _EPOCH + timedelta(microseconds=nanoseconds // 1000)
    except OverflowError:
        raise TimestampRangeError(Reason.TIMESTAMP_OUT_OF_RANGE, value) from None
