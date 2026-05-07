"""Declarative assertion DSL for sandbox runtime checks.

The runtime sandbox always wants the same shape:

    import sys
    sys.path.insert(0, '.')
    <user setup, usually one import line>
    <a few asserts>
    print('OK')

Writing that as a hand-crafted Python string for every test is noisy and
error-prone (escaping, f-string nesting, repeated boilerplate).
``AssertCheck`` lets a test author declare *what* to verify with typed
:class:`Assertion` objects; the boilerplate is generated.

Example::

    AssertCheck(
        label="alchemy/elements.py exposes create_earth / create_air",
        setup="from alchemy import elements as alch_el",
        assertions=(
            Eq("alch_el.create_earth()", "Earth element created"),
            Eq("alch_el.create_air()", "Air element created"),
        ),
    )
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pythonette.checks.base import (
    Check,
    CheckResult,
    evaluate_subprocess,
    run_in_sandbox,
)

if TYPE_CHECKING:
    from pythonette.subjects.registry import Exercise


_SUCCESS = "OK"


class Assertion(ABC):
    """One declarative assertion that emits a snippet of Python code.

    The snippet must:
      * leave no syntax error,
      * raise ``AssertionError`` with a helpful message on failure,
      * not print anything on success (``AssertCheck`` adds the trailing
        ``print('OK')``).
    """

    @abstractmethod
    def to_code(self) -> str: ...


@dataclass(frozen=True)
class Eq(Assertion):
    """``assert <expr> == <value>``.

    ``value`` is rendered with ``repr`` so any literal (str, int, tuple,
    dict, …) works."""

    expr: str
    value: object

    def to_code(self) -> str:
        return (
            f"_v = ({self.expr})\n"
            f"_want = {self.value!r}\n"
            f"assert _v == _want, (\n"
            f"    {self.expr!r} + ' == ' + repr(_v) + "
            f"', expected ' + repr(_want)\n"
            f")"
        )


@dataclass(frozen=True)
class Contains(Assertion):
    """``assert <substring> in <expr>`` (substring may be any literal)."""

    expr: str
    substring: object

    def to_code(self) -> str:
        return (
            f"_v = ({self.expr})\n"
            f"_needle = {self.substring!r}\n"
            f"assert _needle in _v, (\n"
            f"    repr(_needle) + ' not in ' + {self.expr!r} + "
            f"' == ' + repr(_v)\n"
            f")"
        )


@dataclass(frozen=True)
class ContainsAll(Assertion):
    """All listed substrings must be in the expression's value."""

    expr: str
    substrings: tuple[object, ...]

    def to_code(self) -> str:
        return (
            f"_v = ({self.expr})\n"
            f"for _needle in {list(self.substrings)!r}:\n"
            f"    assert _needle in _v, (\n"
            f"        {self.expr!r} + ': missing ' + "
            f"repr(_needle) + ' in ' + repr(_v)\n"
            f"    )"
        )


@dataclass(frozen=True)
class Truthy(Assertion):
    """``assert <expr>`` — true-ish."""

    expr: str
    message: str | None = None

    def to_code(self) -> str:
        msg = self.message or f"{self.expr} must be truthy"
        return f"assert ({self.expr}), {msg!r}"


@dataclass(frozen=True)
class Falsy(Assertion):
    """``assert not <expr>``."""

    expr: str
    message: str | None = None

    def to_code(self) -> str:
        msg = self.message or f"{self.expr} must be falsy"
        return f"assert not ({self.expr}), {msg!r}"


@dataclass(frozen=True)
class IsInstance(Assertion):
    """``assert isinstance(<expr>, <type>)``.

    ``type_`` is a *string* type expression evaluated in the sandbox
    (e.g. ``'set'``, ``'tuple'``, ``'mod.MyClass'``) — that way the
    type does not need to be importable from the test author's process."""

    expr: str
    type_: str

    def to_code(self) -> str:
        return (
            f"_v = ({self.expr})\n"
            f"assert isinstance(_v, {self.type_}), (\n"
            f"    {self.expr!r} + ': expected ' + {self.type_!r} + "
            f"', got ' + type(_v).__name__\n"
            f")"
        )


@dataclass(frozen=True)
class HasAttr(Assertion):
    """``assert hasattr(<obj>, <attr>)``."""

    obj: str
    attr: str
    message: str | None = None

    def to_code(self) -> str:
        msg = self.message or f"{self.obj} must expose attribute {self.attr!r}"
        return f"assert hasattr({self.obj}, {self.attr!r}), {msg!r}"


@dataclass(frozen=True)
class LacksAttr(Assertion):
    """``assert not hasattr(<obj>, <attr>)``."""

    obj: str
    attr: str
    message: str | None = None

    def to_code(self) -> str:
        msg = (
            self.message
            or f"{self.obj} must NOT expose attribute {self.attr!r}"
        )
        return f"assert not hasattr({self.obj}, {self.attr!r}), {msg!r}"


