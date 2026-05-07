# 🤝 Contributing to pythonette

This guide explains how the test framework is organized and how to add
or modify checks. It assumes you've already cloned the repo and run the
installer.

## Project layout

```
pythonette/
├── checks/            # the typed Check primitives
│   ├── base.py        # Check ABC, sandbox runner, result evaluator
│   ├── static.py      # AST/text-only checks (no student code runs)
│   ├── ast_checks.py  # richer AST checks
│   ├── runtime.py     # checks that exec student code in a subprocess
│   ├── declarative.py # AssertCheck + the typed Assertion DSL
│   └── scripted.py    # RunCheck — runpy a student file with argv/stdin
├── checkers/style.py  # flake8 + mypy invocation
├── subjects/          # one file per module
│   ├── registry.py    # Exercise + Module dataclasses + Registry
│   ├── module_00.py … module_06.py
│   └── __init__.py    # registers every module
├── detector.py        # filename → Exercise lookup
├── runner.py          # orchestrates style + checks per detected file
└── printer.py         # rich-formatted output
```

To add coverage you only ever touch files under `pythonette/subjects/`
(and occasionally `pythonette/checks/` to extend the DSL). The runner,
detector and printer are stable.

## The data model

```python
Module(id, title, exercises=(Exercise, …))
Exercise(
    module_id, id,
    filenames=(...),         # what the detector matches
    checks=(Check, …),       # ordered, every check runs
    authorized=(...),        # display only — actual enforcement is in AuthorizedCheck
    explain="...",           # printed with --explain
    support_paths=(...),     # extra files/dirs to copy into the sandbox (optional)
    mypy_skip=(...),         # filenames to skip mypy on (optional)
)
```

A `Check` produces a `CheckResult(name, ok, reason)`. Style tools
(flake8, mypy) run automatically on every `*.py` file in the exercise;
you never wire them yourself.

## The check toolbox

The framework has four layers. **Always reach for the highest layer
that fits.** Hand-written code in test definitions is a smell —
prefer typed primitives so the intent stays readable.

### 1. Static checks (no student code runs)

Use these whenever the property is structural.

| Check | What it asserts |
|---|---|
| `StructureCheck` | top-level functions/classes, optional `__main__` guard, allowed top-level statements |
| `AuthorizedCheck` | only specified bare-name calls appear (`print`, `len`, …); set `allow_method_calls=False` to also forbid `.foo()` |
| `ImportCheck` | only specified modules may be imported |
| `TopLevelFunctionsCheck` | named top-level functions are defined |
| `ClassMethodsCheck` | for each class, the listed methods are present |
| `ClassNamePresenceCheck` | at least one class name (case-insensitive) contains each substring — for "must define a CSV class and a JSON class" |
| `RequireNodeTypesCheck` / `NoNodeTypesCheck` | require / forbid AST node types (`Try`, `With`, `ListComp`, `DictComp`, …), optionally scoped to a function body |
| `ImportStyleCheck` | require absolute and/or relative imports in a file |
| `NoForbiddenCallsCheck` | forbid bare-name calls (`eval`, `exec`, `input`, …) |
| `NoSysPathMutationCheck` | reject `sys.path.append/insert/...` |
| `FilesExistCheck` | required project files exist on disk |
| `FunctionTryHandlersCheck`, `FunctionTryFinallyReturnCheck` | shape of try/except inside a named function |

### 2. Runtime checks (the sandbox)

Each runtime check copies the student files into a temp dir and runs a
generated harness as a subprocess. The harness must print `OK` on
success.

| Check | When to use |
|---|---|
| `SignatureCheck` | inspect a top-level function's signature: param names, defaults, annotations, return annotation |
| `MethodSignatureCheck` | same for a method on a class |
| `MethodArityCheck` | count required parameters after `self` (extras with defaults are tolerated) |
| `CallCheck` | import a function and call it with optional `stdin`, asserting on stdout |
| `ScriptCheck` | run a file as `__main__` via `runpy`, assert substrings in stdout |
| `RunCheck` | richer than `ScriptCheck`: `argv`, `stdin`, fixtures, separate stdout/stderr/combined assertions, optional `post_assertions` after the run |
| `OfficialMainCheck` | drive the subject-provided `pythonette/subjects/main.py` helper with a menu choice |
| `InlineCheck` | escape hatch — runs an arbitrary code snippet. **Avoid:** prefer `AssertCheck` |

### 3. Declarative assertions (`AssertCheck` + `Assertion`s)

`AssertCheck` is the preferred way to express runtime invariants. Its
`setup` typically holds a single `from x import Y` line; the body is a
tuple of typed `Assertion`s. The framework adds the sandbox prelude
(`sys.path.insert(0, '.')`, error reporting, the trailing `print('OK')`)
so test authors never write boilerplate.

```python
AssertCheck(
    label="gen_player_achievements() returns a set",
    setup="from ft_achievement_tracker import gen_player_achievements",
    assertions=(IsInstance("gen_player_achievements()", "set"),),
)
```

Available assertions (in `pythonette.checks.declarative`):

