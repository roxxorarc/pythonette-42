from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pythonette.checks.base import Check, CheckResult

if TYPE_CHECKING:
    from pythonette.subjects.registry import Exercise


def _is_main_guard(test: ast.expr) -> bool:
    if not isinstance(test, ast.Compare):
        return False
    if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return False
    if len(test.comparators) != 1:
        return False
    left = test.left
    right = test.comparators[0]
    name_main = (
        isinstance(left, ast.Name) and left.id == "__name__"
        and isinstance(right, ast.Constant) and right.value == "__main__"
    )
    main_name = (
        isinstance(left, ast.Constant) and left.value == "__main__"
        and isinstance(right, ast.Name) and right.id == "__name__"
    )
    return name_main or main_name


@dataclass(frozen=True)
class StructureCheck(Check):
    file: str
    functions: tuple[str, ...] = ()
    classes: tuple[str, ...] = ()
    allow_extra_functions: bool = False
    allow_extra_classes: bool = False
    allow_main_guard: bool = False
    require_main_guard: bool = False
    allow_top_level_assigns: bool = False
    allow_imports: bool = False
    label: str | None = None

    @property
    def name(self) -> str:
        if self.label:
            return f"structure: {self.label}"
        bits = []
        if self.functions:
            bits.append(f"functions={', '.join(self.functions)}")
        if self.classes:
            bits.append(f"classes={', '.join(self.classes)}")
        if self.require_main_guard:
            bits.append("__main__ guard")
        rules = ", ".join(bits) if bits else "no top-level extras"
        return f"structure ({self.file}): {rules}"

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        path = exercise_dir / self.file
        if not path.is_file():
            return CheckResult(self.name, False, f"{self.file} not found")
        try:
            tree = ast.parse(
                path.read_text(encoding="utf-8"), filename=self.file
            )
        except SyntaxError as exc:
            return CheckResult(self.name, False, f"syntax error: {exc}")

        FN = (ast.FunctionDef, ast.AsyncFunctionDef)
        functions = [n.name for n in tree.body if isinstance(n, FN)]
        classes = [
            n.name for n in tree.body if isinstance(n, ast.ClassDef)
        ]
        has_main_guard = False

        for idx, node in enumerate(tree.body):
            if isinstance(node, FN) or isinstance(node, ast.ClassDef):
                continue
            if (
                idx == 0
                and isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                continue
            if self.allow_imports and isinstance(
                node, (ast.Import, ast.ImportFrom)
            ):
                continue
            if self.allow_top_level_assigns and isinstance(
                node, (ast.Assign, ast.AnnAssign)
            ):
                continue
            if isinstance(node, ast.If) and _is_main_guard(node.test):
                if self.require_main_guard or self.allow_main_guard:
                    has_main_guard = True
                    continue
                return CheckResult(
                    self.name, False,
                    f"forbidden if __name__ == '__main__': "
                    f"guard at line {node.lineno}",
                )
            return CheckResult(
                self.name, False,
                f"forbidden top-level statement at line {node.lineno}: "
                f"{type(node).__name__}",
            )

        if self.functions:
            expected = list(self.functions)
            if self.allow_extra_functions:
                missing = [f for f in expected if f not in functions]
                if missing:
                    return CheckResult(
                        self.name, False,
                        f"missing function(s) {missing!r} "
                        f"(got {functions!r})",
                    )
            elif functions != expected:
                return CheckResult(
                    self.name, False,
                    f"top-level functions: got={functions!r} "
                    f"expected={expected!r}",
                )

        if self.classes:
            expected_cls = list(self.classes)
            if self.allow_extra_classes:
                missing = [c for c in expected_cls if c not in classes]
                if missing:
                    return CheckResult(
                        self.name, False,
                        f"missing class(es) {missing!r} "
                        f"(got {classes!r})",
                    )
            elif classes != expected_cls:
                return CheckResult(
                    self.name, False,
                    f"classes: got={classes!r} expected={expected_cls!r}",
                )

        if self.require_main_guard and not has_main_guard:
            return CheckResult(
                self.name, False,
                "missing if __name__ == '__main__': guard",
            )

        return CheckResult(self.name, True)


_LANGUAGE_FEATURES: frozenset[str] = frozenset({
    "super",
    "BaseException", "Exception",
    "ArithmeticError", "ZeroDivisionError", "OverflowError",
    "FloatingPointError",
    "AssertionError", "AttributeError",
    "ImportError", "ModuleNotFoundError",
    "LookupError", "IndexError", "KeyError",
    "NameError", "UnboundLocalError",
    "OSError", "IOError",
    "FileNotFoundError", "FileExistsError", "PermissionError",
    "IsADirectoryError", "NotADirectoryError",
    "TimeoutError", "InterruptedError", "BlockingIOError",
    "ConnectionError", "ConnectionResetError",
    "ConnectionAbortedError", "ConnectionRefusedError",
    "RuntimeError", "NotImplementedError", "RecursionError",
    "StopIteration", "StopAsyncIteration",
    "SyntaxError", "IndentationError", "TabError",
    "SystemError", "TypeError", "ValueError", "UnicodeError",
    "UnicodeDecodeError", "UnicodeEncodeError",
    "MemoryError",
    "Warning", "UserWarning", "DeprecationWarning",
    "PendingDeprecationWarning", "RuntimeWarning",
    "SyntaxWarning", "FutureWarning",
})


@dataclass(frozen=True)
class AuthorizedCheck(Check):
    file: str
    authorized: tuple[str, ...]
    allow_method_calls: bool = True

    @property
    def name(self) -> str:
        return (
            f"authorized ({self.file}): only "
            f"{', '.join(self.authorized)}() may be called"
        )

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        path = exercise_dir / self.file
        if not path.is_file():
            return CheckResult(self.name, False, f"{self.file} not found")
        try:
            tree = ast.parse(
                path.read_text(encoding="utf-8"), filename=self.file
            )
        except SyntaxError as exc:
            return CheckResult(self.name, False, f"syntax error: {exc}")

        DEF = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        local = {n.name for n in ast.walk(tree) if isinstance(n, DEF)}
        params: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                a = node.args
                for arg in (
                    a.posonlyargs + a.args + a.kwonlyargs
                ):
                    params.add(arg.arg)
                if a.vararg:
                    params.add(a.vararg.arg)
                if a.kwarg:
                    params.add(a.kwarg.arg)
        authorized = set(self.authorized)
        allowed = local | authorized | params | _LANGUAGE_FEATURES

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if (
                not self.allow_method_calls
                and isinstance(node.func, ast.Attribute)
            ):
                return CheckResult(
                    self.name, False,
                    f"forbidden method call .{node.func.attr}() "
                    f"at line {node.lineno}",
                )
            if isinstance(node.func, ast.Name):
                if node.func.id not in allowed:
                    return CheckResult(
                        self.name, False,
                        f"forbidden call {node.func.id}() "
                        f"at line {node.lineno} "
                        f"(authorized: {', '.join(sorted(authorized))})",
                    )

        return CheckResult(self.name, True)


@dataclass(frozen=True)
class ImportCheck(Check):
    file: str
    allowed: tuple[str, ...]

    @property
    def name(self) -> str:
        return (
            f"imports ({self.file}): only {', '.join(self.allowed)} "
            f"may be imported"
        )

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        path = exercise_dir / self.file
        if not path.is_file():
            return CheckResult(self.name, False, f"{self.file} not found")
        try:
            tree = ast.parse(
                path.read_text(encoding="utf-8"), filename=self.file
            )
        except SyntaxError as exc:
            return CheckResult(self.name, False, f"syntax error: {exc}")

        allowed = set(self.allowed)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root not in allowed:
                        return CheckResult(
                            self.name, False,
                            f"forbidden import '{alias.name}' at line "
                            f"{node.lineno} (allowed: "
                            f"{', '.join(sorted(allowed)) or 'none'})",
                        )
            elif isinstance(node, ast.ImportFrom):
                module = (node.module or "").split(".", 1)[0]
                if module and module not in allowed:
                    return CheckResult(
                        self.name, False,
                        f"forbidden import 'from {node.module}' at line "
                        f"{node.lineno} (allowed: "
                        f"{', '.join(sorted(allowed)) or 'none'})",
                    )

        return CheckResult(self.name, True)
