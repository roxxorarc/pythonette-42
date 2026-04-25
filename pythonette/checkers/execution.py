from dataclasses import dataclass
from pathlib import Path

from pythonette.executor import ExecResult, run_case
from pythonette.subjects import Exercise, TestCase


@dataclass(frozen=True)
class CaseOutcome:
    case: TestCase
    ok: bool
    reason: str
    result: ExecResult


def _extract_error(stderr: str) -> str | None:
    lines = [ln for ln in stderr.splitlines() if ln.strip()]
    if not lines:
        return None
    last = lines[-1]
    for prefix in ("AssertionError:", "ImportError:", "ModuleNotFoundError:"):
        if last.startswith(prefix):
            msg = last[len(prefix):].strip()
            return msg or last
    if ": " in last and last.split(":", 1)[0].isidentifier():
        return last
    return None


def run_case_with_check(
    exercise: Exercise, exercise_dir: Path, case: TestCase
) -> CaseOutcome:
    result = run_case(exercise, exercise_dir, case)

    if result.timed_out:
        return CaseOutcome(case, False, "timed out (possible infinite loop)", result)

    if result.returncode != case.expected_returncode:
        err = _extract_error(result.stderr)
        if err:
            reason = err
        else:
            reason = (
                f"exit code {result.returncode} (expected "
                f"{case.expected_returncode})"
            )
        return CaseOutcome(case, False, reason, result)

    if case.expected_stdout is not None:
        got = result.stdout.rstrip("\n")
        want = case.expected_stdout.rstrip("\n")
        if got != want:
            reason = (
                "stdout mismatch\n"
                f"expected: {want!r}\n"
                f"got: {got!r}"
            )
            return CaseOutcome(
                case, False, reason, result
            )

    missing = [s for s in case.expected_contains if s not in result.stdout]
    if missing:
        reason = "missing expected substring(s): " + ", ".join(
            repr(s) for s in missing
        )
        return CaseOutcome(case, False, reason, result)

    return CaseOutcome(case, True, "", result)
