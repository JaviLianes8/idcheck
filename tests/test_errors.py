import pickle

import pytest
from _vectors import V4

from idcheck import (
    InvalidULIDError,
    InvalidUUIDError,
    Reason,
    TimestampRangeError,
    ULIDOverflowError,
    UUIDForm,
    Variant,
    encode_ulid,
    explain_uuid,
    is_uuid,
    parse_uuid,
    ulid_from_parts,
)


@pytest.mark.parametrize(
    "error_type", [InvalidUUIDError, InvalidULIDError, TimestampRangeError, ULIDOverflowError]
)
def test_errors_survive_pickling(error_type: type[InvalidUUIDError]) -> None:
    error = error_type(Reason.BAD_LENGTH, "abc")
    copy = pickle.loads(pickle.dumps(error))
    assert type(copy) is error_type
    assert (copy.reason, copy.value, str(copy)) == (error.reason, error.value, str(error))


def test_huge_ints_still_raise_the_typed_error() -> None:
    huge = 10**5000
    with pytest.raises(InvalidULIDError) as caught:
        encode_ulid(huge)
    assert caught.value.value == huge
    with pytest.raises(InvalidULIDError):
        ulid_from_parts(huge)


def test_messages_stay_short_for_huge_input() -> None:
    with pytest.raises(InvalidUUIDError) as caught:
        parse_uuid("x" * 1_000_000)
    assert len(str(caught.value)) < 100


def test_enums_print_their_stable_value() -> None:
    assert str(Reason.BAD_LENGTH) == f"{Reason.BAD_LENGTH}" == "bad_length"
    assert str(Variant.RFC9562) == "rfc9562"
    assert str(UUIDForm.URN) == "urn"


def test_a_uuid_cut_by_four_characters_is_a_length_problem() -> None:
    assert explain_uuid(V4[:32], lenient=True) is Reason.BAD_LENGTH


@pytest.mark.parametrize("version", [True, 1.0, "1"])
def test_non_integer_version_is_a_type_error(version: object) -> None:
    with pytest.raises(TypeError):
        is_uuid(V4, version=version)  # type: ignore[arg-type]
