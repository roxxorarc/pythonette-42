"""Script-runner check: runpy a student file as __main__ and assert on
stdout / stderr substrings.

This subsumes the per-module ``_runpy_check`` / ``_argv_contains``
helpers that were previously hand-rolling InlineCheck snippets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pythonette.checks.base import (
    Check,
    CheckResult,
    evaluate_subprocess,
    run_in_sandbox,
)
from pythonette.checks.declarative import Assertion

if TYPE_CHECKING:
    from pythonette.subjects.registry import Exercise


_SUCCESS = "OK"


@dataclass(frozen=True)
class RunCheck(Check):
    """Run ``file`` as ``__main__`` via runpy, capture stdout and stderr
    separately, and assert that named substrings are present.

    ``argv`` overrides ``sys.argv`` (first element should normally be
    ``file``). ``fixtures`` is a tuple of ``(name, content)`` pairs that
    are written to the sandbox before the script runs (useful for
    file-IO exercises). ``allow_exception=True`` swallows raised
    exceptions and routes their traceback into stderr — use it when the
    script intentionally crashes (e.g. ``ImportError`` demos).

    For the ``module_06`` style where assertions don't care whether a
    needle is on stdout or stderr, set ``combined_contains`` instead of
    the channel-specific tuples.
    """

    label: str
    file: str
    argv: tuple[str, ...] | None = None
    stdin: str | None = None
    fixtures: tuple[tuple[str, str], ...] = ()
    stdout_contains: tuple[str, ...] = ()
    stderr_contains: tuple[str, ...] = ()
    combined_contains: tuple[str, ...] = ()
    # When True, lowercase both the captured output and the needles
    # before substring matching. Useful when student output capitalization
    # is unspecified.
    case_insensitive: bool = False
    allow_exception: bool = False
    # Optional post-run declarative assertions, evaluated after the
    # stdout/stderr substring checks, in the same sandbox. Useful when
    # a script has filesystem side effects worth asserting.
    post_setup: str = ""
    post_assertions: tuple[Assertion, ...] = ()
    timeout: float = 5.0

    @property
    def name(self) -> str:
        return self.label

    def _build_code(self) -> str:
        parts: list[str] = [
            "import runpy, sys, io\n",
            "from contextlib import redirect_stdout, redirect_stderr\n",
            "sys.path.insert(0, '.')\n",
        ]
        for fname, content in self.fixtures:
            parts.append(
                f"open({fname!r}, 'w', encoding='utf-8')"
                f".write({content!r})\n"
            )
        if self.argv is not None:
            parts.append(f"sys.argv = {list(self.argv)!r}\n")
        if self.stdin is not None:
            parts.append(f"sys.stdin = io.StringIO({self.stdin!r})\n")
        parts.append(
            "out = io.StringIO()\n"
            "err = io.StringIO()\n"
            "try:\n"
            "    with redirect_stdout(out), redirect_stderr(err):\n"
            f"        runpy.run_path({self.file!r}, run_name='__main__')\n"
            "except SystemExit:\n"
            "    pass\n"
        )
        if self.allow_exception:
            parts.append(
                "except BaseException as exc:\n"
                "    import traceback\n"
                "    traceback.print_exception(\n"
                "        type(exc), exc, exc.__traceback__, file=err\n"
                "    )\n"
            )
        parts.append(
            "stdout = out.getvalue()\n"
            "stderr = err.getvalue()\n"
            "combined = stdout + '\\n' + stderr\n"
        )
        if self.case_insensitive:
            parts.append(
                "_stdout_match = stdout.lower()\n"
                "_stderr_match = stderr.lower()\n"
                "_combined_match = combined.lower()\n"
            )
            stdout_var, stderr_var, combined_var = (
                "_stdout_match", "_stderr_match", "_combined_match",
            )
            def _needle(s: str) -> str: return s.lower()
        else:
            stdout_var, stderr_var, combined_var = (
                "stdout", "stderr", "combined",
            )
            def _needle(s: str) -> str: return s
        for needle in self.stdout_contains:
            parts.append(
                f"assert {_needle(needle)!r} in {stdout_var}, (\n"
                f"    'missing in stdout: ' + {needle!r}\n"
                "    + '\\n--- stdout ---\\n' + stdout\n"
                "    + '\\n--- stderr ---\\n' + stderr\n"
                ")\n"
            )
        for needle in self.stderr_contains:
            parts.append(
                f"assert {_needle(needle)!r} in {stderr_var}, (\n"
                f"    'missing in stderr: ' + {needle!r}\n"
                "    + '\\n--- stdout ---\\n' + stdout\n"
                "    + '\\n--- stderr ---\\n' + stderr\n"
                ")\n"
            )
        for needle in self.combined_contains:
            parts.append(
                f"assert {_needle(needle)!r} in {combined_var}, (\n"
                f"    'missing in output: ' + {needle!r}\n"
                "    + '\\n--- output ---\\n' + combined\n"
                ")\n"
            )
        if self.post_setup:
            parts.append(self.post_setup.rstrip("\n") + "\n")
        for assertion in self.post_assertions:
            parts.append(assertion.to_code().rstrip("\n") + "\n")
        parts.append("print('OK')\n")
        return "".join(parts)

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        result = run_in_sandbox(
            exercise, exercise_dir, self._build_code(),
            stdin=self.stdin, timeout=self.timeout,
        )
        return evaluate_subprocess(
            self.name, result, expected_stdout=_SUCCESS,
        )
