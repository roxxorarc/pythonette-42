from __future__ import annotations

from dataclasses import dataclass, field
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


def _module_from_file(file: str) -> str:
    return file[:-3] if file.endswith(".py") else file


@dataclass(frozen=True)
class SignatureCheck(Check):
    """Check signature of a top-level function in a module."""

    module: str
    function: str
    expected_params: tuple[str, ...] = ()
    allow_defaults: bool = False
    require_callable_no_args: bool = False
    param_annotations: dict[str, str] | None = None
    return_annotation: str | None = None
    label: str | None = None

    @property
    def name(self) -> str:
        if self.label:
            return self.label
        if self.expected_params:
            return (
                f"signature: {self.function}"
                f"({', '.join(self.expected_params)})"
            )
        if self.require_callable_no_args:
            return (
                f"signature: {self.function}() callable with no arguments"
            )
        return f"signature: {self.function}() takes no arguments"

    def _build_code(self) -> str:
        lines = [
            "import inspect, sys\n",
            "sys.path.insert(0, '.')\n",
            f"from {self.module} import {self.function}\n",
            f"sig = inspect.signature({self.function})\n",
            "got = list(sig.parameters)\n",
        ]
        fn = self.function
        if self.expected_params:
            lines.append(
                f"expected = {list(self.expected_params)!r}\n"
                "assert got == expected, (\n"
                f"    f'{fn}() params: got={{got!r}} expected={{expected!r}}'\n"
                ")\n"
            )
        elif not self.require_callable_no_args:
            lines.append(
                "assert got == [], (\n"
                f"    f'{fn}() must take no parameters, got {{got!r}}'\n"
                ")\n"
            )
        if self.require_callable_no_args:
            lines.append(
                "for p in sig.parameters.values():\n"
                "    assert p.default is not inspect.Parameter.empty, (\n"
                f"        f'{fn}(): param {{p.name!r}} needs a default'\n"
                "    )\n"
            )
        elif not self.allow_defaults:
            lines.append(
                "for p in sig.parameters.values():\n"
                "    assert p.default is inspect.Parameter.empty, (\n"
                f"        f'{fn}(): param {{p.name!r}} must have no default'\n"
                "    )\n"
            )
        if self.param_annotations:
            for pname, annot in self.param_annotations.items():
                lines.append(
                    f"assert sig.parameters[{pname!r}].annotation is "
                    f"{annot}, (\n"
                    f"    f'{fn}({pname}): annotation must be "
                    f"{annot}, got '\n"
                    f"    f'{{sig.parameters[{pname!r}].annotation!r}}'\n"
                    ")\n"
                )
        if self.return_annotation is not None:
            ann = self.return_annotation
            if ann == "None":
                lines.append(
                    "assert sig.return_annotation is None, (\n"
                    f"    f'{fn}(): return must be None, got '\n"
                    "    f'{sig.return_annotation!r}'\n"
                    ")\n"
                )
            else:
                lines.append(
                    f"assert sig.return_annotation is {ann}, (\n"
                    f"    f'{fn}(): return must be {ann}, got '\n"
                    "    f'{sig.return_annotation!r}'\n"
                    ")\n"
                )
        lines.append("print('OK')\n")
        return "".join(lines)

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        result = run_in_sandbox(
            exercise, exercise_dir, self._build_code()
        )
        return evaluate_subprocess(
            self.name, result, expected_stdout=_SUCCESS
        )


