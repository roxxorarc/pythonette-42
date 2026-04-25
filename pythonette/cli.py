import argparse
import sys
from pathlib import Path

from pythonette import __version__


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
    p.add_argument("-m", "--module", help="restrict to one module id (e.g. 00)")
    p.add_argument("-e", "--exercise", help="restrict to one exercise (e.g. ex00)")
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
        help="pull latest pythonette and reinstall",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.update:
        from pythonette.updater import update

        return update()

    from pythonette.runner import run

    return run(args)


if __name__ == "__main__":
    sys.exit(main())
