# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

- First release.
- `is_uuid(value, version=None)`: strict canonical hyphenated UUID validation with an
  optional version and RFC 4122 variant check.
- `is_ulid(value)`: canonical 26 character Crockford base32 ULID validation.
- `parse_ulid(value)`: decode a ULID string to its 128 bit integer value.
- `ulid_timestamp(value)`: read the UTC timestamp from a ULID's first 48 bits.
- Validation and parsing only. Generating identifiers is out of scope.