@dataclass(frozen=True)
class MethodSignatureCheck(Check):
    """Check signature of a method on a class."""

    module: str
    class_name: str
    method: str
    expected_params: tuple[str, ...]
    allow_defaults: bool = False
    label: str | None = None

    @property
    def name(self) -> str:
        if self.label:
            return self.label
        return (
            f"signature: {self.class_name}.{self.method}"
            f"({', '.join(self.expected_params)})"
        )

    def _build_code(self) -> str:
        target = f"{self.class_name}.{self.method}"
        code = (
            "import inspect, sys\n"
            "sys.path.insert(0, '.')\n"
            f"from {self.module} import {self.class_name}\n"
            f"method = getattr({self.class_name}, {self.method!r})\n"
            "sig = inspect.signature(method)\n"
            "got = list(sig.parameters)\n"
            f"expected = {list(self.expected_params)!r}\n"
            "assert got == expected, (\n"
            f"    f'{target}: got={{got!r}} expected={{expected!r}}'\n"
            ")\n"
        )
        if not self.allow_defaults:
            code += (
                "for p in sig.parameters.values():\n"
                "    assert p.default is inspect.Parameter.empty, (\n"
                f"        f'{target}: param {{p.name!r}} must have no default'\n"
                "    )\n"
            )
        code += "print('OK')\n"
        return code

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        result = run_in_sandbox(
            exercise, exercise_dir, self._build_code()
        )
        return evaluate_subprocess(
            self.name, result, expected_stdout=_SUCCESS
        )


@dataclass(frozen=True)
class MethodArityCheck(Check):
    """Check that a method is callable with N args after self.

    Extra parameters are allowed if they have defaults. Use this when the
    spec dictates only the method name and call shape, not parameter names.
    """

    module: str
    class_name: str
    method: str
    n_required_after_self: int
    label: str | None = None

    @property
    def name(self) -> str:
        if self.label:
            return self.label
        if self.n_required_after_self == 0:
            shape = "()"
        else:
            shape = "(" + ", ".join(
                f"arg{i + 1}" for i in range(self.n_required_after_self)
            ) + ")"
        return (
            f"signature: {self.class_name}.{self.method}{shape} "
            f"callable (extras with defaults ok)"
        )

    def _build_code(self) -> str:
        target = f"{self.class_name}.{self.method}"
        return (
            "import inspect, sys\n"
            "sys.path.insert(0, '.')\n"
            f"from {self.module} import {self.class_name}\n"
            f"m = getattr({self.class_name}, {self.method!r}, None)\n"
            f"assert m is not None, '{target} missing'\n"
            "params = list(inspect.signature(m).parameters.values())\n"
            "assert params and params[0].name == 'self', (\n"
            f"    '{target}: first parameter must be self'\n"
            ")\n"
            "required = [\n"
            "    p for p in params[1:]\n"
            "    if p.default is inspect.Parameter.empty\n"
            "    and p.kind not in (\n"
            "        inspect.Parameter.VAR_POSITIONAL,\n"
            "        inspect.Parameter.VAR_KEYWORD,\n"
            "    )\n"
            "]\n"
            f"want = {self.n_required_after_self}\n"
            "assert len(required) == want, (\n"
            f"    f'{target}: must accept {{want}} arg(s) after self — '\n"
            "    f'required: {[p.name for p in required]!r}'\n"
            ")\n"
            "print('OK')\n"
        )

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        result = run_in_sandbox(
            exercise, exercise_dir, self._build_code()
        )
        return evaluate_subprocess(
            self.name, result, expected_stdout=_SUCCESS
        )


@dataclass(frozen=True)
class CallCheck(Check):
    """Import a function from the student file and call it.

    Optionally feeds stdin. Verifies stdout (exact match or substrings).
    Set forbid_input=True to assert that input() is never called.
    """

    label: str
    module: str
    function: str
    args_repr: str = "()"
    stdin: str | None = None
    expected_stdout: str | None = None
    expected_contains: tuple[str, ...] = ()
    forbid_input: bool = False
    timeout: float = 5.0

    @property
    def name(self) -> str:
        return self.label

    def _build_code(self) -> str:
        prelude = ""
        if self.forbid_input:
            prelude = (
                "import builtins\n"
                "def _fail_input(*_a, **_kw):\n"
                "    raise AssertionError('input() must not be called')\n"
                "builtins.input = _fail_input\n"
            )
        return (
            "import sys\n"
            "sys.path.insert(0, '.')\n"
            + prelude +
            f"from {self.module} import *  # noqa: F401,F403\n"
            f"{self.function}{self.args_repr}\n"
        )

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        result = run_in_sandbox(
            exercise, exercise_dir, self._build_code(),
            stdin=self.stdin, timeout=self.timeout,
        )
        return evaluate_subprocess(
            self.name, result,
            expected_stdout=self.expected_stdout,
            expected_contains=self.expected_contains,
        )


