"""Declarative AST-based static checks.

These promote the ad-hoc AST-scanning InlineCheck snippets into typed
:class:`Check` subclasses. Each one walks the AST of one or more files
and asserts a structural property without running the student code.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pythonette.checks.base import Check, CheckResult

if TYPE_CHECKING:
    from pythonette.subjects.registry import Exercise


def _iter_py_files(exercise_dir: Path, scope: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    for entry in scope:
        p = exercise_dir / entry
        if not p.exists():
            continue
        if p.is_dir():
            out.extend(
                q for q in sorted(p.rglob("*.py"))
                if "__pycache__" not in q.parts
            )
        elif p.suffix == ".py":
            out.append(p)
    return out


_AST_NODES: dict[str, type[ast.AST]] = {
    "Try": ast.Try,
    "Raise": ast.Raise,
    "With": ast.With,
    "AsyncWith": ast.AsyncWith,
    "Return": ast.Return,
    "ListComp": ast.ListComp,
    "DictComp": ast.DictComp,
    "SetComp": ast.SetComp,
    "GeneratorExp": ast.GeneratorExp,
    "Import": ast.Import,
    "ImportFrom": ast.ImportFrom,
    "FunctionDef": ast.FunctionDef,
    "AsyncFunctionDef": ast.AsyncFunctionDef,
    "ClassDef": ast.ClassDef,
}


def _resolve_node_types(names: tuple[str, ...]) -> tuple[type[ast.AST], ...]:
    types: list[type[ast.AST]] = []
    for n in names:
        if n not in _AST_NODES:
            raise ValueError(
                f"unknown AST node type {n!r}; known: "
                f"{sorted(_AST_NODES)!r}"
            )
        types.append(_AST_NODES[n])
    return tuple(types)


def _parse_or_fail(
    name: str, file: Path,
) -> tuple[ast.AST | None, CheckResult | None]:
    try:
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        return tree, None
    except SyntaxError as exc:
        return None, CheckResult(
            name, False, f"syntax error in {file.name}: {exc}",
        )


@dataclass(frozen=True)
class FilesExistCheck(Check):
    """Assert that every named path exists on disk in the exercise dir."""

    label: str
    paths: tuple[str, ...]

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        missing = [
            p for p in self.paths
            if not (exercise_dir / p).exists()
        ]
        if missing:
            return CheckResult(
                self.name, False,
                "missing required project file(s):\n  "
                + "\n  ".join(missing),
            )
        return CheckResult(self.name, True)


@dataclass(frozen=True)
class TopLevelFunctionsCheck(Check):
    """Assert that ``file`` defines the named functions at the top level."""

    label: str
    file: str
    functions: tuple[str, ...]

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        path = exercise_dir / self.file
        if not path.is_file():
            return CheckResult(self.name, False, f"{self.file} not found")
        tree, err = _parse_or_fail(self.name, path)
        if err:
            return err
        FN = (ast.FunctionDef, ast.AsyncFunctionDef)
        defs = [n.name for n in tree.body if isinstance(n, FN)]  # type: ignore[union-attr]
        missing = [n for n in self.functions if n not in defs]
        if missing:
            return CheckResult(
                self.name, False,
                f"missing top-level function(s) {missing!r} "
                f"(found: {defs!r})",
            )
        return CheckResult(self.name, True)


@dataclass(frozen=True)
class ClassMethodsCheck(Check):
    """For each ``class -> method tuple``, assert the class is defined and
    has the named methods. Walks the whole AST so nested classes work."""

    label: str
    file: str
    expected: tuple[tuple[str, tuple[str, ...]], ...]

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        path = exercise_dir / self.file
        if not path.is_file():
            return CheckResult(self.name, False, f"{self.file} not found")
        tree, err = _parse_or_fail(self.name, path)
        if err:
            return err
        FN = (ast.FunctionDef, ast.AsyncFunctionDef)
        by_class: dict[str, set[str]] = {}
        for node in ast.walk(tree):  # type: ignore[arg-type]
            if isinstance(node, ast.ClassDef):
                by_class[node.name] = {
                    f.name for f in node.body if isinstance(f, FN)
                }
        for cls, methods in self.expected:
            if cls not in by_class:
                return CheckResult(
                    self.name, False,
                    f"missing class {cls!r}; "
                    f"found: {sorted(by_class)!r}",
                )
            missing = [m for m in methods if m not in by_class[cls]]
            if missing:
                return CheckResult(
                    self.name, False,
                    f"class {cls!r} missing method(s) {missing!r}; "
                    f"has: {sorted(by_class[cls])!r}",
                )
        return CheckResult(self.name, True)


@dataclass(frozen=True)
class NoForbiddenCallsCheck(Check):
    """Forbid calls to the named bare functions (e.g. ``input``, ``eval``).

    Method calls (``foo.bar()``) are not flagged."""

    label: str
    scope: tuple[str, ...]
    forbidden: tuple[str, ...]

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        forbidden = set(self.forbidden)
        for f in _iter_py_files(exercise_dir, self.scope):
            tree, err = _parse_or_fail(self.name, f)
            if err:
                return err
            for n in ast.walk(tree):  # type: ignore[arg-type]
                if (
                    isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Name)
                    and n.func.id in forbidden
                ):
                    rel = f.relative_to(exercise_dir)
                    return CheckResult(
                        self.name, False,
                        f"forbidden call {n.func.id}() at "
                        f"{rel}:{n.lineno}",
                    )
        return CheckResult(self.name, True)


@dataclass(frozen=True)
class NoSysPathMutationCheck(Check):
    """Forbid ``sys.path.append/insert/extend/...`` calls."""

    label: str
    scope: tuple[str, ...]

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        for f in _iter_py_files(exercise_dir, self.scope):
            tree, err = _parse_or_fail(self.name, f)
            if err:
                return err
            for n in ast.walk(tree):  # type: ignore[arg-type]
                if (
                    isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and isinstance(n.func.value, ast.Attribute)
                    and n.func.value.attr == "path"
                    and isinstance(n.func.value.value, ast.Name)
                    and n.func.value.value.id == "sys"
                ):
                    rel = f.relative_to(exercise_dir)
                    return CheckResult(
                        self.name, False,
                        f"forbidden sys.path.{n.func.attr}() at "
                        f"{rel}:{n.lineno}",
                    )
        return CheckResult(self.name, True)


@dataclass(frozen=True)
class NoNodeTypesCheck(Check):
    """Walk the AST of each scoped file and forbid any node whose type
    appears in ``node_types`` (string names like ``'With'``, ``'Try'``).

    If ``inside_function`` is set, the scan is restricted to the body of
    the named function (whole-file scan when ``None``)."""

    label: str
    scope: tuple[str, ...]
    node_types: tuple[str, ...]
    inside_function: str | None = None
    reason: str | None = None

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        types = _resolve_node_types(self.node_types)
        for f in _iter_py_files(exercise_dir, self.scope):
            tree, err = _parse_or_fail(self.name, f)
            if err:
                return err
            scope_node: ast.AST | None = tree
            if self.inside_function is not None:
                scope_node = next(
                    (
                        n for n in ast.walk(tree)  # type: ignore[arg-type]
                        if isinstance(
                            n, (ast.FunctionDef, ast.AsyncFunctionDef),
                        )
                        and n.name == self.inside_function
                    ),
                    None,
                )
                if scope_node is None:
                    return CheckResult(
                        self.name, False,
                        f"function {self.inside_function!r} not found "
                        f"in {f.name}",
                    )
            for n in ast.walk(scope_node):
                if isinstance(n, types):
                    rel = f.relative_to(exercise_dir)
                    msg = self.reason or (
                        f"forbidden {type(n).__name__} node"
                    )
                    return CheckResult(
                        self.name, False,
                        f"{msg} at {rel}:{getattr(n, 'lineno', '?')}",
                    )
        return CheckResult(self.name, True)


@dataclass(frozen=True)
class RequireNodeTypesCheck(Check):
    """Each node type in ``node_types`` must appear at least once in the
    scanned scope.

    Default scope is the whole file. Set ``inside_function`` to limit to
    a named function's body, or ``top_level_only=True`` to consider only
    immediate children of the module (useful to require a free top-level
    function distinct from class methods)."""

    label: str
    scope: tuple[str, ...]
    node_types: tuple[str, ...]
    inside_function: str | None = None
    top_level_only: bool = False
    reason: str | None = None

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        types = _resolve_node_types(self.node_types)
        present = {t: False for t in types}
        for f in _iter_py_files(exercise_dir, self.scope):
            tree, err = _parse_or_fail(self.name, f)
            if err:
                return err
            if self.top_level_only:
                nodes = list(tree.body)  # type: ignore[union-attr]
            else:
                scope_node: ast.AST | None = tree
                if self.inside_function is not None:
                    scope_node = next(
                        (
                            n for n in ast.walk(tree)  # type: ignore[arg-type]
                            if isinstance(
                                n,
                                (ast.FunctionDef, ast.AsyncFunctionDef),
                            )
                            and n.name == self.inside_function
                        ),
                        None,
                    )
                    if scope_node is None:
                        return CheckResult(
                            self.name, False,
                            f"function {self.inside_function!r} not "
                            f"found in {f.name}",
                        )
                nodes = list(ast.walk(scope_node))
            for n in nodes:
                for t in types:
                    if isinstance(n, t):
                        present[t] = True
        missing = [
            self.node_types[i] for i, t in enumerate(types)
            if not present[t]
        ]
        if missing:
            msg = self.reason or "missing required AST node(s)"
            return CheckResult(
                self.name, False, f"{msg}: {missing!r}",
            )
        return CheckResult(self.name, True)


@dataclass(frozen=True)
class ClassNamePresenceCheck(Check):
    """For each substring in ``must_contain``, require at least one
    ``ClassDef`` in the scoped files whose name contains that substring
    (case-insensitive). Useful for 'must define a CSV class and a JSON
    class' constraints where the exact name is up to the student.

    ``reason`` overrides the default failure message."""

    label: str
    scope: tuple[str, ...]
    must_contain: tuple[str, ...]
    reason: str | None = None

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        names: list[str] = []
        for f in _iter_py_files(exercise_dir, self.scope):
            tree, err = _parse_or_fail(self.name, f)
            if err:
                return err
            for n in ast.walk(tree):  # type: ignore[arg-type]
                if isinstance(n, ast.ClassDef):
                    names.append(n.name)
        lowered = [n.lower() for n in names]
        missing = [
            needle for needle in self.must_contain
            if not any(needle.lower() in n for n in lowered)
        ]
        if missing:
            base = self.reason or "missing class name(s) containing"
            return CheckResult(
                self.name, False,
                f"{base}: {missing!r}; defined classes: {names!r}",
            )
        return CheckResult(self.name, True)


@dataclass(frozen=True)
class ImportStyleCheck(Check):
    """Assert that ``file`` uses the requested mix of import styles.

    Set ``require_absolute=True`` to require at least one absolute import
    (``import x`` or ``from x import y``); ``require_relative=True`` to
    require at least one relative import (``from . import …``)."""

    label: str
    file: str
    require_absolute: bool = False
    require_relative: bool = False

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        path = exercise_dir / self.file
        if not path.is_file():
            return CheckResult(self.name, False, f"{self.file} not found")
        tree, err = _parse_or_fail(self.name, path)
        if err:
            return err
        absolute = relative = False
        for n in ast.walk(tree):  # type: ignore[arg-type]
            if isinstance(n, ast.Import):
                absolute = True
            elif isinstance(n, ast.ImportFrom):
                if (n.level or 0) > 0:
                    relative = True
                else:
                    absolute = True
        if self.require_absolute and not absolute:
            return CheckResult(
                self.name, False,
                f"{self.file}: must use at least one absolute import",
            )
        if self.require_relative and not relative:
            return CheckResult(
                self.name, False,
                f"{self.file}: must use at least one relative import",
            )
        return CheckResult(self.name, True)


@dataclass(frozen=True)
class FunctionTryHandlersCheck(Check):
    """Inside ``function``, require at least one ``try`` block whose
    except clause(s) cover ``min_handlers`` distinct exception types
    (counted via ``len(handlers)`` plus tuple-of-types unpacking)."""

    label: str
    file: str
    function: str
    min_handlers: int = 2
    reason: str | None = None

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        path = exercise_dir / self.file
        if not path.is_file():
            return CheckResult(self.name, False, f"{self.file} not found")
        tree, err = _parse_or_fail(self.name, path)
        if err:
            return err
        fn = next(
            (
                n for n in ast.walk(tree)  # type: ignore[arg-type]
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n.name == self.function
            ),
            None,
        )
        if fn is None:
            return CheckResult(
                self.name, False,
                f"function {self.function!r} not found",
            )
        for node in ast.walk(fn):
            if not isinstance(node, ast.Try):
                continue
            count = len(node.handlers)
            for h in node.handlers:
                if isinstance(h.type, ast.Tuple):
                    count = max(count, len(h.type.elts))
            if count >= self.min_handlers:
                return CheckResult(self.name, True)
        msg = self.reason or (
            f"{self.function} must contain a try block catching at "
            f"least {self.min_handlers} exception types"
        )
        return CheckResult(self.name, False, msg)


@dataclass(frozen=True)
class FunctionTryFinallyReturnCheck(Check):
    """Inside ``function``: require a try/except/finally where some
    except handler contains a ``return``. Used by module 02 ex4 to
    enforce 'cleanup runs even on error, then exit'."""

    label: str
    file: str
    function: str

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        path = exercise_dir / self.file
        if not path.is_file():
            return CheckResult(self.name, False, f"{self.file} not found")
        tree, err = _parse_or_fail(self.name, path)
        if err:
            return err
        fn = next(
            (
                n for n in ast.walk(tree)  # type: ignore[arg-type]
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n.name == self.function
            ),
            None,
        )
        if fn is None:
            return CheckResult(
                self.name, False,
                f"function {self.function!r} not found",
            )
        tries = [n for n in ast.walk(fn) if isinstance(n, ast.Try)]
        if not tries:
            return CheckResult(
                self.name, False,
                f"{self.function} must use try/except/finally",
            )
        if not any(t.finalbody for t in tries):
            return CheckResult(
                self.name, False,
                f"{self.function} must include a finally block",
            )
        has_return = any(
            isinstance(s, ast.Return)
            for t in tries
            for h in t.handlers
            for s in ast.walk(h)
        )
        if not has_return:
            return CheckResult(
                self.name, False,
                f"{self.function} must return from an except handler",
            )
        return CheckResult(self.name, True)
