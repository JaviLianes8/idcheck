"""Build the wheel, install it into a fresh virtual environment, drive the real script."""

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
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist), str(ROOT)],
        check=True,
        capture_output=True,
    )
    (wheel,) = dist.glob("idcheck-*.whl")
    env_dir = base / "venv"
    venv.EnvBuilder(with_pip=True).create(env_dir)
    bin_dir = env_dir / ("Scripts" if os.name == "nt" else "bin")
    python = bin_dir / ("python.exe" if os.name == "nt" else "python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-index", "--quiet", str(wheel)],
        check=True,
        capture_output=True,
    )
    return bin_dir / ("idcheck.exe" if os.name == "nt" else "idcheck")


def _run(script: Path, *args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(script), *args], input=stdin, capture_output=True, text=True, cwd=script.parent
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


def test_installed_script_help_and_version(script: Path) -> None:
    assert "examples:" in _run(script, "--help").stdout
    assert _run(script, "--version").stdout.startswith("idcheck 0.")
