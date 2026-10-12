# Improvement round

Ranked by value to a user who validates identifiers at a boundary (API input, CSV import,
log scraping). Everything here is additive: the 0.1.0 functions keep their signatures,
defaults and results.

## 1. Precise rejection reasons (highest value)

`is_uuid` and `is_ulid` answer yes or no. At an API boundary the caller needs to tell the
client *why*. Add a `Reason` enum (`bad_length`, `bad_character`, `bad_layout`,
`form_not_allowed`, `wrong_variant`, `wrong_version`, `out_of_range`, ...) plus
`explain_uuid` / `explain_ulid` that return the first reason or `None`.

## 2. Honest typed errors

Every failure raises a subclass of `IdCheckError`, itself a `ValueError`, so the existing
`except ValueError` code keeps working. Each error carries `.reason` and `.value`:
`InvalidUUIDError`, `InvalidULIDError`, `TimestampRangeError` (the instant exists but
`datetime` cannot hold it, for example the ULID maximum in year 10889) and
`ULIDOverflowError` (monotonic increment past the 80-bit randomness).

## 3. Strict by default, lenient on request

RFC 9562 Section 4 defines one canonical text form; real data also carries braces,
`urn:uuid:` and bare 32 hex. Add keyword-only `lenient=False` to `is_uuid` and the new
UUID functions so those three forms are accepted on request (case insensitive, as the RFC
requires for input), while strict mode reports `form_not_allowed` instead of a vague
failure. For ULIDs, lenient mode applies the Crockford base32 decoding aliases
(`I`/`L` read as `1`, `O` as `0`).

## 4. Typed frozen inspection results

`inspect_uuid` returns a frozen `UUIDInfo` (integer value, canonical lowercase text, input
form, `Variant`, version, Unix nanosecond timestamp when the layout has one, `is_nil`,
`is_max`). `inspect_ulid` returns a frozen `ULIDInfo` (value, canonical uppercase text,
48-bit millisecond timestamp, 80-bit randomness). `parse_uuid` mirrors `parse_ulid` and
returns the 128-bit integer.

## 5. Timestamps from v1, v6 and v7

RFC 9562 Sections 5.1, 5.6 and 5.7 define where the time lives. Add `uuid_timestamp`
(UTC `datetime`) and `uuid_timestamp_ns` (exact integer nanoseconds since the Unix epoch;
v1/v6 carry 100 ns ticks since 1582-10-15). Add `ulid_timestamp_ms` for the raw ULID
milliseconds so the full 48-bit range is reachable even past `datetime.max`.

## 6. UUID and ULID conversion

Both are 128-bit values, so conversion is a lossless bit copy: `uuid_to_ulid` and
`ulid_to_uuid`. Because UUIDv7 and ULID both start with 48 bits of Unix milliseconds, a v7
converted to a ULID keeps its timestamp. Also `encode_ulid` (integer to text) and
`ulid_from_parts` (timestamp plus randomness to text).

## 7. Monotonic increment, the spec rule only

The ULID spec's monotonicity section says: within the same millisecond, increment the
random part by one in its least significant bit, and fail on overflow. `increment_ulid`
implements exactly that rule as a pure function. No clock and no random source, so the
library still never generates identifiers on its own.

## 8. A command line tool

`idcheck validate`, `inspect`, `convert` and `time`, each taking identifiers as arguments
or one per line on stdin. Machine friendly output (tab separated, JSON lines for
`inspect`), errors on stderr, exit 1 on any failure.

## 9. Proof

Contract tests over the whole promise using the RFC 9562 Appendix A and B vectors and the
ULID spec example, a seeded cross-check of thousands of random values against the
standard library `uuid` module, and an end-to-end test that builds the wheel, installs it
into a fresh virtual environment and drives the real `idcheck` script.

## 10. Documentation

README with section citations, and `docs/GUIDE.md` covering strict versus lenient, the
reason codes, timestamp precision and the conversion caveats.

## Considered and left out

- Random ULID or UUID generation: needs a clock and a random source, and dedicated
  packages already do it. The pure increment rule (item 7) is the coherent part.
- Accepting hyphens anywhere, as `uuid.UUID()` does: that is the footgun this library
  exists to avoid, even in lenient mode.
