"""Inspect the release archives when IDCHECK_DIST points to built distributions."""

from __future__ import annotations

import email
import os
import tarfile
import zipfile
from pathlib import Path

import pytest


def test_release_archive_contents_and_metadata() -> None:
    location = os.environ.get("IDCHECK_DIST")
    if not location:
        pytest.skip("set IDCHECK_DIST to the built wheel and sdist directory")
    path = Path(location)
    with zipfile.ZipFile(path / "idcheck-1.0.0-py3-none-any.whl") as archive:
        names = archive.namelist()
        assert "idcheck/py.typed" in names
        assert "idcheck-1.0.0.dist-info/licenses/LICENSE" in names
        assert all(name.startswith(("idcheck/", "idcheck-1.0.0.dist-info/")) for name in names)
        metadata = email.message_from_bytes(archive.read("idcheck-1.0.0.dist-info/METADATA"))
        assert metadata["Version"] == "1.0.0"
        assert metadata["Requires-Python"] == ">=3.10"
        assert metadata["License-Expression"] == "MIT"
        classifiers = metadata.get_all("Classifier", [])
        assert "Development Status :: 5 - Production/Stable" in classifiers
        for minor in range(10, 15):
            assert f"Programming Language :: Python :: 3.{minor}" in classifiers
        assert all("extra == 'dev'" in item for item in metadata.get_all("Requires-Dist", []))
        for label in ["Homepage", "Source", "Issues", "Changelog"]:
            assert any(
                item.startswith(label + ", ") for item in metadata.get_all("Project-URL", [])
            )
    with tarfile.open(path / "idcheck-1.0.0.tar.gz") as archive:
        names += archive.getnames()
        assert "idcheck-1.0.0/tests/upstream/MANIFEST.json" in names
        assert "idcheck-1.0.0/LICENSE" in names
    assert not any(
        junk in name
        for name in names
        for junk in [
            "__pycache__",
            ".pyc",
            ".venv",
            "CERT-",
            "IMPROVEMENTS",
            "rfc9562.txt",
            "ulid.md",
        ]
    )
