"""Seeded malformed-input properties and private, bounded diagnostics."""

from __future__ import annotations

import io
import random
import string

import pytest

from idcheck import IdCheckError, Reason, explain_ulid, explain_uuid, parse_ulid, parse_uuid
from idcheck._cli import main


@pytest.mark.parametrize("seed", [9562, 128, 20261102])
def test_seeded_hostile_text_has_only_documented_outcomes(seed: int) -> None:
    rng = random.Random(seed)
    alphabet = string.printable + "\x00\ud800\u017f\uff11\ufeff"
    for _ in range(5000):
        value = "".join(rng.choices(alphabet, k=rng.choice([0, 1, 26, 32, 36, 38, 45, 100])))
        for explain, parse in [(explain_uuid, parse_uuid), (explain_ulid, parse_ulid)]:
            for lenient in (False, True):
                reason = explain(value, lenient=lenient)
                if reason is None:
                    assert 0 <= parse(value, lenient=lenient) < 2**128
                else:
                    with pytest.raises(IdCheckError) as caught:
                        parse(value, lenient=lenient)
                    assert caught.value.reason is reason
                    assert str(caught.value) == reason.description


class Unprintable:
    def __repr__(self) -> str:
        raise AssertionError("input must never be formatted")


@pytest.mark.parametrize("parse", [parse_uuid, parse_ulid])
def test_bad_objects_do_not_run_repr(parse: object) -> None:
    assert callable(parse)
    value = Unprintable()
    with pytest.raises(IdCheckError) as caught:
        parse(value)
    assert caught.value.value is value
    assert caught.value.reason is Reason.NOT_A_STRING
    assert str(caught.value) == "expected a str"


@pytest.mark.parametrize("length", [10_000, 100_000, 1_000_000])
def test_huge_inputs_have_constant_size_diagnostics(length: int) -> None:
    for text in ["private-token-" * length, "{" + "x" * length + "}", "urn:uuid:" + "x" * length]:
        for parse in [parse_uuid, parse_ulid]:
            with pytest.raises(IdCheckError) as caught:
                parse(text)
            assert str(caught.value) == "wrong length"


@pytest.mark.parametrize("command", ["validate", "inspect", "convert", "time"])
def test_cli_rejections_do_not_echo_secret_or_control_characters(command: str) -> None:
    out, err = io.StringIO(), io.StringIO()
    code = main([command, "private-token\n\x1b" * 10000], stdout=out, stderr=err)
    assert code == 1
    combined = out.getvalue() + err.getvalue()
    assert "private-token" not in combined and "\x1b" not in combined
    assert combined.count("\n") == 1 and len(combined) < 100


def test_cli_usage_errors_do_not_echo_input(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["validate", "--kind", "private-token" * 10000])
    assert caught.value.code == 1
    output = capsys.readouterr().err
    assert "private-token" not in output and len(output) < 1000