@dataclass(frozen=True)
class ScriptCheck(Check):
    """Run the student file as __main__ via runpy."""

    label: str
    file: str
    stdin: str | None = None
    expected_contains: tuple[str, ...] = ()
    expected_stdout: str | None = None
    timeout: float = 5.0

    @property
    def name(self) -> str:
        return self.label

    def _build_code(self) -> str:
        return (
            "import runpy, sys\n"
            "sys.path.insert(0, '.')\n"
            f"runpy.run_path({self.file!r}, run_name='__main__')\n"
        )

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        result = run_in_sandbox(
            exercise, exercise_dir, self._build_code(),
            stdin=self.stdin, timeout=self.timeout,
        )
        return evaluate_subprocess(
            self.name, result,
            expected_stdout=self.expected_stdout,
            expected_contains=self.expected_contains,
        )


@dataclass(frozen=True)
class InlineCheck(Check):
    """Escape hatch: run an arbitrary code snippet in the sandbox.

    Use this for assertions that don't fit the typed checks
    (subclassing, hasattr, custom comparisons, …). The snippet must
    print 'OK' on success.
    """

    label: str
    code: str
    stdin: str | None = None
    timeout: float = 5.0

    @property
    def name(self) -> str:
        return self.label

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        result = run_in_sandbox(
            exercise, exercise_dir, self.code,
            stdin=self.stdin, timeout=self.timeout,
        )
        return evaluate_subprocess(
            self.name, result, expected_stdout=_SUCCESS
        )


@dataclass(frozen=True)
class OfficialMainCheck(Check):
    """Run the subject-provided main.py helper with a given choice."""

    choice: str
    inputs: tuple[str, ...] = ()
    expected_pieces: tuple[str, ...] = ()
    label: str = "official main.py helper runs cleanly"

    @property
    def name(self) -> str:
        return self.label

    def _build_code(self) -> str:
        feed = (self.choice,) + self.inputs
        contains_lit = list(self.expected_pieces)
        return (
            "import builtins\n"
            "import io\n"
            "import sys\n"
            "from contextlib import redirect_stdout\n"
            "from pathlib import Path\n"
            "import pythonette.subjects\n"
            "sys.path.insert(0, '.')\n"
            "helper = (\n"
            "    Path(pythonette.subjects.__file__).parent / 'main.py'\n"
            ")\n"
            f"_inputs = iter({list(feed)!r})\n"
            "def _input(prompt=''):\n"
            "    sys.stdout.write(prompt)\n"
            "    try:\n"
            "        return next(_inputs)\n"
            "    except StopIteration:\n"
            "        raise AssertionError(\n"
            "            f'helper asked for unexpected extra input '\n"
            "            f'(prompt={prompt!r})'\n"
            "        )\n"
            "builtins.input = _input\n"
            "src = helper.read_text(encoding='utf-8')\n"
            "stream = io.StringIO()\n"
            "with redirect_stdout(stream):\n"
            "    exec(\n"
            "        compile(src, str(helper), 'exec'),\n"
            "        {'__name__': '__main__'},\n"
            "    )\n"
            "out = stream.getvalue()\n"
            "assert '\\u274c' not in out, (\n"
            "    f'official helper reported an error:\\n{out}'\n"
            ")\n"
            f"for piece in {contains_lit!r}:\n"
            "    assert piece in out, (\n"
            "        f'helper output missing {piece!r}:\\n{out}'\n"
            "    )\n"
            "print('OK')\n"
        )

    def run(
        self, exercise_dir: Path, exercise: "Exercise"
    ) -> CheckResult:
        result = run_in_sandbox(
            exercise, exercise_dir, self._build_code()
        )
        return evaluate_subprocess(
            self.name, result, expected_stdout=_SUCCESS
        )
