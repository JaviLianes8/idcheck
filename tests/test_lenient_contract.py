"""Handwritten lenient-input contracts for timestamps and conversions."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

import idcheck as api

UUID = "00000000-0001-7000-8000-000000000000"
FORMS = [UUID, "{" + UUID + "}", "urn:uuid:" + UUID, UUID.replace("-", "")]


@pytest.mark.parametrize("text", FORMS)
def test_datetime_from_every_uuid_form(text: str) -> None:
    assert api.uuid_timestamp(text, lenient=True) == datetime(
        1970, 1, 1, microsecond=1000, tzinfo=timezone.utc
    )
    if text != UUID:
        with pytest.raises(api.InvalidUUIDError) as caught:
            api.uuid_timestamp(text)
        assert caught.value.reason is api.Reason.FORM_NOT_ALLOWED


@pytest.mark.parametrize("text", FORMS)
def test_uuid_conversion_from_every_form(text: str) -> None:
    assert api.uuid_to_ulid(text, lenient=True) == "0000000001E008000000000000"
    if text != UUID:
        with pytest.raises(api.InvalidUUIDError) as caught:
            api.uuid_to_ulid(text)
        assert caught.value.reason is api.Reason.FORM_NOT_ALLOWED


@pytest.mark.parametrize(
    "alias,digit", [("O", "0"), ("o", "0"), ("I", "1"), ("i", "1"), ("L", "1"), ("l", "1")]
)
def test_ulid_aliases_reach_every_timestamp_and_conversion(alias: str, digit: str) -> None:
    text = "0" * 9 + alias + "0" * 15 + alias
    timestamp = int(digit)
    expected_uuid = (
        "00000000-0000-0000-0000-000000000000"
        if digit == "0"
        else "00000000-0001-0000-0000-000000000001"
    )
    assert api.ulid_timestamp_ms(text, lenient=True) == timestamp
    assert api.ulid_timestamp(text, lenient=True) == datetime(
        1970, 1, 1, microsecond=timestamp * 1000, tzinfo=timezone.utc
    )
    assert api.increment_ulid(text, lenient=True) == (
        "0" * 9 + digit + "0" * 15 + str(timestamp + 1)
    )
    assert api.ulid_to_uuid(text, lenient=True) == expected_uuid
    for reader in (api.ulid_timestamp_ms, api.ulid_timestamp, api.increment_ulid, api.ulid_to_uuid):
        with pytest.raises(api.InvalidULIDError) as caught:
            reader(text)
        assert caught.value.reason is api.Reason.BAD_CHARACTER


def test_all_alias_zero_ulid() -> None:
    text = "O" * 26
    assert api.ulid_timestamp_ms(text, lenient=True) == 0
    assert api.ulid_timestamp(text, lenient=True) == datetime(1970, 1, 1, tzinfo=timezone.utc)
    assert api.increment_ulid(text, lenient=True) == "0" * 25 + "1"
    assert api.ulid_to_uuid(text, lenient=True) == "00000000-0000-0000-0000-000000000000"
