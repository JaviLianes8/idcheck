"""Handwritten contracts for string iteration and concatenation overrides."""

from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest

import idcheck as api

UUID = "00000000-0001-7000-8000-000000000001"
ULID = "0" * 9 + "1" + "0" * 15 + "1"


class FalseULIDIteration(str):
    def __iter__(self) -> Iterator[str]:
        return iter("0" * 26)


class FalseULIDAddition(str):
    def __add__(self, other: str) -> str:
        return "0" * 26


class FalseUUIDAddition(str):
    def __add__(self, other: str) -> str:
        return "00000000-0000-0000-0000-000000000000"


@pytest.mark.parametrize("subclass", [FalseULIDIteration, FalseULIDAddition])
@pytest.mark.parametrize("lenient", [False, True])
@pytest.mark.parametrize("text", [ULID, "!" * 26], ids=["valid", "invalid"])
@pytest.mark.parametrize(
    "reader",
    [
        api.is_ulid,
        api.explain_ulid,
        api.parse_ulid,
        api.inspect_ulid,
        api.ulid_timestamp_ms,
        api.ulid_timestamp,
        api.ulid_to_uuid,
        api.increment_ulid,
    ],
)
def test_ulid_readers_ignore_overridden_text_operations(
    reader: Callable[..., object], text: str, lenient: bool, subclass: type[str]
) -> None:
    value = subclass(text)
    if text == ULID:
        assert reader(value, lenient=lenient) == reader(text, lenient=lenient)
    elif reader is api.is_ulid:
        assert reader(value, lenient=lenient) is False
    elif reader is api.explain_ulid:
        assert reader(value, lenient=lenient) is api.Reason.BAD_CHARACTER
    else:
        with pytest.raises(api.InvalidULIDError) as caught:
            reader(value, lenient=lenient)
        assert caught.value.reason is api.Reason.BAD_CHARACTER
        assert caught.value.value is value
        assert str(caught.value) == api.Reason.BAD_CHARACTER.description


@pytest.mark.parametrize("lenient", [False, True])
@pytest.mark.parametrize("text", [UUID, "!" * 36], ids=["valid", "invalid"])
@pytest.mark.parametrize(
    "reader",
    [
        api.is_uuid,
        api.explain_uuid,
        api.parse_uuid,
        api.inspect_uuid,
        api.uuid_timestamp_ns,
        api.uuid_timestamp,
        api.uuid_to_ulid,
    ],
)
def test_uuid_readers_ignore_overridden_concatenation(
    reader: Callable[..., object], text: str, lenient: bool
) -> None:
    value = FalseUUIDAddition(text)
    if text == UUID:
        assert reader(value, lenient=lenient) == reader(text, lenient=lenient)
    elif reader is api.is_uuid:
        assert reader(value, lenient=lenient) is False
    elif reader is api.explain_uuid:
        assert reader(value, lenient=lenient) is api.Reason.BAD_CHARACTER
    else:
        with pytest.raises(api.InvalidUUIDError) as caught:
            reader(value, lenient=lenient)
        assert caught.value.reason is api.Reason.BAD_CHARACTER
        assert caught.value.value is value
        assert str(caught.value) == api.Reason.BAD_CHARACTER.description


@pytest.mark.parametrize(
    "parser,value",
    [
        (api.parse_ulid, FalseULIDIteration("0" * 25 + "1")),
        (api.parse_ulid, FalseULIDAddition("0" * 25 + "1")),
        (api.parse_uuid, FalseUUIDAddition("00000000-0000-0000-0000-000000000001")),
    ],
    ids=["ulid-iteration", "ulid-concatenation", "uuid-concatenation"],
)
def test_text_operations_cannot_replace_underlying_one_with_zero(
    parser: Callable[[str], int], value: str
) -> None:
    assert parser(value) == 1
