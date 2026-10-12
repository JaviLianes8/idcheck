"""The work behind each command line subcommand, one identifier at a time."""

from __future__ import annotations

import json
from typing import Literal

from ._convert import ulid_to_uuid, uuid_to_ulid
from ._errors import InvalidUUIDError, Reason, TimestampRangeError
from ._time import to_datetime
from ._ulid import explain_ulid, inspect_ulid
from ._uuid import explain_uuid, inspect_uuid

Kind = Literal["auto", "uuid", "ulid"]
_ULID_LENGTH = 26
_MS_NS = 1_000_000


def detect(text: str, kind: Kind) -> Literal["uuid", "ulid"]:
    """Pick the format: forced by ``kind``, else 26 characters means ULID."""
    if kind != "auto":
        return kind
    return "ulid" if len(text) == _ULID_LENGTH else "uuid"


def validate(text: str, kind: Kind, lenient: bool, version: int | None) -> tuple[bool, str]:
    """Return ``(ok, line)`` where line is ``valid<TAB>kind<TAB>id`` or the reason."""
    chosen = detect(text, kind)
    if chosen == "ulid":
        reason = explain_ulid(text, lenient=lenient)
    else:
        reason = explain_uuid(text, version, lenient=lenient)
    if reason is None:
        return True, f"valid\t{chosen}\t{text}"
    return False, f"invalid\t{reason.value}\t{text}"


def _iso(nanoseconds: int | None, text: str) -> str | None:
    if nanoseconds is None:
        return None
    try:
        return to_datetime(nanoseconds, text).isoformat()
    except TimestampRangeError:
        return None


def inspect(text: str, kind: Kind, lenient: bool) -> str:
    """Return one JSON object describing ``text``. Raises :class:`IdCheckError`."""
    record: dict[str, object] = {"input": text}
    if detect(text, kind) == "ulid":
        info = inspect_ulid(text, lenient=lenient)
        record.update(
            kind="ulid",
            canonical=info.canonical,
            uuid=ulid_to_uuid(info.canonical),
            timestamp_ms=info.timestamp_ms,
            timestamp=_iso(info.timestamp_ms * _MS_NS, text),
            randomness_hex=f"{info.randomness:020x}",
        )
    else:
        uinfo = inspect_uuid(text, lenient=lenient)
        record.update(
            kind="uuid",
            canonical=uinfo.canonical,
            form=uinfo.form.value,
            variant=uinfo.variant.value,
            version=uinfo.version,
            nil=uinfo.is_nil,
            max=uinfo.is_max,
            timestamp_ns=uinfo.timestamp_ns,
            timestamp=_iso(uinfo.timestamp_ns, text),
            ulid=uuid_to_ulid(uinfo.canonical),
        )
    return json.dumps(record)


def convert(text: str, kind: Kind, lenient: bool) -> str:
    """Return the other format with the same 128 bits. Raises :class:`IdCheckError`."""
    if detect(text, kind) == "ulid":
        return ulid_to_uuid(text, lenient=lenient)
    return uuid_to_ulid(text, lenient=lenient)


def timestamp(text: str, kind: Kind, lenient: bool, unix_ns: bool) -> str:
    """Return the embedded time as ISO 8601 UTC, or integer Unix nanoseconds."""
    if detect(text, kind) == "ulid":
        nanoseconds = inspect_ulid(text, lenient=lenient).timestamp_ms * _MS_NS
    else:
        found = inspect_uuid(text, lenient=lenient).timestamp_ns
        if found is None:
            raise InvalidUUIDError(Reason.NO_TIMESTAMP, text)
        nanoseconds = found
    if unix_ns:
        return str(nanoseconds)
    return to_datetime(nanoseconds, text).isoformat()
