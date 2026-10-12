# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
  on well formed ones.
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
