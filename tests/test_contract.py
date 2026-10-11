import importlib.resources

import idcheck

PUBLIC_API: list[str] = ["is_uuid", "is_ulid", "parse_ulid", "ulid_timestamp"]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(idcheck.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in idcheck.__all__:
        assert hasattr(idcheck, name)


def test_version_is_a_three_part_string() -> None:
    parts = idcheck.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("idcheck").joinpath("py.typed").is_file()
