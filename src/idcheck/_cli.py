"""The ``idcheck`` command line tool: validate, inspect, convert and read timestamps."""

from __future__ import annotations

import argparse
import errno
import os
import sys
from collections.abc import Callable, Iterator, Sequence
from typing import NoReturn, TextIO

from . import _cli_commands as commands
from ._errors import IdCheckError

_EPILOG = """\
Identifiers come from the arguments, or one per line on stdin when none are given.
A 26 character value is read as a ULID, anything else as a UUID (override with --kind).

examples:
  idcheck validate f47ac10b-58cc-4372-a567-0e02b2c3d479 01ARZ3NDEKTSV4RRFFQ69G5FAV
  idcheck validate --uuid-version 4 < ids.txt
  idcheck validate --lenient "{f47ac10b-58cc-4372-a567-0e02b2c3d479}"
  idcheck inspect 017F22E2-79B0-7CC3-98C4-DC0C0C07398F
  idcheck convert 01ARZ3NDEKTSV4RRFFQ69G5FAV
  idcheck time C232AB00-9414-11EC-B3C8-9F6BDECED846

exit status: 0 when every identifier passes, 1 otherwise (errors go to stderr).
"""


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(1, f"{self.prog}: error: {message}\n")


def _build_parser() -> argparse.ArgumentParser:
    from . import __version__

    parser = _Parser(
        prog="idcheck",
        description="Validate and inspect UUID (RFC 9562) and ULID strings.",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"idcheck {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    helps = {
        "validate": "print valid or invalid with the reason, one line per identifier",
        "inspect": "print one JSON object per identifier with every decoded field",
        "convert": "print the ULID of a UUID, or the UUID of a ULID (same 128 bits)",
        "time": "print the embedded timestamp of a v1, v6 or v7 UUID or of a ULID",
    }
    for name, text in helps.items():
        child = sub.add_parser(name, help=text, description=text)
        child.add_argument("ids", nargs="*", metavar="ID", help="identifiers (default: stdin)")
        child.add_argument(
            "--kind",
            choices=("auto", "uuid", "ulid"),
            default="auto",
            help="format to read; auto treats 26 characters as a ULID (default: auto)",
        )
        child.add_argument(
            "--lenient",
            action="store_true",
            help="accept braced, urn:uuid: and bare hex UUIDs, and Crockford aliases in ULIDs",
        )
    validate = sub.choices["validate"]
    validate.add_argument(
        "--uuid-version",
        type=int,
        choices=range(1, 9),
        metavar="N",
        help="also require RFC 9562 variant and version N (1-8); implies --kind uuid",
    )
    sub.choices["time"].add_argument(
        "--unix-ns", action="store_true", help="print integer Unix nanoseconds, not ISO 8601"
    )
    return parser


def _identifiers(given: list[str], stdin: TextIO) -> Iterator[str]:
    if given:
        yield from given
        return
    if stdin.isatty():
        print("idcheck: reading identifiers from stdin, one per line", file=sys.stderr)
    for line in stdin:
        text = line.strip().lstrip("\ufeff").strip()
        if text:
            yield text


def _run_each(ids: Iterator[str], work: Callable[[str], str], out: TextIO, err: TextIO) -> int:
    status = 0
    for text in ids:
        try:
            print(work(text), file=out)
        except IdCheckError as error:
            print(f"idcheck: {text}: {error.reason.value}: {error.reason.description}", file=err)
            status = 1
    return status


def _safe(stream: TextIO) -> None:
    # A console or pipe in a legacy code page must not crash on a non-ASCII identifier.
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(errors="backslashreplace")


def main(
    argv: Sequence[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the command line tool and return its exit status."""
    if stdout is None:
        _safe(sys.stdout)
    if stderr is None:
        _safe(sys.stderr)
    if stdin is None and hasattr(sys.stdin, "reconfigure"):
        # Identifiers are ASCII; utf-8-sig drops the BOM some editors write on Windows.
        sys.stdin.reconfigure(encoding="utf-8-sig", errors="replace")
    args = _build_parser().parse_args(argv)
    out, err = stdout or sys.stdout, stderr or sys.stderr
    try:
        return _dispatch(args, _identifiers(args.ids, stdin or sys.stdin), out, err)
    except OSError as error:
        # The reader went away (for example ``| head -1``). Windows reports EINVAL.
        if not isinstance(error, BrokenPipeError) and error.errno != errno.EINVAL:
            raise
        if stdout is None:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 1


def _dispatch(args: argparse.Namespace, ids: Iterator[str], out: TextIO, err: TextIO) -> int:
    kind = args.kind
    if args.command == "validate":
        version = args.uuid_version
        if version is not None:
            if kind == "ulid":
                print("idcheck: --uuid-version cannot be used with --kind ulid", file=err)
                return 1
            kind = "uuid"
        status = 0
        for text in ids:
            ok, line = commands.validate(text, kind, args.lenient, version)
            print(line, file=out)
            status = status if ok else 1
        return status
    if args.command == "inspect":
        return _run_each(ids, lambda t: commands.inspect(t, kind, args.lenient), out, err)
    if args.command == "convert":
        return _run_each(ids, lambda t: commands.convert(t, kind, args.lenient), out, err)
    return _run_each(
        ids, lambda t: commands.timestamp(t, kind, args.lenient, args.unix_ns), out, err
    )


if __name__ == "__main__":
    sys.exit(main())
