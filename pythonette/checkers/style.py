import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StyleResult:
    ok: bool
    output: str


def check_flake8(file: Path) -> StyleResult:
    proc = subprocess.run(
        [sys.executable, "-m", "flake8", str(file)],
        capture_output=True,
        text=True,
    )
    output = (proc.stdout + proc.stderr).strip()
    return StyleResult(ok=proc.returncode == 0, output=output)
