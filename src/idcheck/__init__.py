"""Strict validation and parsing of UUID and ULID identifier strings."""

from __future__ import annotations

from ._convert import encode_ulid, increment_ulid, ulid_from_parts, ulid_to_uuid, uuid_to_ulid
from ._errors import (
    IdCheckError,
    InvalidULIDError,
    InvalidUUIDError,
    Reason,
    TimestampRangeError,
    ULIDOverflowError,
)
from ._ulid import (
    ULIDInfo,
    explain_ulid,
    inspect_ulid,
    is_ulid,
    parse_ulid,
    ulid_timestamp,
    ulid_timestamp_ms,
)
from ._uuid import (
    UUIDInfo,
    explain_uuid,
    inspect_uuid,
    is_uuid,
    parse_uuid,
    uuid_timestamp,
    uuid_timestamp_ns,
)
from ._uuid_text import UUIDForm, Variant

__version__ = "0.2.0"

__all__ = [
    "IdCheckError",
    "InvalidULIDError",
    "InvalidUUIDError",
    "Reason",
    "TimestampRangeError",
    "ULIDInfo",
    "ULIDOverflowError",
    "UUIDForm",
    "UUIDInfo",
    "Variant",
    "encode_ulid",
    "explain_ulid",
    "explain_uuid",
    "increment_ulid",
    "inspect_ulid",
    "inspect_uuid",
    "is_ulid",
    "is_uuid",
    "parse_ulid",
    "parse_uuid",
    "ulid_from_parts",
    "ulid_timestamp",
    "ulid_timestamp_ms",
    "ulid_to_uuid",
    "uuid_timestamp",
    "uuid_timestamp_ns",
    "uuid_to_ulid",
]
