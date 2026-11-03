# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-02

### Stable

- The 27 public names, strict and lenient parsing, typed rejection reasons, frozen
  inspection records, timestamp precision, lossless conversions and monotonic increment.
- Python 3.10 through 3.14, shipped typing information, and a dependency-free runtime.

### Changed

- Default exception messages no longer include the rejected input. The `.value`
  attribute still retains it, and explicitly supplied custom messages remain verbatim.
  This also avoids calling arbitrary input objects' `repr` during error construction.
- Invalid `validate` records end with `<redacted>` instead of the input. Errors from
  `inspect`, `convert` and `time` omit input, and CLI usage errors print a generic
  diagnostic plus usage. Exit statuses and successful output are unchanged.

### Added

- Runnable examples for public classes, source provenance checks, hostile-input
  properties, installed-wheel upgrade tests and release packaging contracts.
- Contracts for lenient timestamp and conversion options, enum serialization,
  exception message defaults, padded CLI randomness and overridden builtin subclasses.
- Contracts preserve underlying UUID and ULID text despite overridden slicing, and
  integer values despite overridden addition in encoding, ULID parts and UUID versions.
- Contracts preserve underlying ULID text despite overridden iteration and UUID/ULID
  text despite overridden concatenation, across all readers and both parsing modes.
- Contracts preserve underlying UUID and ULID text despite overridden multiplication
  and prefix removal, and ULID text despite overridden replacement, across all readers
  and both parsing modes, including typed rejection of invalid underlying text.
- Contracts preserve underlying UUID and ULID text despite overridden suffix removal
  and reflected multiplication, across all readers and both parsing modes, including
  typed rejection of invalid underlying text and exact integer-one parsing witnesses.
- Local checks stop at the first failed gate. The publishing script checks the
  requested version instead of rejecting the existing project, refuses a dirty
  tree, and builds into a fresh directory without deleting earlier artifacts.

### Fixed

- UUID and ULID consumers reject objects that only report `__class__` as `str`:
  predicates return `False`, explanations return `NOT_A_STRING`, and other readers
  raise their typed identifier error with that reason instead of a plain `TypeError`.
- UUID and ULID readers validate the underlying text of string subclasses using
  builtin operations. Overridden length, iteration or case methods cannot bypass
  validation, trigger unbounded ULID decoding, or expose input in conversion errors.
- Integer subclasses use their underlying value for encoding, both ULID parts and
  UUID version checks. Overridden comparisons and arithmetic cannot bypass bounds or
  crash encoding; valid unhashable version integers are accepted. Booleans remain
  rejected, and typed errors retain the original input in `.value`.
- The guide documents `increment_ulid`'s lenient option; contribution instructions
  describe integration-test disk/network requirements and `IDCHECK_SCRATCH`.

## [0.2.0]

### Added

- `explain_uuid` and `explain_ulid` return a precise `Reason` for a rejection.
- Typed errors: `IdCheckError` (a `ValueError`), `InvalidUUIDError`,
  `InvalidULIDError`, `TimestampRangeError` and `ULIDOverflowError`, each with
  `.reason` and `.value`.
- Keyword-only `lenient=False` on `is_uuid`, `is_ulid` and `parse_ulid`. Lenient UUIDs
  accept braces, `urn:uuid:` and bare 32 hex; lenient ULIDs read the Crockford aliases.
- `parse_uuid` and `inspect_uuid` with the frozen `UUIDInfo`, `UUIDForm` and `Variant`.
- `inspect_ulid` with the frozen `ULIDInfo`, and `ulid_timestamp_ms`.
- `uuid_timestamp` and `uuid_timestamp_ns` for v1, v6 and v7 (RFC 9562).
- `uuid_to_ulid`, `ulid_to_uuid`, `encode_ulid`, `ulid_from_parts` and `increment_ulid`.
- The `idcheck` command (`validate`, `inspect`, `convert`, `time`) and `python -m idcheck`.
- `docs/GUIDE.md`.

### Changed

- `is_uuid` raises `ValueError` for an out of range `version=` on every input, not only
  on well formed ones, and `TypeError` for a non-integer `version=` (such as `True`,
  which 0.1.0 read as 1).
- `parse_ulid` and `ulid_timestamp` raise `InvalidULIDError`, a `ValueError` subclass.
  `ulid_timestamp` raises `TimestampRangeError` (also a `ValueError`) past year 9999 and
  converts milliseconds with exact integer arithmetic.

### Fixed

- Non-ASCII letters that upper-case onto the Crockford alphabet (such as U+017F) are no
  longer accepted as ULID characters.
- `ulid_timestamp` on a far future ULID raised a platform dependent `OSError`,
  `OverflowError` or `ValueError`; it now always raises `TimestampRangeError`.

## [0.1.0]

- First release.
- `is_uuid(value, version=None)`: strict canonical hyphenated UUID validation with an
  optional version and RFC 4122 variant check.
- `is_ulid(value)`: canonical 26 character Crockford base32 ULID validation.
- `parse_ulid(value)`: decode a ULID string to its 128 bit integer value.
- `ulid_timestamp(value)`: read the UTC timestamp from a ULID's first 48 bits.
- Validation and parsing only. Generating identifiers is out of scope.
