from dataclasses import dataclass
from typing import Iterable

from pythonette.checks import Check


@dataclass(frozen=True)
class Exercise:
    module_id: str
    id: str
    filenames: tuple[str, ...]
    authorized: tuple[str, ...] = ()
    checks: tuple[Check, ...] = ()
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
