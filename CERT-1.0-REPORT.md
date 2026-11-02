# idcheck 1.0.0 preparation report

Progress:
- [x] Release branch from main `49e4136`; PyPI 0.2.0 confirmed live.
- [x] Stable API, typed errors, runnable public docstrings and strict typing.
- [x] Fetched specifications, contract tests and seeded hostile-input properties.
- [x] Wheel, sdist, archive inspection, README validation and PyPI upgrade e2e.
- [x] Documentation, metadata and dated changelog.
- [x] Every distinct installed supported interpreter: 12 builds, including free-threaded.
- [x] Mutation round: 22 of 22 killed; final gates pass.
- [ ] Independent reviewer (item 16): pending.
- [ ] Five QA lenses (item 19): pending.
- [ ] Merge and publication (item 17): pending.

## Scorecard

| Item | Preparation verdict | Evidence |
| --- | --- | --- |
| 1 | PASS | Same 27 public names, signatures, defaults and parsing results as 0.2.0; diagnostic changes in CHANGELOG. |
| 2 | PASS | Exact `__all__` contract, every export resolves, public imports in all documentation examples. |
| 3 | PASS | Every public name has an executable example; public-only doctest namespace and module doctests pass. |
| 4 | PASS | `mypy --strict src tests`, no public `Any`, `py.typed` inspected in the wheel. |
| 5 | PASS | Typed data errors, documented option errors, fixed default diagnostics, unprintable objects tested. |
| 6 | PASS | 184 tests including complete API contracts, CLI, errors, timestamp edges, dataclass immutability and pickling. |
| 7 | PASS | Live-fetched specifications with hashes; stdlib UUID and python-ulid 4.1.0 executed as independent references. |
| 8 | PASS | Wheel built from sdist; fresh venv installs PyPI 0.2.0, exercises an external consumer, upgrades and repeats; both CLI entry points exercised. |
| 9 | PASS | Three hostile-text seeds, 60,000 format/mode cases; large inputs to 13 MB, unprintable objects and scaling probes. |
| 10 | PASS | All 12 distinct available supported builds, 3.10 through 3.14, tested against the installed final wheel. |
| 11 | PASS | Exact certification badge, absolute README links, factual comparison, examples executed; `twine check --strict` passes. |
| 12 | PASS | Dated 1.0.0 section: 2026-11-02, stable contract and every changed diagnostic. |
| 13 | PASS | Version 1.0.0, Production/Stable, Python 3.10 to 3.14, MIT, project URLs, keywords, no runtime dependencies. |
| 14 | PASS | Both archive inventories inspected and contract-tested; LICENSE and typing marker present, no downloaded corpus or scratch data. |
| 15 | PASS | Format, lint, strict source typing and pytest each run independently with exit 0; strict test typing also passes. |
| 16 | PENDING | Independent review remains to be performed. |
| 17 | PENDING | Release branch pushed; merge and publication remain to be performed. |
| 18 | PASS | 22 deliberate mutations killed; the initial rounding survivor gained a contract and was killed on rerun. |
| 19 | PENDING | No independent QA lens verdicts recorded. |

## API and upgrade

All 27 public names keep their signatures and parsing defaults from 0.2.0. Default
exception messages and rejected CLI output no longer echo input. The `.value` attribute
still holds the original input; nonempty custom messages remain caller-controlled.
Option errors remain plain `TypeError` or `ValueError` as documented. Inspection records
remain frozen dataclasses; direct construction does not validate field consistency.

The upgrade consumer compares 100 seeded 128-bit values, both inspection records,
all accepted UUID forms, requested versions, conversions, ULID parts and increment,
invalid inputs and timestamps. It checks old and new exception diagnostics and drives
every CLI command plus usage errors before and after upgrade. Successful results and
exit statuses stay the same. The final source suite passes 184 tests without skips.

The publishing helper now checks the specific version, refuses a dirty tree and keeps
previous artifacts. Its PowerShell syntax was parsed successfully; publishing was not run.

## Ground truth

