# idcheck guide

Everything public is importable from `idcheck`. Every function is pure: no clock, no
random source, no I/O.

## Strict and lenient

| Input | strict (default) | `lenient=True` |
| --- | --- | --- |
| `f47ac10b-58cc-4372-a567-0e02b2c3d479` (any case) | accepted | accepted |
| `{f47ac10b-58cc-4372-a567-0e02b2c3d479}` | `form_not_allowed` | accepted |
| `urn:uuid:f47ac10b-58cc-4372-a567-0e02b2c3d479` (prefix any case) | `form_not_allowed` | accepted |
| `f47ac10b58cc4372a5670e02b2c3d479` | `form_not_allowed` | accepted |
| hyphens elsewhere, braces around bare hex, surrounding spaces | rejected | rejected |

RFC 9562 Section 4 defines the canonical text and states that hex letters may be any
case. It mentions the braced form (as output by some implementations) and the URN form
for information only, which is why they are opt in. `uuid.UUID()` from the standard
library is looser still: it drops every hyphen wherever it appears.

For ULIDs, strict mode accepts the 32 symbols of the Crockford alphabet in any case.
Lenient mode also reads `I` and `L` as `1` and `O` as `0`, Crockford's decoding aliases.
`U` is rejected in both modes.

## Reason codes

`explain_uuid` and `explain_ulid` return the first problem as a `Reason`, or `None`.
Every error carries the same value in `error.reason`. `reason.value` is a stable string;
`reason.description` is a short sentence.

| Reason | Meaning |
| --- | --- |
| `not_a_string` | the value is not a `str` |
| `bad_length` | wrong number of characters (after removing an accepted wrapper) |
| `bad_character` | a character outside hex (UUID) or Crockford base32 (ULID) |
| `bad_layout` | UUID hyphens not at positions 8, 13, 18 and 23 |
| `form_not_allowed` | a braced, URN or bare hex UUID without `lenient=True` |
| `wrong_variant` | `version=` was given but the variant bits are not `10` |
| `wrong_version` | the version nibble differs from `version=` |
| `out_of_range` | a ULID above `7ZZZZZZZZZZZZZZZZZZZZZZZZZ`, or an integer part out of range |
| `no_timestamp` | the UUID is valid but its version carries no time (only v1, v6, v7 do) |
| `timestamp_out_of_range` | the instant is real but past `datetime.max` |
| `overflow` | `increment_ulid` on a ULID whose randomness is all ones |

## Errors

All errors derive from `IdCheckError`, which is a `ValueError`:

- `InvalidUUIDError`: bad UUID input, or `no_timestamp`.
- `InvalidULIDError`: bad ULID text, or an out of range integer for `encode_ulid` and
  `ulid_from_parts`.
- `TimestampRangeError`: the decoded instant cannot be a `datetime` (year above 9999).
- `ULIDOverflowError`: the monotonic increment would overflow 80 bits.

Two errors are not `IdCheckError`: `is_uuid` and friends raise a plain `ValueError` for a
`version=` argument outside 1 to 8 (a programming error), and `encode_ulid` and
`ulid_from_parts` raise `TypeError` for a non-integer (booleans included).

## UUID functions

- `is_uuid(value, version=None, *, lenient=False) -> bool`
- `explain_uuid(value, version=None, *, lenient=False) -> Reason | None`
- `parse_uuid(value, version=None, *, lenient=False) -> int`
- `inspect_uuid(value, *, lenient=False) -> UUIDInfo`
- `uuid_timestamp_ns(value, *, lenient=False) -> int`
- `uuid_timestamp(value, *, lenient=False) -> datetime`

`UUIDInfo` is a frozen dataclass: `value`, `canonical` (lowercase hyphenated), `form`
(`UUIDForm`), `variant` (`Variant`), `version`, `timestamp_ns`, plus the `is_nil` and
`is_max` properties. `version` is the version nibble when the variant is the RFC 9562
one and `None` otherwise, exactly like `uuid.UUID.version`. It can therefore be a
reserved value such as 0 or 15; `is_uuid(..., version=n)` only accepts 1 to 8.

`Variant` follows RFC 9562 Section 4.1, Table 1: `NCS` (`0xxx`, includes nil),
`RFC9562` (`10xx`), `MICROSOFT` (`110x`), `FUTURE` (`111x`, includes max).

## Timestamps and precision

- v1 and v6 (Sections 5.1 and 5.6) store a 60-bit count of 100 ns ticks since
  1582-10-15 00:00:00 UTC. `uuid_timestamp_ns` converts it exactly to Unix nanoseconds,
  which is negative before 1970.
- v7 (Section 5.7) stores 48 bits of Unix milliseconds.
- ULID stores 48 bits of Unix milliseconds: `ulid_timestamp_ms`.
- `uuid_timestamp` and `ulid_timestamp` return aware UTC datetimes. Python datetimes have
  microsecond resolution, so v1 and v6 ticks are floored. The 48-bit millisecond range
  reaches year 10889, past `datetime.max`, and those values raise
  `TimestampRangeError`; the integer functions always work.

## ULID functions

- `is_ulid`, `explain_ulid`, `parse_ulid`, `inspect_ulid`, `ulid_timestamp_ms`,
  `ulid_timestamp`, all taking `value, *, lenient=False`.
- `ULIDInfo` is a frozen dataclass: `value`, `canonical` (uppercase), `timestamp_ms`,
  `randomness`.
- `encode_ulid(value: int) -> str` writes any integer from 0 to 2**128 - 1.
- `ulid_from_parts(timestamp_ms, randomness=0) -> str` composes the two fields.
- `increment_ulid(value) -> str` applies the spec's monotonicity rule: add one to the
  randomness, keep the timestamp, fail with `ULIDOverflowError` rather than wrap.

## Conversion

UUIDs and ULIDs are both 128-bit values, so `uuid_to_ulid` and `ulid_to_uuid` copy the
bits unchanged and round trip losslessly. A UUIDv7 converted to a ULID keeps its
timestamp, because both put Unix milliseconds in the top 48 bits. The reverse is not
true in general: a ULID converted to a UUID usually has random bits where the version
and variant live, so it is a valid UUID string but not a valid RFC 9562 version.

## Command line

```
idcheck validate [--kind auto|uuid|ulid] [--lenient] [--uuid-version N] [ID ...]
idcheck inspect  [--kind ...] [--lenient] [ID ...]
idcheck convert  [--kind ...] [--lenient] [ID ...]
idcheck time     [--kind ...] [--lenient] [--unix-ns] [ID ...]
```

- With no `ID`, identifiers are read from stdin, one per line; blank lines are skipped
  and surrounding whitespace is stripped.
- `--kind auto` (the default) treats a 26 character value as a ULID and anything else
  as a UUID. `--uuid-version` implies `--kind uuid`.
- `validate` prints `valid<TAB>kind<TAB>id` or `invalid<TAB>reason<TAB>id` on stdout.
- `inspect` prints one JSON object per identifier. `timestamp` is ISO 8601, or `null`
  when absent or past `datetime.max`; ULID randomness is a 20 digit hex string so no
  JSON reader loses precision.
- `convert` prints the other format; `time` prints ISO 8601 UTC, or integer Unix
  nanoseconds with `--unix-ns`.
- Exit status 0 when every identifier passes, 1 otherwise, including usage errors.
  Errors go to stderr as `idcheck: <id>: <reason>: <description>`.
