"""Exact timestamp boundaries and stable immutable inspection records."""

from __future__ import annotations

import pickle
import random
import uuid
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from idcheck import (
    ULIDInfo,
    UUIDInfo,
    encode_ulid,
    inspect_ulid,
    inspect_uuid,
    uuid_timestamp,
    uuid_timestamp_ns,
)


def test_fractional_ticks_floor_on_both_sides_of_the_unix_epoch() -> None:
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    rng = random.Random(100)
    offsets = list(range(-21, 22)) + [rng.randrange(-(10**12), 10**12) for _ in range(1000)]
    for ticks_from_epoch in offsets:
        ticks = 0x01B21DD213814000 + ticks_from_epoch
        low, middle, high = ticks & 0xFFFFFFFF, (ticks >> 32) & 0xFFFF, ticks >> 48
        v1 = str(uuid.UUID(fields=(low, middle, high | 0x1000, 0x80, 0, 0)))
        v6 = str(
            uuid.UUID(int=((ticks >> 12) << 80) | (6 << 76) | ((ticks & 4095) << 64) | (1 << 63))
        )
        expected = epoch + timedelta(microseconds=ticks_from_epoch // 10)
        for text in (v1, v6):
            assert uuid_timestamp_ns(text) == ticks_from_epoch * 100
            assert uuid_timestamp(text) == expected


def test_inspection_records_are_frozen_hashable_and_pickleable() -> None:
    records: list[UUIDInfo | ULIDInfo] = [
        inspect_uuid(str(uuid.UUID(int=1))),
        inspect_ulid(encode_ulid(1)),
    ]
    for info in records:
        restored = pickle.loads(pickle.dumps(info))
        assert restored == info and hash(restored) == hash(info)
        assert str(restored) == info.canonical
        with pytest.raises(FrozenInstanceError):
            info.canonical = "changed"  # type: ignore[misc]
