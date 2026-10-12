"""Seeded cross-check against the standard library ``uuid`` module, the oracle."""

import random
import uuid

import pytest
from _vectors import V1, V3, V4, V5

from idcheck import (
    Variant,
    inspect_uuid,
    is_uuid,
    parse_uuid,
    ulid_to_uuid,
    uuid_timestamp_ns,
    uuid_to_ulid,
)

SEED = 9562
ROUNDS = 3000
_VARIANTS = {
    uuid.RESERVED_NCS: Variant.NCS,
    uuid.RFC_4122: Variant.RFC9562,
    uuid.RESERVED_MICROSOFT: Variant.MICROSOFT,
    uuid.RESERVED_FUTURE: Variant.FUTURE,
}


def _random_values() -> list[int]:
    rng = random.Random(SEED)
    edges = [0, (1 << 128) - 1, 1 << 127, (1 << 64) - 1]
    return edges + [rng.getrandbits(128) for _ in range(ROUNDS)]


def _stamped(rng: random.Random, version: int) -> int:
    value = rng.getrandbits(128)
    value = (value & ~(0xF << 76)) | (version << 76)
    return (value & ~(0b11 << 62)) | (0b10 << 62)


def test_stdlib_names_appendix_a_v3_and_v5() -> None:
    assert str(uuid.uuid3(uuid.NAMESPACE_DNS, "www.example.com")) == V3
    assert str(uuid.uuid5(uuid.NAMESPACE_DNS, "www.example.com")) == V5


@pytest.mark.parametrize("text", [V1, V3, V4, V5])
def test_appendix_vectors_agree_with_stdlib(text: str) -> None:
    oracle = uuid.UUID(text)
    info = inspect_uuid(text)
    assert (info.value, info.version, info.canonical) == (oracle.int, oracle.version, str(oracle))


def test_random_values_agree_with_stdlib_in_every_form() -> None:
    for value in _random_values():
        oracle = uuid.UUID(int=value)
        text = str(oracle)
        info = inspect_uuid(text.upper())
        assert info.value == value
        assert info.canonical == text
        assert info.version == oracle.version
        assert info.variant is _VARIANTS[oracle.variant]
        for form in (oracle.hex, "{" + text + "}", oracle.urn):
            assert parse_uuid(form, lenient=True) == uuid.UUID(form).int
            assert not is_uuid(form)
        assert parse_uuid(oracle.urn.upper(), lenient=True) == value


def test_versions_agree_with_stdlib_for_every_nibble() -> None:
    rng = random.Random(SEED)
    for version in range(16):
        for _ in range(50):
            oracle = uuid.UUID(int=_stamped(rng, version))
            assert inspect_uuid(str(oracle)).version == oracle.version == version
            if 1 <= version <= 8:
                assert is_uuid(str(oracle), version=version)


def test_v1_timestamps_agree_with_stdlib_time_field() -> None:
    rng = random.Random(SEED)
    for _ in range(ROUNDS):
        oracle = uuid.UUID(int=_stamped(rng, 1))
        expected = (oracle.time - 0x01B21DD213814000) * 100
        assert uuid_timestamp_ns(str(oracle)) == expected


def test_v1_built_by_stdlib_round_trips_its_timestamp() -> None:
    rng = random.Random(SEED)
    for _ in range(200):
        ticks = rng.getrandbits(60)
        fields = (ticks & 0xFFFFFFFF, (ticks >> 32) & 0xFFFF, (ticks >> 48) | 0x1000)
        oracle = uuid.UUID(fields=(*fields, 0x80, 0, rng.getrandbits(48)))
        assert uuid_timestamp_ns(str(oracle)) == (ticks - 0x01B21DD213814000) * 100


def test_conversion_round_trips_random_values() -> None:
    for value in _random_values():
        text = str(uuid.UUID(int=value))
        assert ulid_to_uuid(uuid_to_ulid(text)) == text
