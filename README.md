# idcheck

Strict validation and parsing of UUID and ULID identifier strings, zero dependencies and fully typed.

## Install

```
pip install idcheck
```

## Usage

```python
from idcheck import is_uuid, is_ulid, parse_ulid, ulid_timestamp

# Strict UUID check: canonical hyphenated form only, any case.
is_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479")  # True
is_uuid("{f47ac10b-58cc-4372-a567-0e02b2c3d479}")  # False (braces)
is_uuid("urn:uuid:f47ac10b-58cc-4372-a567-0e02b2c3d479")  # False (urn prefix)
is_uuid("f47ac10b58cc4372a5670e02b2c3d479")  # False (bare hex)

# Lenient mode accepts exactly those three forms, nothing looser.
is_uuid("{f47ac10b-58cc-4372-a567-0e02b2c3d479}", lenient=True)  # True

# Optional version check (also verifies the RFC 9562 variant bits).
is_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479", version=4)  # True
is_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479", version=1)  # False

# ULID validation and parsing (Crockford base32, 26 characters).
is_ulid("01ARZ3NDEKTSV4RRFFQ69G5FAV")  # True
parse_ulid("01ARZ3NDEKTSV4RRFFQ69G5FAV")  # 1777027686520646174104517696511196507
ulid_timestamp("01ARZ3NDEKTSV4RRFFQ69G5FAV")
# datetime.datetime(2016, 7, 30, 23, 54, 10, 259000, tzinfo=datetime.timezone.utc)
```

### Why was it rejected?

```python
from idcheck import Reason, explain_uuid, parse_uuid, InvalidUUIDError

explain_uuid("f47ac10b58cc4372a5670e02b2c3d479")  # Reason.FORM_NOT_ALLOWED
explain_uuid("00000000-0000-0000-0000-000000000000", 4)  # Reason.WRONG_VARIANT
explain_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479")  # None (valid)

try:
    parse_uuid("not-a-uuid")
except InvalidUUIDError as error:  # a ValueError subclass
    error.reason  # Reason.BAD_LENGTH
```

### Inspect, timestamps and conversion

```python
from idcheck import inspect_uuid, uuid_timestamp, uuid_to_ulid, ulid_to_uuid

info = inspect_uuid("017F22E2-79B0-7CC3-98C4-DC0C0C07398F")  # RFC 9562 A.6
info.version, info.variant, info.canonical
# (7, <Variant.RFC9562: 'rfc9562'>, '017f22e2-79b0-7cc3-98c4-dc0c0c07398f')
info.timestamp_ns  # 1645557742000000000

uuid_timestamp("C232AB00-9414-11EC-B3C8-9F6BDECED846")  # RFC 9562 A.1, v1
# datetime.datetime(2022, 2, 22, 19, 22, 22, tzinfo=datetime.timezone.utc)

uuid_to_ulid("017F22E2-79B0-7CC3-98C4-DC0C0C07398F")  # '01FWHE4YDGFK1SHH6W1G60EECF'
ulid_to_uuid("01FWHE4YDGFK1SHH6W1G60EECF")  # back, losslessly
```

### Command line

```
$ idcheck validate f47ac10b-58cc-4372-a567-0e02b2c3d479 "{f47ac10b-58cc-4372-a567-0e02b2c3d479}"
valid	uuid	f47ac10b-58cc-4372-a567-0e02b2c3d479
invalid	form_not_allowed	{f47ac10b-58cc-4372-a567-0e02b2c3d479}
$ idcheck validate --uuid-version 4 < ids.txt
$ idcheck inspect 01ARZ3NDEKTSV4RRFFQ69G5FAV      # one JSON object per line
$ idcheck convert 017F22E2-79B0-7CC3-98C4-DC0C0C07398F
01FWHE4YDGFK1SHH6W1G60EECF
$ idcheck time C232AB00-9414-11EC-B3C8-9F6BDECED846
2022-02-22T19:22:22+00:00
```

Identifiers come from the arguments or one per line on stdin. `validate` reports every
result on stdout; the other commands print errors to stderr. The exit status is 0 when
every identifier passes and 1 otherwise.

The full reference (every function, the reason codes, precision and caveats) is in
[docs/GUIDE.md](docs/GUIDE.md).

## Scope

This library validates, parses and converts. It never reads a clock or a random source,
so it does not generate identifiers: [python-ulid](https://pypi.org/project/python-ulid/)
and the standard library `uuid` module already cover generation. `ulid_from_parts` and
`increment_ulid` (the ULID monotonicity rule) only work from values you pass in.

## Standards

- UUID: [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562). Canonical text and the
  braced and URN forms: Section 4. Variant: Section 4.1. Version: Section 4.2. Time
  layouts: Sections 5.1 (v1), 5.6 (v6) and 5.7 (v7). Nil and max: Sections 5.9 and 5.10.
  The tests use the Appendix A test vectors and the Appendix B v8 examples.
- ULID: the [ULID specification](https://github.com/ulid/spec): 48-bit millisecond
  timestamp plus 80 bits of randomness, Crockford base32, case insensitive, maximum
  `7ZZZZZZZZZZZZZZZZZZZZZZZZZ`, and the monotonicity and overflow rules. The tests use
  its examples verbatim.
- Crockford base32 decoding aliases (`I`, `L` as `1`, `O` as `0`), used only in lenient
  mode: [crockford.com/base32](https://www.crockford.com/base32.html).

## Why

The standard library `uuid.UUID()` is a footgun for validation. It silently accepts
braces, the `urn:uuid:` prefix and bare 32 character hex, and it never checks the
version, so it cannot answer "is this exactly a canonical version 4 UUID string?".
`is_uuid` does, in one strict function.

For ULIDs the healthy packages (`python-ulid`, `ulid-py`) are built around generating
new values and pull in their own object model. There was no small, typed, zero
dependency helper that just answers "is this string a valid ULID?" and reads back its
integer value and timestamp. `idcheck` fills that gap and keeps both formats under one
roof.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
