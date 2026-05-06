from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pythonette.subjects.registry import Exercise


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    reason: str = ""
    stderr: str = ""
    stdout: str = ""
    expected_stdout: str | None = None


class Check(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult: ...


@dataclass(frozen=True)
class _SandboxResult:
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool


def run_in_sandbox(
    exercise: "Exercise",
    exercise_dir: Path,
    code: str,
    *,
    stdin: str | None = None,
    timeout: float = 5.0,
) -> _SandboxResult:
    with tempfile.TemporaryDirectory(prefix="pythonette_") as tmp:
        sandbox = Path(tmp)
        for fname in exercise.filenames:
            src = exercise_dir / fname
            if src.is_file():
                shutil.copy(src, sandbox / fname)
        for extra in getattr(exercise, "support_paths", ()):
            src = exercise_dir / extra
            dst = sandbox / extra
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            elif src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src, dst)
        target = sandbox / "_pythonette_harness.py"
        target.write_text(code)
        try:
            proc = subprocess.run(
                [sys.executable, target.name],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(sandbox),
            )
        except subprocess.TimeoutExpired as exc:
            return _SandboxResult(
                stdout=exc.stdout if isinstance(exc.stdout, str) else "",
                stderr=exc.stderr if isinstance(exc.stderr, str) else "",
                returncode=-1,
                timed_out=True,
            )
        return _SandboxResult(
            stdout=proc.stdout,
            stderr=proc.stderr,
            returncode=proc.returncode,
            timed_out=False,
        )


def extract_error(stderr: str) -> str | None:
    lines = [ln for ln in stderr.splitlines() if ln.strip()]
    if not lines:
        return None
    last = lines[-1]
    for prefix in (
        "AssertionError:",
        "ImportError:",
        "ModuleNotFoundError:",
        "TypeError:",
        "AttributeError:",
        "NameError:",
    ):
        if last.startswith(prefix):
            msg = last[len(prefix):].strip()
            return msg or last
    if ": " in last and last.split(":", 1)[0].isidentifier():
        return last
    return None


def evaluate_subprocess(
    name: str,
    result: _SandboxResult,
    *,
    expected_stdout: str | None = None,
    expected_contains: tuple[str, ...] = (),
    expected_returncode: int = 0,
) -> CheckResult:
    if result.timed_out:
        return CheckResult(
            name, False, "timed out (possible infinite loop)",
            stderr=result.stderr, stdout=result.stdout,
            expected_stdout=expected_stdout,
        )
    if result.returncode != expected_returncode:
        err = extract_error(result.stderr)
        reason = err or (
            f"exit code {result.returncode} "
            f"(expected {expected_returncode})"
        )
        return CheckResult(
            name, False, reason,
            stderr=result.stderr, stdout=result.stdout,
            expected_stdout=expected_stdout,
        )
    if expected_stdout is not None:
        got = result.stdout.rstrip("\n")
        want = expected_stdout.rstrip("\n")
        if got != want:
            return CheckResult(
                name, False,
                f"stdout mismatch\nexpected: {want!r}\ngot: {got!r}",
                stderr=result.stderr, stdout=result.stdout,
                expected_stdout=expected_stdout,
            )
    missing = [s for s in expected_contains if s not in result.stdout]
    if missing:
        return CheckResult(
            name, False,
            "missing expected substring(s): "
            + ", ".join(repr(s) for s in missing),
            stderr=result.stderr, stdout=result.stdout,
            expected_stdout=expected_stdout,
        )
    return CheckResult(
        name, True,
        stderr=result.stderr, stdout=result.stdout,
        expected_stdout=expected_stdout,
    )
