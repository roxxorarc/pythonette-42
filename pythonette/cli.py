import argparse
import sys
from pathlib import Path

from pythonette import __version__


def _normalize_module(value: str) -> str:
    """Accept '2', '02', etc. — module ids are stored zero-padded to 2."""
    s = value.strip()
    if s.isdigit():
        return s.zfill(2)
    return s


def _normalize_exercise(value: str) -> str:
    """Accept '4', 'ex4', 'ex04' — exercise ids in registry are 'ex<digit>'."""
    s = value.strip().lower()
    if s.startswith("ex"):
        s = s[2:]
    if s.isdigit():
        return f"ex{int(s)}"
    return value


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pythonette",
        description="Test automation framework for 42 Python modules.",
    )
    p.add_argument(
        "path",
        nargs="?",
        default=".",
        type=Path,
        help="project directory (default: cwd)",
    )
    p.add_argument(
        "-m", "--module",
        type=_normalize_module,
        help="restrict to one module id (e.g. 2, 02, or 00)",
    )
    p.add_argument(
        "-e", "--exercise",
        type=_normalize_exercise,
        help="restrict to one exercise (e.g. 4, ex4, or ex04)",
    )
    p.add_argument(
        "--diff",
        action="store_true",
        help="show colored diffs on failure",
    )
    p.add_argument(
        "--explain",
        action="store_true",
        help="print explanation for each failure",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument(
        "-V", "--version", action="version", version=f"pythonette {__version__}"
    )
    p.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="pull latest pythonette and reinstall in-place",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="with -u: rebuild venv from scratch via install.sh",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.update:
        from pythonette.updater import update

        return update(force=args.force)

    from pythonette.runner import run

    return run(args)


if __name__ == "__main__":
    sys.exit(main())