@dataclass(frozen=True)
class Subclass(Assertion):
    """``assert issubclass(<child>, <parent>)``.

    Both arguments are *expressions* evaluated in the sandbox."""

    child: str
    parent: str
    message: str | None = None

    def to_code(self) -> str:
        msg = (
            self.message
            or f"{self.child} must be a subclass of {self.parent}"
        )
        return (
            f"assert issubclass({self.child}, {self.parent}), {msg!r}"
        )


@dataclass(frozen=True)
class Is(Assertion):
    """``assert <a> is <b>``."""

    a: str
    b: str
    message: str | None = None

    def to_code(self) -> str:
        msg = self.message or f"{self.a} is not {self.b}"
        return f"assert ({self.a}) is ({self.b}), {msg!r}"


@dataclass(frozen=True)
class IsNot(Assertion):
    """``assert <a> is not <b>``."""

    a: str
    b: str
    message: str | None = None

    def to_code(self) -> str:
        msg = self.message or f"{self.a} unexpectedly is {self.b}"
        return f"assert ({self.a}) is not ({self.b}), {msg!r}"


@dataclass(frozen=True)
class Raises(Assertion):
    """A statement that must raise one of the listed exception type(s).

    ``statement`` is rendered as-is (single line). ``exception_types`` is
    a tuple of *type expressions* evaluated in the sandbox — pass strings
    like ``'ImportError'``, ``'(ImportError, AttributeError)'``."""

    statement: str
    exception_types: tuple[str, ...] = ("Exception",)
    message: str | None = None

    def to_code(self) -> str:
        if len(self.exception_types) == 1:
            excs = self.exception_types[0]
        else:
            excs = "(" + ", ".join(self.exception_types) + ")"
        msg = (
            self.message
            or f"{self.statement!r} must raise {excs}"
        )
        return (
            f"try:\n"
            f"    {self.statement}\n"
            f"    raise AssertionError({msg!r})\n"
            f"except {excs}:\n"
            f"    pass"
        )


@dataclass(frozen=True)
class NotRaises(Assertion):
    """A statement that must NOT raise — wraps it in try/except and
    converts any failure into a clear ``AssertionError``.

    Use when constructor arity / a happy-path call should succeed without
    bothering to introspect the return value."""

    statement: str
    exception_types: tuple[str, ...] = ("Exception",)
    message: str | None = None

    def to_code(self) -> str:
        if len(self.exception_types) == 1:
            excs = self.exception_types[0]
        else:
            excs = "(" + ", ".join(self.exception_types) + ")"
        msg = self.message or f"{self.statement!r} unexpectedly raised"
        return (
            f"try:\n"
            f"    {self.statement}\n"
            f"except {excs} as _exc:\n"
            f"    raise AssertionError(\n"
            f"        {msg!r} + ': ' + type(_exc).__name__ + ': ' + str(_exc)\n"
            f"    )"
        )


@dataclass(frozen=True)
class Exec(Assertion):
    """Escape hatch: run an arbitrary multi-line snippet verbatim.

    Use only when no typed assertion fits — for stateful flows that need
    to instantiate, mutate, then assert. Prefer the typed helpers above
    for everything else."""

    code: str

    def to_code(self) -> str:
        return self.code


@dataclass(frozen=True)
class AssertCheck(Check):
    """A declarative runtime check: setup + a list of typed assertions.

    The harness wraps the snippet with the standard sandbox prelude
    (``import sys; sys.path.insert(0, '.')``) and trailing ``print('OK')``,
    so test authors only declare what to verify.
    """

    label: str
    setup: str = ""
    assertions: tuple[Assertion, ...] = ()
    stdin: str | None = None
    timeout: float = 5.0
    # When True, run setup + assertions inside a redirect_stdout/stderr
    # so the student module's top-level prints (or constructor noise)
    # don't leak into the sandbox stdout. The final 'OK' is emitted
    # after the redirect ends, preserving the success contract.
    quiet: bool = False

    @property
    def name(self) -> str:
        return self.label

    def _build_code(self) -> str:
        body_lines: list[str] = []
        if self.setup:
            body_lines.append(self.setup.rstrip("\n"))
        for assertion in self.assertions:
            body_lines.append(assertion.to_code().rstrip("\n"))
        body = "\n".join(body_lines)

        if self.quiet:
            indented = "\n".join(
                "    " + ln if ln else "    pass"
                for ln in body.split("\n")
            ) or "    pass"
            return (
                "import sys, io\n"
                "from contextlib import redirect_stdout, redirect_stderr\n"
                "sys.path.insert(0, '.')\n"
                "with redirect_stdout(io.StringIO()), "
                "redirect_stderr(io.StringIO()):\n"
                f"{indented}\n"
                "print('OK')\n"
            )
        return (
            "import sys\n"
            "sys.path.insert(0, '.')\n"
            + (body + "\n" if body else "")
            + "print('OK')\n"
        )

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        result = run_in_sandbox(
            exercise, exercise_dir, self._build_code(),
            stdin=self.stdin, timeout=self.timeout,
        )
        return evaluate_subprocess(
            self.name, result, expected_stdout=_SUCCESS
        )
