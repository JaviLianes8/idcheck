import importlib.resources
from datetime import datetime, timezone
from itertools import pairwise

import pytest
from _vectors import (
    FIGURE_1,
    FIGURE_3,
    GREGORIAN_TICKS,
    MAX,
    MONOTONIC,
    MONOTONIC_TAIL,
    NIL,
    ULID_EXAMPLE,
    ULID_EXAMPLE_MS,
    ULID_MAX,
    ULID_MAX_MS,
    UNIX_MS,
    UNIX_NS,
    V1,
    V6,
    V7,
    VERSIONS,
)

import idcheck
from idcheck import (
    IdCheckError,
    Reason,
    TimestampRangeError,
    ULIDOverflowError,
    Variant,
)

PUBLIC_API: list[str] = [
    "IdCheckError",
    "InvalidULIDError",
    "InvalidUUIDError",
    "Reason",
    "TimestampRangeError",
    "ULIDInfo",
    "ULIDOverflowError",
    "UUIDForm",
    "UUIDInfo",
    "Variant",
    "encode_ulid",
    "explain_ulid",
    "explain_uuid",
    "increment_ulid",
    "inspect_ulid",
    "inspect_uuid",
    "is_ulid",
    "is_uuid",
    "parse_ulid",
    "parse_uuid",
    "ulid_from_parts",
    "ulid_timestamp",
    "ulid_timestamp_ms",
    "ulid_to_uuid",
    "uuid_timestamp",
    "uuid_timestamp_ns",
    "uuid_to_ulid",
]
STAMP = datetime(2022, 2, 22, 19, 22, 22, tzinfo=timezone.utc)


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(idcheck.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in idcheck.__all__:
        assert hasattr(idcheck, name)


def test_version_is_a_three_part_string() -> None:
    parts = idcheck.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("idcheck").joinpath("py.typed").is_file()


def test_every_error_is_a_value_error_with_a_reason() -> None:
    for error in (idcheck.InvalidUUIDError, idcheck.InvalidULIDError):
        assert issubclass(error, IdCheckError)
    assert issubclass(TimestampRangeError, ValueError)
    assert issubclass(ULIDOverflowError, ValueError)
    assert all(reason.description for reason in Reason)


@pytest.mark.parametrize(("text", "version"), sorted(VERSIONS.items()))
def test_rfc_vectors_validate_with_their_version(text: str, version: int) -> None:
    assert idcheck.is_uuid(text, version=version)
    info = idcheck.inspect_uuid(text)
    assert (info.version, info.variant) == (version, Variant.RFC9562)
    assert info.canonical == text.lower()
    others = [other for other in range(1, 9) if other != version]
    assert all(idcheck.explain_uuid(text, o) is Reason.WRONG_VERSION for o in others)


def test_section_4_text_and_integer_are_the_same_uuid() -> None:
    assert idcheck.parse_uuid(FIGURE_1) == FIGURE_3
    assert idcheck.parse_uuid("urn:uuid:" + FIGURE_1, lenient=True) == FIGURE_3


def test_appendix_a_timestamps_agree_for_v1_v6_and_v7() -> None:
    assert UNIX_NS == (GREGORIAN_TICKS - 0x01B21DD213814000) * 100
    assert UNIX_NS == UNIX_MS * 1_000_000
    for text in (V1, V6, V7):
        assert idcheck.uuid_timestamp_ns(text) == UNIX_NS
        assert idcheck.uuid_timestamp(text) == STAMP


def test_nil_and_max_are_valid_but_versionless() -> None:
    nil, top = idcheck.inspect_uuid(NIL), idcheck.inspect_uuid(MAX)
    assert nil.is_nil and not nil.is_max and nil.variant is Variant.NCS
    assert top.is_max and not top.is_nil and top.variant is Variant.FUTURE
    assert nil.version is None and top.version is None
    assert idcheck.explain_uuid(NIL, 4) is Reason.WRONG_VARIANT


def test_ulid_spec_example_and_maximum() -> None:
    assert idcheck.ulid_timestamp_ms(ULID_EXAMPLE) == ULID_EXAMPLE_MS
    assert idcheck.parse_ulid(ULID_MAX) == (1 << 128) - 1
    assert idcheck.ulid_timestamp_ms(ULID_MAX) == ULID_MAX_MS == 2**48 - 1
    assert idcheck.explain_ulid("8" + ULID_MAX[1:]) is Reason.OUT_OF_RANGE
    with pytest.raises(TimestampRangeError):
        idcheck.ulid_timestamp(ULID_MAX)


def test_ulid_spec_monotonic_sequence_and_overflow() -> None:
    for before, after in pairwise(MONOTONIC):
        assert idcheck.increment_ulid(before) == after
    for before, after in pairwise(MONOTONIC_TAIL):
        assert idcheck.increment_ulid(before) == after
    with pytest.raises(ULIDOverflowError) as caught:
        idcheck.increment_ulid(MONOTONIC_TAIL[-1])
    assert caught.value.reason is Reason.OVERFLOW


def test_conversion_is_lossless_and_keeps_the_v7_timestamp() -> None:
    ulid = idcheck.uuid_to_ulid(V7)
    assert idcheck.ulid_timestamp_ms(ulid) == UNIX_MS
    assert idcheck.ulid_to_uuid(ulid) == V7.lower()
    assert idcheck.uuid_to_ulid(idcheck.ulid_to_uuid(ULID_EXAMPLE)) == ULID_EXAMPLE
