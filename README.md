# idcheck

Strict validation and parsing of UUID and ULID identifier strings, zero dependencies and fully typed.

## Install

```
pip install idcheck
```

## Usage

```python
from idcheck import is_uuid, is_ulid, parse_ulid, ulid_timestamp

# Strict UUID check: canonical hyphenated form only.
is_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479")          # True
is_uuid("{f47ac10b-58cc-4372-a567-0e02b2c3d479}")        # False (braces)
is_uuid("urn:uuid:f47ac10b-58cc-4372-a567-0e02b2c3d479")  # False (urn prefix)
is_uuid("f47ac10b58cc4372a5670e02b2c3d479")              # False (bare hex)

# Optional version check (also verifies the RFC 4122 variant).
is_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479", version=4)  # True
is_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479", version=1)  # False

# ULID validation and parsing (Crockford base32, 26 characters).
is_ulid("01ARZ3NDEKTSV4RRFFQ69G5FAV")   # True
parse_ulid("01ARZ3NDEKTSV4RRFFQ69G5FAV")  # 1777027686520646174104517696511196507
ulid_timestamp("01ARZ3NDEKTSV4RRFFQ69G5FAV")
# datetime.datetime(2016, 7, 30, 23, 54, 10, 259000, tzinfo=datetime.timezone.utc)
```

This library validates and parses only. It does not generate identifiers:
[python-ulid](https://pypi.org/project/python-ulid/) already covers generation.

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
