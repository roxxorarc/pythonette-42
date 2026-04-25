from dataclasses import dataclass
from pathlib import Path

from pythonette.subjects import REGISTRY, Exercise

_SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}


@dataclass(frozen=True)
class Found:
    file: Path
    exercise: Exercise


def detect(root: Path) -> list[Found]:
    root = root.resolve()
    findings: list[Found] = []
    seen: set[tuple[str, str]] = set()

    for path in _walk(root):
        if path.suffix != ".py":
            continue
        exercise = REGISTRY.match(path.name)
        if exercise is None:
            continue
        key = (exercise.module_id, exercise.id)
        if key in seen:
            continue
        seen.add(key)
        findings.append(Found(file=path, exercise=exercise))

    findings.sort(key=lambda f: (f.exercise.module_id, f.exercise.id))
    return findings


def _walk(root: Path):
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path
