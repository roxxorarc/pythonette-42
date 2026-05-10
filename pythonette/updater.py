import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def update(force: bool = False) -> int:
    """Pull latest pythonette and reinstall in-place.
    With force=True, fall back to running install.sh from scratch (slower
    but recovers from a corrupted venv).
    """
    repo_root = _find_repo_root(Path(__file__).resolve())
    if repo_root is None:
        console.print(
            "[red]error:[/red] pythonette is not installed from a git checkout"
        )
        return 1

    if force:
        return _full_reinstall(repo_root)

    branch = _current_branch(repo_root)
    if branch is None:
        console.print(
            "[yellow]warning:[/yellow] detached HEAD — falling back to "
            "full reinstall"
        )
        return _full_reinstall(repo_root)

    fetch = subprocess.run(
        ["git", "-C", str(repo_root), "fetch", "--quiet", "origin", branch],
        capture_output=True, text=True,
    )
    if fetch.returncode != 0:
        console.print(f"[red]git fetch failed:[/red]\n{fetch.stderr}")
        return fetch.returncode

    incoming = _commits_between(repo_root, "HEAD", f"origin/{branch}")
    if not incoming:
        console.print(
            Panel(
                Text("Already up to date.", style="green"),
                title="pythonette update",
                border_style="green",
            )
        )
        return 0

    body = Text()
    body.append(f"{len(incoming)} new commit(s) on origin/{branch}:\n\n")
    for sha, subject in incoming:
        body.append(f"  {sha}", style="yellow")
        body.append(f"  {subject}\n")
    console.print(
        Panel(body, title="pythonette update", border_style="cyan")
    )

    pull = subprocess.run(
        ["git", "-C", str(repo_root), "pull", "--ff-only", "--quiet"],
    )
    if pull.returncode != 0:
        console.print(
            "[red]git pull failed[/red] — try "
            "[bold]pythonette -u --force[/bold]"
        )
        return pull.returncode

    pip = Path(sys.executable).parent / "pip"
    if not pip.is_file():
        return _full_reinstall(repo_root)
    install = subprocess.run(
        [str(pip), "install", "--quiet", "--upgrade", "-e", str(repo_root)],
    )
    if install.returncode != 0:
        console.print(
            "[red]pip install failed[/red] — retry with "
            "[bold]pythonette -u --force[/bold]"
        )
        return install.returncode

    console.print(
        Panel(
            Text("Updated.", style="bold green"),
            title="pythonette update",
            border_style="green",
        )
    )
    return 0


def check_and_prompt() -> None:
    """Best-effort: fetch origin and, if the current branch is behind,
    prompt the user to install. Stays silent on any failure (no git,
    no network, detached HEAD, not a checkout, non-interactive stdin)."""
    try:
        repo_root = _find_repo_root(Path(__file__).resolve())
        if repo_root is None:
            return
        branch = _current_branch(repo_root)
        if branch is None:
            return
        fetch = subprocess.run(
            ["git", "-C", str(repo_root), "fetch", "--quiet", "origin", branch],
            capture_output=True, text=True, timeout=3,
        )
        if fetch.returncode != 0:
            return
        incoming = _commits_between(repo_root, "HEAD", f"origin/{branch}")
    except (subprocess.TimeoutExpired, OSError):
        return
    if not incoming:
        return

    body = Text()
    body.append(
        f"{len(incoming)} new commit(s) on origin/{branch}:\n\n"
    )
    for sha, subject in incoming[:5]:
        body.append(f"  {sha}", style="yellow")
        body.append(f"  {subject}\n")
    if len(incoming) > 5:
        body.append(f"  ... and {len(incoming) - 5} more\n", style="dim")
    console.print(
        Panel(body, title="pythonette update available", border_style="cyan")
    )

    if not sys.stdin.isatty():
        console.print(
            "[dim]run [bold]pythonette -u[/bold] to install.[/dim]"
        )
        return
    try:
        answer = input("Install now? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        console.print()
        return
    if answer in ("y", "yes"):
        update()


def _full_reinstall(repo_root: Path) -> int:
    install_sh = repo_root / "install.sh"
    if not install_sh.is_file():
        console.print(f"[red]error:[/red] missing {install_sh}")
        return 1
    pull = subprocess.run(["git", "-C", str(repo_root), "pull", "--ff-only"])
    if pull.returncode != 0:
        return pull.returncode
    return subprocess.run(["bash", str(install_sh)]).returncode


def _current_branch(repo_root: Path) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    name = proc.stdout.strip()
    return None if name in ("", "HEAD") else name


def _commits_between(
    repo_root: Path, base: str, head: str,
) -> list[tuple[str, str]]:
    proc = subprocess.run(
        [
            "git", "-C", str(repo_root), "log",
            "--pretty=format:%h %s", f"{base}..{head}",
        ],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return []
    out: list[tuple[str, str]] = []
    for line in proc.stdout.splitlines():
        if " " in line:
            sha, subject = line.split(" ", 1)
            out.append((sha, subject))
    return out


def _find_repo_root(start: Path) -> Path | None:
    for parent in (start, *start.parents):
        if (parent / ".git").exists() and (parent / "pyproject.toml").exists():
            return parent
    return None
