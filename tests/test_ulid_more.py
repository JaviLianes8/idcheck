from datetime import datetime, timezone

import pytest
from _vectors import ULID_EXAMPLE, ULID_EXAMPLE_MS, ULID_MAX

from idcheck import (
    InvalidULIDError,
    Reason,
    encode_ulid,
    explain_ulid,
    increment_ulid,
    inspect_ulid,
    is_ulid,
    parse_ulid,
    ulid_from_parts,
    ulid_timestamp,
)


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        (42, Reason.NOT_A_STRING),
        ("", Reason.BAD_LENGTH),
        (ULID_EXAMPLE[:-1], Reason.BAD_LENGTH),
        (ULID_EXAMPLE[:-1] + "U", Reason.BAD_CHARACTER),
        (ULID_EXAMPLE[:-1] + "-", Reason.BAD_CHARACTER),
        (ULID_EXAMPLE[:-1] + chr(0x17F), Reason.BAD_CHARACTER),
        ("8" + ULID_MAX[1:], Reason.OUT_OF_RANGE),
        ("Z" * 26, Reason.OUT_OF_RANGE),
    ],
)
def test_explain_names_the_problem(text: object, reason: Reason) -> None:
    assert explain_ulid(text) is reason


def test_strict_rejects_crockford_aliases_lenient_reads_them() -> None:
    aliased = "0IL" + "O" * 23
    assert explain_ulid(aliased) is Reason.BAD_CHARACTER
    assert is_ulid(aliased.lower(), lenient=True)
    assert inspect_ulid(aliased, lenient=True).canonical == "011" + "0" * 23
    assert explain_ulid("0" * 25 + "U", lenient=True) is Reason.BAD_CHARACTER


def test_inspect_splits_timestamp_and_randomness() -> None:
    info = inspect_ulid(ULID_EXAMPLE.lower())
    assert info.canonical == ULID_EXAMPLE
    assert str(info) == ULID_EXAMPLE
    assert info.timestamp_ms == ULID_EXAMPLE_MS
    assert info.value == (info.timestamp_ms << 80) | info.randomness
    with pytest.raises(AttributeError):
        info.value = 0  # type: ignore[misc]


def test_parse_raises_typed_error() -> None:
    with pytest.raises(InvalidULIDError) as caught:
        parse_ulid("8" + ULID_MAX[1:])
    assert caught.value.reason is Reason.OUT_OF_RANGE


def test_timestamp_is_exact_to_the_millisecond() -> None:
    stamp = ulid_timestamp(ulid_from_parts(1, 0))
    assert stamp == datetime(1970, 1, 1, 0, 0, 0, 1000, tzinfo=timezone.utc)


def test_encode_covers_the_full_range_and_rejects_the_rest() -> None:
    assert encode_ulid(0) == "0" * 26
    assert encode_ulid((1 << 128) - 1) == ULID_MAX
    for bad in (-1, 1 << 128):
        with pytest.raises(InvalidULIDError):
            encode_ulid(bad)
    for wrong in (True, 1.0, "1"):
        with pytest.raises(TypeError):
            encode_ulid(wrong)  # type: ignore[arg-type]


def test_from_parts_checks_each_part() -> None:
    assert ulid_from_parts(ULID_EXAMPLE_MS, 0)[:10] == ULID_EXAMPLE[:10]
    with pytest.raises(InvalidULIDError, match="timestamp_ms"):
        ulid_from_parts(1 << 48)
    with pytest.raises(InvalidULIDError, match="randomness"):
        ulid_from_parts(0, 1 << 80)


def test_increment_keeps_the_timestamp_and_is_sortable() -> None:
    nxt = increment_ulid(ULID_EXAMPLE.lower())
    assert nxt > ULID_EXAMPLE
    assert nxt[:10] == ULID_EXAMPLE[:10]
    assert parse_ulid(nxt) == parse_ulid(ULID_EXAMPLE) + 1
