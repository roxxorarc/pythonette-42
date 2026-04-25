import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pythonette.subjects import Exercise, TestCase

_HARNESS_NAME = "_pythonette_harness.py"


@dataclass(frozen=True)
class ExecResult:
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool


def run_case(exercise: Exercise, exercise_dir: Path, case: TestCase) -> ExecResult:
    with tempfile.TemporaryDirectory(prefix="pythonette_") as tmp:
        sandbox = Path(tmp)
        for fname in exercise.filenames:
            src = exercise_dir / fname
            if src.is_file():
                shutil.copy(src, sandbox / fname)

        if case.harness is None:
            target = sandbox / exercise.primary_file
        else:
            target = sandbox / _HARNESS_NAME
            target.write_text(case.harness)

        return _run([sys.executable, target.name], sandbox, case)


def _run(cmd: list[str], cwd: Path, case: TestCase) -> ExecResult:
    try:
        proc = subprocess.run(
            cmd,
            input=case.stdin,
            capture_output=True,
            text=True,
            timeout=case.timeout,
            cwd=str(cwd),
        )
    except subprocess.TimeoutExpired as exc:
        return ExecResult(
            stdout=(exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            stderr=(exc.stderr or b"").decode() if isinstance(exc.stderr, bytes) else (exc.stderr or ""),
            returncode=-1,
            timed_out=True,
        )
    return ExecResult(
        stdout=proc.stdout,
        stderr=proc.stderr,
        returncode=proc.returncode,
        timed_out=False,
    )
