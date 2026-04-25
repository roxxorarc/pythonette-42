from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class TestCase:
    name: str
    harness: str | None = None
    stdin: str | None = None
    expected_stdout: str | None = None
    expected_contains: tuple[str, ...] = ()
    expected_returncode: int = 0
    timeout: float = 5.0


@dataclass(frozen=True)
class Exercise:
    module_id: str
    id: str
    filenames: tuple[str, ...]
    authorized: tuple[str, ...] = ()
    cases: tuple[TestCase, ...] = ()
    explain: str = ""

    @property
    def primary_file(self) -> str:
        return self.filenames[0]


@dataclass(frozen=True)
class Module:
    id: str
    title: str
    exercises: tuple[Exercise, ...]


class Registry:
    def __init__(self, modules: Iterable[Module]) -> None:
        self._by_filename: dict[str, Exercise] = {}
        self._modules: list[Module] = list(modules)
        for module in self._modules:
            for exercise in module.exercises:
                for fname in exercise.filenames:
                    if fname in self._by_filename:
                        raise ValueError(f"duplicate filename: {fname}")
                    self._by_filename[fname] = exercise

    def match(self, filename: str) -> Exercise | None:
        return self._by_filename.get(filename)

    def filenames(self) -> list[str]:
        return sorted(self._by_filename)

    @property
    def modules(self) -> list[Module]:
        return list(self._modules)
