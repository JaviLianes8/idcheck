from datetime import datetime, timezone

import pytest

from idcheck import is_ulid, parse_ulid, ulid_timestamp

EXAMPLE = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
EXAMPLE_INT = 1777027686520646174104517696511196507
EXAMPLE_MS = 1469922850259


def _encode(value: int) -> str:
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    chars = []
    for _ in range(26):
        chars.append(alphabet[value & 31])
        value >>= 5
    return "".join(reversed(chars))


def test_accepts_canonical() -> None:
    assert is_ulid(EXAMPLE)


def test_accepts_lowercase() -> None:
    assert is_ulid(EXAMPLE.lower())


def test_rejects_wrong_length() -> None:
    assert not is_ulid(EXAMPLE[:-1])
    assert not is_ulid(EXAMPLE + "0")


def test_rejects_ambiguous_letters() -> None:
    assert not is_ulid("0" * 25 + "I")
    assert not is_ulid("0" * 25 + "L")
    assert not is_ulid("0" * 25 + "O")
    assert not is_ulid("0" * 25 + "U")


def test_rejects_first_character_overflow() -> None:
    assert not is_ulid("8" + "0" * 25)
    assert is_ulid("7" + "Z" * 25)


def test_rejects_non_string() -> None:
    assert not is_ulid(1)  # type: ignore[arg-type]


def test_parse_ulid_value() -> None:
    assert parse_ulid("0" * 26) == 0
    assert parse_ulid("7" + "Z" * 25) == (1 << 128) - 1
    assert parse_ulid(EXAMPLE) == EXAMPLE_INT
    assert parse_ulid(EXAMPLE) >> 80 == EXAMPLE_MS


def test_parse_ulid_round_trips_a_constructed_value() -> None:
    value = (EXAMPLE_MS << 80) | 0x1234
    assert parse_ulid(_encode(value)) == value


def test_parse_ulid_rejects_invalid() -> None:
    with pytest.raises(ValueError):
        parse_ulid("not-a-ulid")


def test_ulid_timestamp_is_correct_utc() -> None:
    expected = datetime(2016, 7, 30, 23, 54, 10, 259000, tzinfo=timezone.utc)
    result = ulid_timestamp(EXAMPLE)
    assert result == expected
    assert result.tzinfo is timezone.utc


def test_ulid_timestamp_matches_constructed_milliseconds() -> None:
    value = (1 << 80) | 0  # timestamp of 1 millisecond after the epoch
    stamp = ulid_timestamp(_encode(value))
    assert stamp == datetime(1970, 1, 1, 0, 0, 0, 1000, tzinfo=timezone.utc)


def test_ulid_timestamp_rejects_invalid() -> None:
    with pytest.raises(ValueError):
        ulid_timestamp("short")
