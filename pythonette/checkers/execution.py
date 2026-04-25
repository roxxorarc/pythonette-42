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


def run_case_with_check(
    exercise: Exercise, exercise_dir: Path, case: TestCase
) -> CaseOutcome:
    result = run_case(exercise, exercise_dir, case)

    if result.timed_out:
        return CaseOutcome(case, False, "timed out (possible infinite loop)", result)

    if result.returncode != case.expected_returncode:
        reason = (
            f"exit code {result.returncode} (expected "
            f"{case.expected_returncode})"
        )
        if result.stderr.strip():
            reason += f"\nstderr:\n{result.stderr.strip()}"
        return CaseOutcome(case, False, reason, result)

    if case.expected_stdout is not None:
        got = result.stdout.rstrip("\n")
        want = case.expected_stdout.rstrip("\n")
        if got != want:
            return CaseOutcome(
                case, False, "stdout mismatch", result
            )

    missing = [s for s in case.expected_contains if s not in result.stdout]
    if missing:
        reason = "missing expected substring(s): " + ", ".join(
            repr(s) for s in missing
        )
        return CaseOutcome(case, False, reason, result)

    return CaseOutcome(case, True, "", result)
