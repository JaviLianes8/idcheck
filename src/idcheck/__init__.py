"""Strict validation and parsing of UUID and ULID identifier strings."""

from __future__ import annotations

from ._ulid import is_ulid, parse_ulid, ulid_timestamp
from ._uuid import is_uuid

__version__ = "0.1.0"

__all__ = ["is_ulid", "is_uuid", "parse_ulid", "ulid_timestamp"]