Sources were fetched on 2026-11-02 UTC. `tests/upstream/MANIFEST.json` records URLs,
revision, size, license and SHA-256. The downloaded documents remain outside the
repository. `scripts/fetch_upstream.py` was run again and all three digests matched.
Source-dependent tests skip cleanly when the files are absent and reject changed bytes.

- RFC 9562: https://www.rfc-editor.org/rfc/rfc9562.txt
  Figures 1 and 3, Appendix A and B UUID vectors, timestamp fields, nil and max are
  checked against the fetched text in `test_sources` and against API results.
- ULID specification, revision d0c7170df4517939e70129b4d6462cc162f2d5bf:
  https://github.com/ulid/spec/tree/d0c7170df4517939e70129b4d6462cc162f2d5bf
  Its examples and monotonic sequences are located in the downloaded source; its
  alphabet is extracted and tested digit by digit. Derived timestamps are labeled.
- Crockford alphabet and aliases: https://www.crockford.com/base32.html
  The downloaded table confirms the aliases used by lenient decoding.
- python-ulid 4.1.0: https://pypi.org/project/python-ulid/4.1.0/
  Installed and executed against the built wheel: 20,000 values, seed 9562, zero
  differences in encoding, decoding, UUID conversion, canonical text and timestamp
  fields. Its output also confirms the derived timestamp of the ULID example.
- Python's `uuid` module: 3,004 random/boundary values in all accepted forms, every
  version nibble and 3,000 timestamps per time-bearing layout. The v6/v7 time oracle
  runs on Python 3.14; older versions skip those two tests. The README comparison
  was checked by running brace, misplaced-hyphen and version-bit-setting examples.

## Robustness and performance

Three seeds (9562, 128, 20261102), 5,000 strings each, two formats and two modes give
60,000 hostile cases. Predicates, reasons and parsers agree; errors keep their typed
reason and a fixed message. Controls, lone surrogates, non-ASCII folding, oversized
integers, unprintable objects and large text are covered. Invalid CLI records do not
echo input or inject additional output lines.

Scaling probes used plain, braced and URN text at 100,000, 1,000,000 and 10,000,000
characters, five samples of 100 calls per shape/size. Median totals at 10 million
characters were 0.00027 s, 0.36441 s and 0.31266 s respectively; none hung. Ordinary
oversized text is rejected by length; wrappers require one linear slice, then a length
check. Accepted inputs have at most 45 characters and bounded parsing loops.

## Interpreter matrix

The wheel was installed outside the checkout, with tests and docs extracted from the
sdist and no source directory. Each run included package doctests, the external
consumer and `python -m idcheck`; normal venvs also exercised the installed launcher.
Embedded runtimes were copied before configuring paths, leaving their originals intact.
One embedded 3.10 setup needed pytest's `exceptiongroup` and `tomli` dependencies
installed explicitly; the corrected final run passed. The seven wheel-build/upgrade
tests run separately in the full source suite. All supported minor versions were run;
13 stale launcher entries point to absent installations and are not usable runtimes.

| Python build | Installed-wheel suite |
| --- | --- |
| 3.14.6 | 177 passed in 8.96s |
| 3.13.2 | 175 passed, 2 skipped in 8.70s |
| 3.12.10 | 175 passed, 2 skipped in 6.54s |
| 3.11.9 | 175 passed, 2 skipped in 6.21s |
| 3.10.11 | 175 passed, 2 skipped in 2.56s |
| 3.14.10 free-threaded | 177 passed in 1.79s |
| 3.13.18 | 175 passed, 2 skipped in 1.45s |
| 3.12.16 | 175 passed, 2 skipped in 1.72s |
| 3.11.18 | 175 passed, 2 skipped in 1.69s |
| 3.10.22 | 175 passed, 2 skipped in 2.14s |
| 3.14.10 | 177 passed in 2.01s |
| 3.11.11 | 175 passed, 2 skipped in 3.38s |

## Mutation round

Each mutation was applied alone to a disposable source copy at `e2ca2e6`, with bytecode
disabled and the full contract suite except wheel-build tests run with `-x`, a 300 s
per-test timeout and an overall timeout. The original source was restored after each
run. M18 initially survived: a new test pins flooring at 1,043 offsets on both sides
of the Unix epoch for v1 and v6. On the final round all 22 failed assertions. Later
changes only clarify error docstrings and strengthen installed-upgrade checks.

