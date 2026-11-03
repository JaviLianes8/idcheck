"""Literal contracts for stable enum tokens and exception messages."""

from __future__ import annotations

import pickle
from enum import Enum

import pytest

import idcheck as api


@pytest.mark.parametrize(
    "enum_type,expected",
    [
        (api.UUIDForm, {"CANONICAL": "canonical", "BRACED": "braced", "URN": "urn", "HEX": "hex"}),
        (
            api.Variant,
            {"NCS": "ncs", "RFC9562": "rfc9562", "MICROSOFT": "microsoft", "FUTURE": "future"},
        ),
        (
            api.Reason,
            {
                "NOT_A_STRING": "not_a_string",
                "BAD_LENGTH": "bad_length",
                "BAD_CHARACTER": "bad_character",
                "BAD_LAYOUT": "bad_layout",
                "FORM_NOT_ALLOWED": "form_not_allowed",
                "WRONG_VARIANT": "wrong_variant",
                "WRONG_VERSION": "wrong_version",
                "OUT_OF_RANGE": "out_of_range",
                "NO_TIMESTAMP": "no_timestamp",
                "TIMESTAMP_OUT_OF_RANGE": "timestamp_out_of_range",
                "OVERFLOW": "overflow",
            },
        ),
    ],
)
def test_complete_enum_serialization(enum_type: type[Enum], expected: dict[str, str]) -> None:
    assert {name: member.value for name, member in enum_type.__members__.items()} == expected
    assert {name: str(member) for name, member in enum_type.__members__.items()} == expected


@pytest.mark.parametrize(
    "error_type",
    [
        api.IdCheckError,
        api.InvalidUUIDError,
        api.InvalidULIDError,
        api.TimestampRangeError,
        api.ULIDOverflowError,
    ],
)
@pytest.mark.parametrize(
    "message,expected",
    [(None, "wrong length"), ("", "wrong length"), ("custom message", "custom message")],
)
def test_error_message_defaults_and_pickle(
    error_type: type[api.IdCheckError], message: str | None, expected: str
) -> None:
    error = error_type(api.Reason.BAD_LENGTH, "private input", message)
    for result in (error, pickle.loads(pickle.dumps(error))):
        assert type(result) is error_type
        assert str(result) == expected
        assert result.reason is api.Reason.BAD_LENGTH
        assert result.value == "private input"


def test_bad_layout_api_token() -> None:
    value = "0000000-00000-0000-0000-000000000000"
    reason = api.explain_uuid(value)
    assert reason is not None
    assert reason.value == "bad_layout"
