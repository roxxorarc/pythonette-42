import subprocess
import sys
from pathlib import Path


def update() -> int:
    repo_root = _find_repo_root(Path(__file__).resolve())
    if repo_root is None:
        print("error: pythonette is not installed from a git checkout", file=sys.stderr)
        return 1

    install_sh = repo_root / "install.sh"
    if not install_sh.is_file():
        print(f"error: missing {install_sh}", file=sys.stderr)
        return 1

    pull = subprocess.run(["git", "-C", str(repo_root), "pull", "--ff-only"])
    if pull.returncode != 0:
        return pull.returncode

    return subprocess.run(["bash", str(install_sh)]).returncode


def _find_repo_root(start: Path) -> Path | None:
    for parent in (start, *start.parents):
        if (parent / ".git").exists() and (parent / "pyproject.toml").exists():
            return parent
    return None
