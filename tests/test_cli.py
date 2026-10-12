import io
import json

import pytest
from _vectors import NIL, ULID_EXAMPLE, ULID_MAX, V1, V4, V7

from idcheck._cli import main


def _run(*argv: str, stdin: str = "") -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    status = main(list(argv), stdin=io.StringIO(stdin), stdout=out, stderr=err)
    return status, out.getvalue(), err.getvalue()


def test_validate_reports_each_identifier_and_passes() -> None:
    status, out, err = _run("validate", V4, ULID_EXAMPLE)
    assert status == 0
    assert out.splitlines() == [f"valid\tuuid\t{V4}", f"valid\tulid\t{ULID_EXAMPLE}"]
    assert err == ""


def test_validate_reads_stdin_and_fails_on_any_invalid() -> None:
    status, out, _ = _run("validate", stdin=f"{V4}\n\n  {{{V4}}}  \n")
    assert status == 1
    assert out.splitlines()[1] == f"invalid\tform_not_allowed\t{{{V4}}}"


def test_stdin_byte_order_mark_is_ignored() -> None:
    status, out, _ = _run("validate", stdin=chr(0xFEFF) + V4 + "\n")
    assert (status, out) == (0, f"valid\tuuid\t{V4}\n")


def test_validate_lenient_and_version() -> None:
    assert _run("validate", "--lenient", "{" + V4 + "}")[0] == 0
    status, out, _ = _run("validate", "--uuid-version", "1", V4, NIL)
    assert status == 1
    assert out.splitlines() == [f"invalid\twrong_version\t{V4}", f"invalid\twrong_variant\t{NIL}"]


def test_version_forces_uuid_kind() -> None:
    status, out, _ = _run("validate", "--uuid-version", "4", ULID_EXAMPLE)
    assert status == 1
    assert "bad_length" in out
    status, _, err = _run("validate", "--kind", "ulid", "--uuid-version", "4", ULID_EXAMPLE)
    assert status == 1
    assert "cannot be used" in err


def test_inspect_prints_json_lines() -> None:
    status, out, _ = _run("inspect", V7, ULID_EXAMPLE)
    assert status == 0
    uuid_record, ulid_record = (json.loads(line) for line in out.splitlines())
    assert uuid_record["version"] == 7
    assert uuid_record["timestamp"] == "2022-02-22T19:22:22+00:00"
    assert ulid_record["timestamp_ms"] == 1469922850259
    assert ulid_record["uuid"] == "01563e3a-b5d3-d676-4c61-efb99302bd5b"


def test_inspect_ulid_beyond_datetime_has_null_timestamp() -> None:
    record = json.loads(_run("inspect", ULID_MAX)[1])
    assert record["timestamp"] is None
    assert record["timestamp_ms"] == 2**48 - 1


def test_convert_both_ways() -> None:
    status, out, _ = _run("convert", V7, ULID_EXAMPLE)
    assert status == 0
    assert out.splitlines() == [
        "01FWHE4YDGFK1SHH6W1G60EECF",
        "01563e3a-b5d3-d676-4c61-efb99302bd5b",
    ]


def test_time_prints_iso_or_nanoseconds_and_errors_go_to_stderr() -> None:
    status, out, err = _run("time", V1, V4)
    assert status == 1
    assert out.strip() == "2022-02-22T19:22:22+00:00"
    assert "no_timestamp" in err
    assert _run("time", "--unix-ns", V7)[1].strip() == "1645557742000000000"


def test_time_past_datetime_max_is_an_error() -> None:
    status, out, err = _run("time", ULID_MAX)
    assert (status, out) == (1, "")
    assert "timestamp_out_of_range" in err


def test_kind_override_reports_the_forced_format() -> None:
    status, out, _ = _run("validate", "--kind", "ulid", V4)
    assert status == 1
    assert out.startswith("invalid\tbad_length")


def test_usage_errors_exit_one(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["validate", "--uuid-version", "9", V4])
    assert caught.value.code == 1
    assert "invalid choice" in capsys.readouterr().err


def test_help_has_runnable_examples(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["--help"])
    assert caught.value.code == 0
    assert "idcheck validate --uuid-version 4 < ids.txt" in capsys.readouterr().out