| ID | Mutation | Test that killed it |
| --- | --- | --- |
| M01 | UUID final hyphen shifted | `tests/test_cli.py::test_validate_reports_each_identifier_and_passes` |
| M02 | UUID leniency inverted | `tests/test_cli.py::test_validate_reads_stdin_and_fails_on_any_invalid` |
| M03 | RFC variant boundary moved | `tests/test_cli.py::test_validate_lenient_and_version` |
| M04 | UUID version shift wrong | `tests/test_cli.py::test_inspect_prints_json_lines` |
| M05 | Requested version ignored | `tests/test_cli.py::test_validate_lenient_and_version` |
| M06 | Requested variant ignored | `tests/test_cli.py::test_validate_lenient_and_version` |
| M07 | Nil value wrong | `tests/test_contract.py::test_nil_and_max_are_valid_but_versionless` |
| M08 | Non-ASCII case folding accepted | `tests/test_ulid_more.py::test_explain_names_the_problem` |
| M09 | ULID radix wrong | `tests/test_cli.py::test_inspect_prints_json_lines` |
| M10 | ULID 130-bit overflow accepted | `tests/test_contract.py::test_ulid_spec_example_and_maximum` |
| M11 | Crockford I alias wrong | `tests/test_sources.py::test_crockford_aliases_are_in_the_fetched_table` |
| M12 | Boolean encoding accepted | `tests/test_ulid_more.py::test_encode_covers_the_full_range_and_rejects_the_rest` |
| M13 | Maximum integer rejected | `tests/test_ulid_more.py::test_encode_covers_the_full_range_and_rejects_the_rest` |
| M14 | ULID parts swapped | `tests/test_docs.py::test_public_docstrings_execute_with_only_public_imports` |
| M15 | Monotonic overflow wraps | `tests/test_contract.py::test_ulid_spec_monotonic_sequence_and_overflow` |
| M16 | Monotonic increment skips value | `tests/test_contract.py::test_ulid_spec_monotonic_sequence_and_overflow` |
| M17 | Gregorian tick precision wrong | `tests/test_cli.py::test_time_prints_iso_or_nanoseconds_and_errors_go_to_stderr` |
| M18 | Datetime rounding replaces floor | `tests/test_precision.py::test_fractional_ticks_floor_on_both_sides_of_the_unix_epoch` |
| M19 | UUIDv7 timestamp shift wrong | `tests/test_cli.py::test_inspect_prints_json_lines` |
| M20 | Rejected input exposed in error | `tests/test_docs.py::test_public_docstrings_execute_with_only_public_imports` |
| M21 | Rejected CLI input exposed | `tests/test_cli.py::test_validate_reads_stdin_and_fails_on_any_invalid` |
| M22 | Randomness returns timestamp | `tests/test_ulid_more.py::test_inspect_splits_timestamp_and_randomness` |

## Packaging and final gates

`ruff format --check .`, `ruff check .`, `mypy --strict src`, `mypy --strict src tests`
and `pytest` each exit 0. Pytest uses a 300 s per-test limit and an explicit scratch
base directory. The final source suite: 184 passed. `twine check --strict` passes
for both artifacts. All Python source and test files remain below 200 lines.

Wheel: only package modules, `py.typed`, entry-point/metadata records and LICENSE.
Sdist: source, purposeful contract tests and provenance manifest, documentation,
fetch script, pyproject, README, CHANGELOG and LICENSE. Downloaded documents, caches,
local environments, improvement notes and this report are excluded.

Final artifact SHA-256:
- `idcheck-1.0.0-py3-none-any.whl`: `f8408c869d06b4604ac8d06caea646b6299fea39ed14aa5f83c4a605161ef8dd`
- `idcheck-1.0.0.tar.gz`: `7dd6c9ffb120bec1ef6f73a613e1bb5d2492a0dfeaa0f909cfbc0f5b2b8425eb`
