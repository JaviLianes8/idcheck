"""Strict UUID string validation."""

from __future__ import annotations

import re

_CANONICAL = re.compile(
    r"\A[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\Z"
)
_VERSION_INDEX = 14
_VARIANT_INDEX = 19
_RFC_VARIANT = frozenset("89ab")
_VERSIONS = frozenset(range(1, 9))


def is_uuid(value: str, version: int | None = None) -> bool:
    """Report whether ``value`` is a canonical hyphenated UUID string.

    Unlike :class:`uuid.UUID`, this rejects braces, the ``urn:`` prefix and bare
    hex. With ``version`` given it also checks the version nibble and the RFC 4122
    variant, so ``is_uuid(s, version=4)`` means a real version 4 UUID.
    """
    if not isinstance(value, str):
        return False
    if _CANONICAL.match(value) is None:
        return False
    if version is None:
        return True
    if version not in _VERSIONS:
        raise ValueError("version must be one of 1 through 8")
    if int(value[_VERSION_INDEX], 16) != version:
        return False
    return value[_VARIANT_INDEX].lower() in _RFC_VARIANT
