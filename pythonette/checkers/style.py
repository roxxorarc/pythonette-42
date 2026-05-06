import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StyleResult:
    tool: str
    ok: bool
    output: str


def check_flake8(file: Path) -> StyleResult:
    proc = subprocess.run(
        [sys.executable, "-m", "flake8", str(file)],
        capture_output=True,
        text=True,
    )
    output = (proc.stdout + proc.stderr).strip()
    return StyleResult(tool="flake8", ok=proc.returncode == 0, output=output)


def check_mypy(file: Path) -> StyleResult:
    """Subject III.1: 'All functions and methods must include type hints.
    Check this using mypy.'"""
    proc = subprocess.run(
        [
            sys.executable, "-m", "mypy",
            "--no-color-output",
            "--no-error-summary",
            "--hide-error-context",
            "--show-error-codes",
            "--disallow-untyped-defs",
            "--disallow-incomplete-defs",
            "--check-untyped-defs",
            "--disallow-untyped-calls",
            "--disallow-any-generics",
            "--disallow-subclassing-any",
            "--warn-return-any",
            "--warn-unused-ignores",
            "--warn-redundant-casts",
            "--warn-unreachable",
            "--no-implicit-optional",
            "--strict-equality",
            "--ignore-missing-imports",
            str(file),
        ],
        capture_output=True,
        text=True,
        cwd=str(file.parent),
    )
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode not in (0, 1):
        # Tooling failure (e.g. mypy crashed). Surface as KO with a clear
        # message — better than silently passing.
        return StyleResult(
            tool="mypy", ok=False,
            output=output or f"mypy exit code {proc.returncode}",
        )
    return StyleResult(tool="mypy", ok=proc.returncode == 0, output=output)