| Assertion | Code emitted (conceptually) |
|---|---|
| `Eq(expr, value)` | `assert (expr) == value` |
| `Contains(expr, substring)` | `assert substring in (expr)` |
| `ContainsAll(expr, (s1, s2, …))` | each substring in `expr` |
| `Truthy(expr)` / `Falsy(expr)` | `assert (expr)` / `assert not (expr)` |
| `Is(a, b)` / `IsNot(a, b)` | identity comparison |
| `IsInstance(expr, "type")` | `isinstance(...)` against a *string* type expression |
| `HasAttr(obj, attr)` / `LacksAttr(obj, attr)` | `hasattr` / `not hasattr` |
| `Subclass(child, parent)` | `issubclass(...)` |
| `Raises(stmt, exception_types=(...))` | wraps `stmt` in try/except and asserts it raised |
| `NotRaises(stmt, exception_types=(...))` | `stmt` must succeed cleanly |
| `Prints(stmt, contains=(…), case_insensitive=…)` | runs `stmt` under captured stdout, asserts substrings |
| `HasStaticMethod(class_)` / `HasClassMethod(class_, callable_no_args=…)` | class introspection without `inspect.getattr_static` boilerplate |
| `HasNestedClass(class_)` | requires a nested class (any name) |
| `FileWritten(path, contains=(…), line_suffix=…)` | a file at `path` exists, optionally with content/line-suffix constraints |
| `Exec(code)` | escape hatch — paste a multi-line snippet verbatim. Use only when no typed assertion fits |

If an assertion you need is missing, **add it to `declarative.py`** rather
than embedding raw code in `setup=`. Six lines of new dataclass beats
six lines of boilerplate replicated across every test that needs the
pattern.

### 4. Scripted (`RunCheck`)

For exercises whose contract is "run as `__main__` with these args, this
stdin, these fixtures, and assert on output":

```python
RunCheck(
    label="filename provided: file is created with '#'-suffixed lines",
    file="ft_archive_creation.py",
    argv=("ft_archive_creation.py", "ancient_fragment.txt"),
    stdin="new_fragment.txt\n",
    fixtures=(("ancient_fragment.txt", _FRAGMENT_CONTENT),),
    stdout_contains=("new_fragment.txt",),
    post_assertions=(FileWritten("new_fragment.txt", line_suffix="#"),),
)
```

Use `combined_contains=` when assertions don't care about
stdout-vs-stderr; use `allow_exception=True` when the script is expected
to crash (e.g. demonstrating an `ImportError`).

## Adding an exercise

```python
# pythonette/subjects/module_03.py

_EX_FILE = "ft_my_exercise.py"

_MY_EX = Exercise(
    module_id="03", id="ex_new",
    filenames=(_EX_FILE,),
    authorized=("len", "print"),         # display only
    checks=(
        StructureCheck(
            file=_EX_FILE,
            functions=("my_func",),
            allow_imports=True,
            allow_main_guard=True,
        ),
        ImportCheck(_EX_FILE, ("sys",)),
        AuthorizedCheck(_EX_FILE, ("len", "print")),
        AssertCheck(
            label="my_func() returns a list of strings",
            setup="from ft_my_exercise import my_func",
            assertions=(
                IsInstance("my_func()", "list"),
                Truthy("all(isinstance(x, str) for x in my_func())"),
            ),
        ),
        ScriptCheck(
            label="script prints the banner",
            file=_EX_FILE,
            expected_contains=("=== My Exercise ===",),
        ),
    ),
    explain="Define my_func(): returns a list of strings; the script prints …",
)

# Register in the module's tuple:
MODULE_03 = Module(
    id="03",
    title="Data Quest — mastering Python collections",
    exercises=(_EX0, _EX1, _EX2, _EX3, _EX4, _EX5, _EX6, _MY_EX),
)
```

The detector picks up the new file automatically because it matches on
`Exercise.filenames`.

## Adding a module

1. Create `pythonette/subjects/module_NN.py` exporting `MODULE_NN`.
2. Register it in `pythonette/subjects/__init__.py`:
   ```python
   from pythonette.subjects.module_NN import MODULE_NN
   ALL_MODULES = [..., MODULE_NN]
   ```
3. Filenames must be globally unique across modules — the registry
   raises on collision.

## Style guide for tests

- **One concept per check.** A label like "valid input: tuple + distance
  to center" is fine; "everything works" is not. Failure messages are
  the docs students read.
- **Prefer typed primitives.** If you find yourself writing
  `setup="import inspect\n..."` or hand-rolled f-string assertions
  inside `Exec`, add a typed assertion instead.
- **Avoid `InlineCheck` and `Exec`** unless no typed primitive fits.
  Both are escape hatches and bypass the declarative guarantees.
- **Sandbox awareness.** The sandbox copies `Exercise.filenames` and
  `support_paths` into a temp dir, then runs `_pythonette_harness.py`
  there. The student's working directory is never touched.
- **Order matters.** Static checks are cheapest and most informative on
  failure (they don't need the code to run). Put them first.

## Running locally

```sh
# from the pythonette-42 repo
pip install -e .

# point pythonette at any directory
pythonette path/to/some/student/repo
pythonette -m 03 -e ex3 -v   # narrow scope, verbose output
```

`-v` is useful while developing checks: it dumps the full stderr from
failing sandbox runs so you can see the generated harness traceback.

## When something breaks

- **`SyntaxError: f-string: ...`** in a generated harness on Python <
  3.12: a check is emitting nested same-quote f-strings. Replace the
  f-string interpolation with plain string concatenation. See the
  `IsInstance` / `SignatureCheck` fixes (commit `9654dde`) for
  examples.
- **Mypy is slow.** It caches at `~/.cache/pythonette/mypy/` (or
  `$XDG_CACHE_HOME/pythonette/mypy/`). Deleting the cache forces a cold
  re-check; warm runs are ~10× faster.
- **A check is flaky.** Almost always: the student exercise involves
  randomness or timing, and the check is asserting an implementation
  detail. Tighten the assertion to the contract, not the output shape.

## Reporting issues

Open an issue on GitHub with:
- the exercise (module + ex id),
- the student file that triggered it (or a minimal reproducer),
- the failing check name and the `-v` output.

False positives and false negatives are both bugs in the framework.
