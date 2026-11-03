"""Handwritten contracts for forged types, slicing and integer addition overrides."""

from __future__ import annotations

from collections.abc import Callable
from typing import SupportsIndex, cast

import pytest

import idcheck as api

UUID = "00000000-0001-7000-8000-000000000001"
ULID = "0" * 9 + "1" + "0" * 15 + "1"
UUID_READERS: list[Callable[..., object]] = [
    api.is_uuid,
    api.explain_uuid,
    api.parse_uuid,
    api.inspect_uuid,
    api.uuid_timestamp_ns,
    api.uuid_timestamp,
    api.uuid_to_ulid,
]
ULID_READERS: list[Callable[..., object]] = [
    api.is_ulid,
    api.explain_ulid,
    api.parse_ulid,
    api.inspect_ulid,
    api.ulid_timestamp_ms,
    api.ulid_timestamp,
    api.ulid_to_uuid,
    api.increment_ulid,
]


@pytest.mark.parametrize("lenient", [False, True])
@pytest.mark.parametrize("reader", UUID_READERS + ULID_READERS)
def test_forged_string_identity_is_rejected(reader: Callable[..., object], lenient: bool) -> None:
    value = type("PretendString", (), {"__class__": property(lambda self: str)})()
    assert isinstance(value, str)
    assert not issubclass(type(value), str)
    if reader in (api.is_uuid, api.is_ulid):
        assert reader(value, lenient=lenient) is False
    elif reader in (api.explain_uuid, api.explain_ulid):
        assert reader(value, lenient=lenient) is api.Reason.NOT_A_STRING
    else:
        error = api.InvalidUUIDError if reader in UUID_READERS else api.InvalidULIDError
        with pytest.raises(error) as caught:
            reader(value, lenient=lenient)
        assert caught.value.reason is api.Reason.NOT_A_STRING
        assert caught.value.value is value
        assert str(caught.value) == api.Reason.NOT_A_STRING.description


class FalseSlice(str):
    def __getitem__(self, key: SupportsIndex | slice) -> str:
        return "00000000-0000-0000-0000-000000000000" if "-" in self else "0" * 26


@pytest.mark.parametrize("lenient", [False, True])
@pytest.mark.parametrize("reader", UUID_READERS)
def test_uuid_readers_ignore_overridden_slicing(
    reader: Callable[..., object], lenient: bool
) -> None:
    assert reader(FalseSlice(UUID), lenient=lenient) == reader(UUID, lenient=lenient)


@pytest.mark.parametrize("lenient", [False, True])
@pytest.mark.parametrize("reader", ULID_READERS)
def test_ulid_readers_ignore_overridden_slicing(
    reader: Callable[..., object], lenient: bool
) -> None:
    assert reader(FalseSlice(ULID), lenient=lenient) == reader(ULID, lenient=lenient)


def test_slicing_cannot_replace_underlying_one_with_zero() -> None:
    assert api.parse_uuid(FalseSlice("00000000-0000-0000-0000-000000000001")) == 1
    assert api.parse_ulid(FalseSlice("0" * 25 + "1")) == 1


class FalseAddition(int):
    def __add__(self, other: int) -> int:
        return 0


@pytest.mark.parametrize(
    "encoder,expected",
    [
        (api.encode_ulid, "0" * 25 + "1"),
        (lambda value: api.ulid_from_parts(value, 0), "0" * 9 + "1" + "0" * 16),
        (lambda value: api.ulid_from_parts(0, value), "0" * 25 + "1"),
    ],
    ids=["encode", "timestamp", "randomness"],
)
def test_ulid_integer_inputs_ignore_overridden_addition(
    encoder: Callable[[int], str], expected: str
) -> None:
    assert encoder(FalseAddition(1)) == expected


@pytest.mark.parametrize("reader", [api.is_uuid, api.explain_uuid, api.parse_uuid])
def test_uuid_version_ignores_overridden_addition(reader: Callable[..., object]) -> None:
    text = "00000000-0000-4000-8000-000000000000"
    assert reader(text, FalseAddition(4)) == reader(text, 4)


@pytest.mark.parametrize("text", [UUID, ULID])
def test_genuine_string_subclass_need_not_report_string_identity(text: str) -> None:
    subclass = type("HiddenString", (str,), {"__class__": property(lambda self: object)})
    reader = api.parse_uuid if "-" in text else api.parse_ulid
    assert reader(cast(str, subclass(text))) == reader(text)
