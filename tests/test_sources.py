"""Check the short cited vectors against specifications fetched in this release run."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

import pytest
from _vectors import (
    FIGURE_1,
    FIGURE_3,
    MAX,
    MONOTONIC,
    MONOTONIC_TAIL,
    NIL,
    ULID_EXAMPLE,
    ULID_MAX,
    ULID_MAX_MS,
    VERSIONS,
)

from idcheck import encode_ulid, parse_ulid


@pytest.fixture(scope="module")
def sources() -> dict[str, str]:
    location = os.environ.get("IDCHECK_UPSTREAM")
    if not location:
        pytest.skip("set IDCHECK_UPSTREAM to the fetched specification directory")
    manifest = Path(__file__).parent / "upstream/MANIFEST.json"
    result = {}
    for item in json.loads(manifest.read_text(encoding="utf-8")):
        path = Path(location) / item["name"]
        if not path.exists():
            pytest.skip(f"source absent: {item['name']}")
        raw = path.read_bytes()
        assert len(raw) == item["size"]
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]
        result[item["name"]] = raw.decode("utf-8")
    return result


def test_rfc_vectors_are_in_the_fetched_document(sources: dict[str, str]) -> None:
    text = sources["rfc9562.txt"].lower()
    for value in [FIGURE_1, NIL, MAX, *VERSIONS]:
        assert value.lower() in text
    assert str(FIGURE_3) in text
    assert "0x1ec9414c232ab00" in text
    assert "0x017f22e279b0" in text


def test_ulid_examples_are_in_the_fetched_document(sources: dict[str, str]) -> None:
    text = sources["ulid.md"]
    for value in [ULID_EXAMPLE, ULID_MAX, *MONOTONIC, *MONOTONIC_TAIL]:
        assert value in text
    assert str(ULID_MAX_MS) in text


def test_alphabet_is_extracted_from_the_specification(sources: dict[str, str]) -> None:
    match = re.search(r"```\s*([0-9A-Z]{32})\s*```", sources["ulid.md"])
    assert match is not None
    for digit, char in enumerate(match[1]):
        assert encode_ulid(digit) == "0" * 25 + char
        assert parse_ulid("0" * 25 + char) == digit


def test_crockford_aliases_are_in_the_fetched_table(sources: dict[str, str]) -> None:
    text = re.sub(r"<[^>]+>", " ", sources["base32.html"])
    text = " ".join(text.split())
    assert "0 O o" in text and "1 I i L l" in text
    for char in "Oo":
        assert parse_ulid("0" * 25 + char, lenient=True) == 0
    for char in "IiLl":
        assert parse_ulid("0" * 25 + char, lenient=True) == 1
