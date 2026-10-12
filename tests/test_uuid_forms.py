from datetime import datetime, timezone

import pytest
from _vectors import V1, V4, V6, V7

from idcheck import (
    InvalidUUIDError,
    Reason,
    TimestampRangeError,
    UUIDForm,
    explain_uuid,
    inspect_uuid,
    is_uuid,
    parse_uuid,
    uuid_timestamp,
    uuid_timestamp_ns,
)

BRACED = "{" + V4 + "}"
URN = "urn:uuid:" + V4
BARE = V4.replace("-", "")


@pytest.mark.parametrize(
    ("text", "form"),
    [
        (V4, UUIDForm.CANONICAL),
        (BRACED, UUIDForm.BRACED),
        (URN, UUIDForm.URN),
        (BARE, UUIDForm.HEX),
    ],
)
def test_lenient_accepts_each_form_and_reports_it(text: str, form: UUIDForm) -> None:
    info = inspect_uuid(text, lenient=True)
    assert info.form is form
    assert info.canonical == V4
    assert str(info) == V4


@pytest.mark.parametrize("text", [BRACED, URN, BARE, "URN:UUID:" + V4.upper()])
def test_strict_rejects_wrappers_with_form_not_allowed(text: str) -> None:
    assert explain_uuid(text) is Reason.FORM_NOT_ALLOWED
    assert is_uuid(text, lenient=True)


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        (12345, Reason.NOT_A_STRING),
        (None, Reason.NOT_A_STRING),
        ("", Reason.BAD_LENGTH),
        (V4 + "0", Reason.BAD_LENGTH),
        ("{" + BARE + "}", Reason.BAD_LENGTH),
        ("urn:uuid:" + BARE, Reason.BAD_LENGTH),
        ("g" + V4[1:], Reason.BAD_CHARACTER),
        (" " + V4[1:], Reason.BAD_CHARACTER),
        (chr(0x661) + V4[1:], Reason.BAD_CHARACTER),
        ("z" + BARE[1:], Reason.BAD_CHARACTER),
        (V4[:8] + V4[9] + "-" + V4[10:], Reason.BAD_LAYOUT),
        ("-" * 36, Reason.BAD_LAYOUT),
    ],
)
def test_explain_names_the_first_problem(text: object, reason: Reason) -> None:
    assert explain_uuid(text, lenient=True) is reason


def test_wrong_variant_is_reported_before_version() -> None:
    microsoft = V4[:19] + "c" + V4[20:]
    assert is_uuid(microsoft)
    assert explain_uuid(microsoft, 4) is Reason.WRONG_VARIANT


def test_parse_raises_a_typed_error_with_reason_and_value() -> None:
    with pytest.raises(InvalidUUIDError) as caught:
        parse_uuid(BRACED)
    assert caught.value.reason is Reason.FORM_NOT_ALLOWED
    assert caught.value.value == BRACED
    assert "lenient" in str(caught.value)


def test_parse_with_version_checks_it() -> None:
    assert parse_uuid(V4, 4) == int(BARE, 16)
    with pytest.raises(InvalidUUIDError):
        parse_uuid(V4, 7)


def test_invalid_version_argument_raises_even_for_bad_input() -> None:
    with pytest.raises(ValueError, match="1 through 8"):
        explain_uuid("nope", 0)


def test_timestamp_of_a_versionless_layout_is_refused() -> None:
    assert inspect_uuid(V4).timestamp_ns is None
    with pytest.raises(InvalidUUIDError) as caught:
        uuid_timestamp(V4)
    assert caught.value.reason is Reason.NO_TIMESTAMP


def test_v1_and_v6_keep_100_ns_ticks_and_floor_the_datetime() -> None:
    one_tick_later = V1[:7] + "1" + V1[8:]
    six_later = V6[:17] + "1" + V6[18:]
    assert uuid_timestamp_ns(one_tick_later) == uuid_timestamp_ns(V1) + 100
    assert uuid_timestamp_ns(six_later) == uuid_timestamp_ns(V6) + 100
    assert uuid_timestamp(one_tick_later) == uuid_timestamp(V1)


def test_v1_before_the_unix_epoch_is_negative() -> None:
    gregorian_start = "00000000-0000-1000-8000-000000000000"
    assert uuid_timestamp(gregorian_start) == datetime(1582, 10, 15, tzinfo=timezone.utc)
    assert uuid_timestamp_ns(gregorian_start) < 0


def test_v7_past_datetime_max_raises_range_error() -> None:
    latest = "ffffffff-ffff-7fff-bfff-ffffffffffff"
    assert uuid_timestamp_ns(latest) == (2**48 - 1) * 1_000_000
    with pytest.raises(TimestampRangeError):
        uuid_timestamp(latest)


def test_lenient_timestamp_reads_wrapped_forms() -> None:
    assert uuid_timestamp_ns("{" + V7 + "}", lenient=True) == uuid_timestamp_ns(V7)
