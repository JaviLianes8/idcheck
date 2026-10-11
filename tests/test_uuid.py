import pytest

from idcheck import is_uuid

V1 = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
V3 = "6fa459ea-ee8a-3ca4-894e-db77e160355e"
V4 = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
V5 = "886313e1-3b8a-5372-9b90-0c9aee199e5d"
NIL = "00000000-0000-0000-0000-000000000000"


def test_accepts_canonical_lowercase() -> None:
    assert is_uuid(V4)


def test_accepts_uppercase() -> None:
    assert is_uuid(V4.upper())


def test_rejects_braces() -> None:
    assert not is_uuid("{" + V4 + "}")


def test_rejects_urn_prefix() -> None:
    assert not is_uuid("urn:uuid:" + V4)


def test_rejects_bare_hex() -> None:
    assert not is_uuid(V4.replace("-", ""))


def test_rejects_wrong_length() -> None:
    assert not is_uuid(V4 + "0")
    assert not is_uuid(V4[:-1])


def test_rejects_non_hex_character() -> None:
    assert not is_uuid("g47ac10b-58cc-4372-a567-0e02b2c3d479")


def test_rejects_non_string() -> None:
    assert not is_uuid(12345)  # type: ignore[arg-type]


def test_version_match() -> None:
    assert is_uuid(V4, version=4)
    assert is_uuid(V1, version=1)
    assert is_uuid(V3, version=3)
    assert is_uuid(V5, version=5)


def test_version_mismatch() -> None:
    assert not is_uuid(V4, version=1)
    assert not is_uuid(V1, version=4)


def test_version_requires_rfc_variant() -> None:
    wrong_variant = V4[:19] + "0" + V4[20:]
    assert is_uuid(wrong_variant)
    assert not is_uuid(wrong_variant, version=4)


def test_nil_fails_version_check() -> None:
    assert is_uuid(NIL)
    assert not is_uuid(NIL, version=4)


def test_invalid_version_argument_raises() -> None:
    with pytest.raises(ValueError):
        is_uuid(V4, version=0)
    with pytest.raises(ValueError):
        is_uuid(V4, version=9)
