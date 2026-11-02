"""External consumer used before and after upgrading the installed package."""

from __future__ import annotations

import json
import random
import uuid

import idcheck as lib


def snapshot() -> dict[str, object]:
    """Return reproducible results covering valid data, options and rejection reasons."""
    rng = random.Random(1000)
    records: list[object] = []
    for _ in range(100):
        number = rng.getrandbits(128)
        text = str(uuid.UUID(int=number))
        ulid = lib.encode_ulid(number)
        ui, li = lib.inspect_uuid(text), lib.inspect_ulid(ulid)
        records.append([ui.value, ui.canonical, ui.form, ui.variant, ui.version, ui.timestamp_ns])
        records.append([li.value, li.canonical, li.timestamp_ms, li.randomness])
        assert lib.is_uuid(text) and lib.is_ulid(ulid)
        assert lib.parse_uuid(text) == lib.parse_ulid(ulid) == number
        assert lib.ulid_from_parts(li.timestamp_ms, li.randomness) == ulid
        assert lib.uuid_to_ulid(text) == ulid and lib.ulid_to_uuid(ulid) == text
        assert lib.parse_ulid(lib.increment_ulid(ulid)) == number + 1
        for wrapped in ["{" + text + "}", "urn:uuid:" + text, text.replace("-", "")]:
            assert lib.parse_uuid(wrapped, lenient=True) == number
            records.append(lib.explain_uuid(wrapped))
        for version in range(1, 9):
            records.append(lib.is_uuid(text, version))
    for text in ["", "bad", "Z" * 26, "0" * 25 + "I", "\u017f" * 26]:
        records.extend([lib.explain_uuid(text), lib.explain_ulid(text)])
        records.append(lib.explain_ulid(text, lenient=True))
    for text in ["C232AB00-9414-11EC-B3C8-9F6BDECED846", "017F22E2-79B0-7CC3-98C4-DC0C0C07398F"]:
        records.extend([lib.uuid_timestamp_ns(text), lib.uuid_timestamp(text).isoformat()])
    records.extend(
        [
            lib.ulid_timestamp_ms(lib.ulid_from_parts(1)),
            lib.ulid_timestamp(lib.ulid_from_parts(1)).isoformat(),
        ]
    )
    try:
        lib.parse_uuid("private-token")
    except lib.IdCheckError as error:
        diagnostic = str(error)
    return {"version": lib.__version__, "records": records, "diagnostic": diagnostic}


if __name__ == "__main__":
    print(json.dumps(snapshot()))
