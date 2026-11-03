"""Handwritten contracts for builtin values with overridden subclass operations."""

from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest

import idcheck as api


class FalseLength(str):
    def __len__(self) -> int:
        return 26


class FalseIteration(str):
    def __iter__(self) -> Iterator[str]:
        return iter("00000000-0000-0000-0000-000000000000")


class FalseString(str):
    def __str__(self) -> str:
        return "0" * 26

    def upper(self) -> str:
        return "0" * 26


@pytest.mark.parametrize("text", ["", "1" * 4000], ids=["empty", "oversized"])
@pytest.mark.parametrize("lenient", [False, True])
def test_ulid_subclass_length_uses_actual_text(text: str, lenient: bool) -> None:
    value = FalseLength(text)
    assert not api.is_ulid(value, lenient=lenient)
    assert api.explain_ulid(value, lenient=lenient) is api.Reason.BAD_LENGTH
    for reader in (
        api.parse_ulid,
        api.inspect_ulid,
        api.ulid_timestamp_ms,
        api.ulid_timestamp,
        api.increment_ulid,
        api.ulid_to_uuid,
    ):
        with pytest.raises(api.InvalidULIDError) as caught:
            reader(value, lenient=lenient)
        assert caught.value.reason is api.Reason.BAD_LENGTH
        assert caught.value.value is value


@pytest.mark.parametrize(
    "reader",
    [api.parse_uuid, api.inspect_uuid, api.uuid_timestamp_ns, api.uuid_timestamp, api.uuid_to_ulid],
)
def test_uuid_subclass_errors_stay_typed_and_redacted(reader: Callable[[str], object]) -> None:
    value = FalseIteration("PRIVATE_TOKEN_" + "x" * 22)
    with pytest.raises(api.InvalidUUIDError) as caught:
        reader(value)
    assert caught.value.reason is api.Reason.BAD_CHARACTER
    assert caught.value.value is value
    assert str(caught.value) == "invalid character"
    assert "PRIVATE_TOKEN" not in repr(caught.value)


def test_uuid_subclass_predicates_use_actual_text() -> None:
    value = FalseIteration("PRIVATE_TOKEN_" + "x" * 22)
    assert not api.is_uuid(value)
    assert api.explain_uuid(value) is api.Reason.BAD_CHARACTER


def test_string_subclass_conversion_and_case_overrides_are_ignored() -> None:
    assert api.parse_ulid(FalseString("0" * 25 + "1")) == 1
    assert api.parse_uuid(FalseString("00000000-0000-0000-0000-000000000001")) == 1


class FalseArithmetic(int):
    def __and__(self, other: int) -> int:
        return 32

    def __lshift__(self, other: int) -> int:
        return 0

    def __ror__(self, other: int) -> int:
        return 0

    def __int__(self) -> int:
        return 0


class FalseRange(int):
    def __le__(self, other: int) -> bool:
        return True

    def __ge__(self, other: int) -> bool:
        return True


class UnhashableVersion(int):
    def __eq__(self, other: object) -> bool:
        return False

    def __ne__(self, other: object) -> bool:
        return True

    def __int__(self) -> int:
        return 1


def test_integer_subclass_arithmetic_uses_actual_value() -> None:
    assert api.encode_ulid(FalseArithmetic(1)) == "0" * 25 + "1"
    assert api.ulid_from_parts(FalseArithmetic(1), 0) == "0" * 9 + "1" + "0" * 16
    assert api.ulid_from_parts(0, FalseArithmetic(1)) == "0" * 25 + "1"


@pytest.mark.parametrize(
    ("encoder", "number"),
    [
        (api.encode_ulid, -1),
        (api.encode_ulid, 2**130),
        (api.ulid_from_parts, -1),
        (api.ulid_from_parts, 2**48),
        (lambda value: api.ulid_from_parts(0, value), -1),
        (lambda value: api.ulid_from_parts(0, value), 2**80),
    ],
)
def test_integer_subclass_cannot_bypass_range(encoder: Callable[[int], str], number: int) -> None:
    value = FalseRange(number)
    with pytest.raises(api.InvalidULIDError) as caught:
        encoder(value)
    assert caught.value.reason is api.Reason.OUT_OF_RANGE
    assert caught.value.value is value


def test_unhashable_version_subclass_uses_actual_value() -> None:
    value = "00000000-0000-4000-8000-000000000000"
    version = UnhashableVersion(4)
    assert api.is_uuid(value, version)
    assert api.explain_uuid(value, version) is None
    assert api.parse_uuid(value, version) == int(value.replace("-", ""), 16)
    assert not api.is_uuid(value, UnhashableVersion(3))
    for invalid in (0, 9):
        with pytest.raises(ValueError, match="version must be one of 1 through 8"):
            api.is_uuid(value, UnhashableVersion(invalid))
