# idcheck 1.0.0 preparation report

Progress:
- [x] Release branch from main `49e4136`; PyPI 0.2.0 confirmed live.
- [x] Stable API, typed errors, runnable public docstrings and strict typing.
- [x] Fetched specifications, contract tests and seeded hostile-input properties.
- [x] Wheel, sdist, archive inspection, README validation and PyPI upgrade e2e.
- [x] Documentation, metadata and dated changelog.
- [ ] Every installed supported interpreter.
- [ ] Mutation round and final gates.
- [ ] Independent reviewer (item 16): pending.
- [ ] Five QA lenses (item 19): pending.
- [ ] PR and final guard; merge and publication (item 17) remain pending.

## Preparation evidence

All 27 public names keep their signatures and parsing defaults from 0.2.0. Default
exception messages and rejected CLI output no longer echo input. Custom exception
messages remain caller-controlled. Every behavior change appears in CHANGELOG 1.0.0.

Baseline: 148 tests passed; `mypy --strict src tests` passed. Expanded suite: 184
passed, including real wheel installation over PyPI 0.2.0 in a fresh environment.
The external consumer compares seeded results before and after upgrade, verifies
error-message changes, and the CLI tests exercise both installed entry points.

Sources were fetched on 2026-11-02 UTC. `tests/upstream/MANIFEST.json` records the
URLs, pinned revision where available, sizes, licenses and SHA-256 digests.
Downloaded documents remain outside the repository; `scripts/fetch_upstream.py`
re-fetches and verifies them. Source tests skip without the local downloads.

- RFC 9562: https://www.rfc-editor.org/rfc/rfc9562.txt
- ULID specification at d0c7170df4517939e70129b4d6462cc162f2d5bf:
  https://github.com/ulid/spec/tree/d0c7170df4517939e70129b4d6462cc162f2d5bf
- Crockford alphabet and aliases: https://www.crockford.com/base32.html
- Reference implementation: python-ulid 4.1.0, installed from PyPI and executed
  against the built wheel on 20,000 seeded 128-bit values, zero differences in
  encoding, parsing, UUID conversion, canonical text and raw timestamp fields.
  https://pypi.org/project/python-ulid/4.1.0/
- The standard library UUID oracle covers 3,004 random/boundary values in each
  accepted form, every version nibble and 3,000 timestamps per time-bearing layout.

The hostile-text test uses three seeds, 5,000 strings each, both formats and both
leniency settings. Huge strings and unprintable objects have fixed-size diagnostics.
Formatting, lint, strict typing and the full suite currently pass. Final evidence
will be recorded after the interpreter and mutation runs finish.
