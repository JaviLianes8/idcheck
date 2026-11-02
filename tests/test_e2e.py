"""Build the wheel, install it into a fresh virtual environment, drive the real script."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import venv
from pathlib import Path

import pytest
from _vectors import ULID_EXAMPLE, V1, V4, V7

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def script(tmp_path_factory: pytest.TempPathFactory) -> Path:
    base = tmp_path_factory.mktemp("e2e")
    dist = base / "dist"
    subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(dist), str(ROOT)],
        check=True,
        capture_output=True,
        timeout=180,
    )
    (wheel,) = dist.glob("idcheck-*.whl")
    env_dir = base / "venv"
    venv.EnvBuilder(with_pip=True).create(env_dir)
    bin_dir = env_dir / ("Scripts" if os.name == "nt" else "bin")
    python = bin_dir / ("python.exe" if os.name == "nt" else "python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--quiet", "idcheck==0.2.0"],
        check=True,
        capture_output=True,
        timeout=120,
    )
    consumer = [str(python), "-I", str(ROOT / "tests/_consumer.py")]
    before = json.loads(subprocess.check_output(consumer, cwd=base, text=True, timeout=30))
    assert before["version"] == "0.2.0"
    assert all("private-token" in message for message in _diagnostics(python))
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-index", "--quiet", str(wheel)],
        check=True,
        capture_output=True,
        timeout=120,
    )
    after = json.loads(subprocess.check_output(consumer, cwd=base, text=True, timeout=30))
    assert after["version"] == "1.0.0"
    assert before["records"] == after["records"]
    assert "private-token" in before["diagnostic"]
    assert after["diagnostic"] == "wrong length"
    assert all(
        "private-token" not in message and len(message) < 1000 for message in _diagnostics(python)
    )
    return bin_dir / ("idcheck.exe" if os.name == "nt" else "idcheck")


def _diagnostics(python: Path) -> list[str]:
    results = []
    for arguments in [
        [command, "private-token"] for command in ["validate", "inspect", "convert", "time"]
    ] + [["validate", "--kind", "private-token"]]:
        done = subprocess.run(
            [str(python), "-I", "-m", "idcheck", *arguments],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=python.parent,
        )
        assert done.returncode == 1
        results.append(done.stdout + done.stderr)
    return results


def _run(script: Path, *args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(script), *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=script.parent,
        timeout=30,
    )


def test_installed_script_validates_stdin(script: Path) -> None:
    done = _run(script, "validate", stdin=f"{V4}\n{ULID_EXAMPLE}\n")
    assert done.returncode == 0
    assert done.stdout.splitlines() == [f"valid\tuuid\t{V4}", f"valid\tulid\t{ULID_EXAMPLE}"]


def test_installed_script_fails_with_exit_one(script: Path) -> None:
    done = _run(script, "validate", "{" + V4 + "}")
    assert done.returncode == 1
    assert "form_not_allowed" in done.stdout


def test_installed_script_inspects_converts_and_reads_time(script: Path) -> None:
    record = json.loads(_run(script, "inspect", V7).stdout)
    assert record["version"] == 7
    assert record["variant"] == "rfc9562"
    converted = _run(script, "convert", V7).stdout.strip()
    assert _run(script, "convert", converted).stdout.strip() == V7.lower()
    assert _run(script, "time", V1).stdout.strip() == "2022-02-22T19:22:22+00:00"


def test_installed_script_reports_errors_on_stderr(script: Path) -> None:
    done = _run(script, "time", V4)
    assert done.returncode == 1
    assert done.stdout == ""
    assert "no_timestamp" in done.stderr


def test_installed_module_entry_point(script: Path) -> None:
    python = script.parent / ("python.exe" if os.name == "nt" else "python")
    done = subprocess.run(
        [str(python), "-m", "idcheck", "convert", V7], capture_output=True, text=True
    )
    assert (done.returncode, done.stdout.strip()) == (0, "01FWHE4YDGFK1SHH6W1G60EECF")


def test_installed_script_survives_non_ascii_output(script: Path) -> None:
    done = subprocess.run(
        [str(script), "validate", chr(0x131) * 26], capture_output=True, cwd=script.parent
    )
    assert done.returncode == 1
    assert done.stdout.startswith(b"invalid\tbad_character\t")


def test_installed_script_help_and_version(script: Path) -> None:
    assert "examples:" in _run(script, "--help").stdout
    assert _run(script, "--version").stdout.strip() == "idcheck 1.0.0"


@pytest.mark.parametrize(
    "tail,expected",
    [("0", "00000000000000000000"), ("1", "00000000000000000001"), ("Z", "0000000000000000001f")],
)
def test_installed_randomness_hex_padding(script: Path, tail: str, expected: str) -> None:
    done = _run(script, "inspect", "0" * 25 + tail)
    assert done.returncode == 0
    assert json.loads(done.stdout)["randomness_hex"] == expected


@pytest.mark.parametrize("form", ["canonical", "braced", "urn", "hex"])
def test_installed_uuid_form_tokens(script: Path, form: str) -> None:
    text = {
        "canonical": V4,
        "braced": "{" + V4 + "}",
        "urn": "urn:uuid:" + V4,
        "hex": V4.replace("-", ""),
    }[form]
    done = _run(script, "inspect", "--lenient", text)
    assert done.returncode == 0
    assert json.loads(done.stdout)["form"] == form
    assert json.loads(done.stdout)["variant"] == "rfc9562"


def test_installed_bad_layout_token(script: Path) -> None:
    done = _run(script, "validate", "0000000-00000-0000-0000-000000000000")
    assert done.returncode == 1
    assert done.stdout == "invalid\tbad_layout\t<redacted>\n"
