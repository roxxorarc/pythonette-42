from pythonette.checks import (
    AuthorizedCheck,
    InlineCheck,
)
from pythonette.subjects.registry import Exercise, Module


_FRAGMENT_NAME = "ancient_fragment.txt"
_FRAGMENT_CONTENT = (
    "[FRAGMENT 001] Digital preservation protocols established 2087\n"
    "[FRAGMENT 002] Knowledge must survive the entropy wars\n"
    "[FRAGMENT 003] Every byte saved is a victory against oblivion\n"
)


def _required_functions(file: str, functions: tuple[str, ...]) -> InlineCheck:
    """Lighter-weight than StructureCheck: only assert that the named
    functions exist as top-level defs. Module-04 scripts may freely use
    top-level statements (including a bare `main()` call) — that is
    standard 42 style and not forbidden by the subject."""
    names = list(functions)
    return InlineCheck(
        label=f"{file}: top-level function(s) defined: {', '.join(names)}",
        code=(
            "import ast\n"
            "from pathlib import Path\n"
            f"src = Path({file!r}).read_text(encoding='utf-8')\n"
            f"tree = ast.parse(src, filename={file!r})\n"
            "FN = (ast.FunctionDef, ast.AsyncFunctionDef)\n"
            "defs = [n.name for n in tree.body if isinstance(n, FN)]\n"
            f"missing = [n for n in {names!r} if n not in defs]\n"
            "assert not missing, (\n"
            "    f'missing top-level function(s) {missing!r} '\n"
            "    f'(found: {defs!r})'\n"
            ")\n"
            "print('OK')\n"
        ),
    )


def _no_with_check(file: str) -> InlineCheck:
    """Subject: 'with' statement is introduced in ex3 only."""
    return InlineCheck(
        label="no use of 'with' statement before exercise 3",
        code=(
            "import ast\n"
            "from pathlib import Path\n"
            f"src = Path({file!r}).read_text(encoding='utf-8')\n"
            f"tree = ast.parse(src, filename={file!r})\n"
            "bad = [n for n in ast.walk(tree)\n"
            "       if isinstance(n, (ast.With, ast.AsyncWith))]\n"
            "assert not bad, (\n"
            "    f'with statement is introduced in exercise 3 only — '\n"
            "    f'found at line {bad[0].lineno}'\n"
            ")\n"
            "print('OK')\n"
        ),
    )


def _runpy_check(
    label: str,
    file: str,
    *,
    argv: tuple[str, ...],
    stdin: str | None = None,
    stdout_contains: tuple[str, ...] = (),
    stderr_contains: tuple[str, ...] = (),
    fixtures: tuple[tuple[str, str], ...] = (),
    after: str = "",
    timeout: float = 5.0,
) -> InlineCheck:
    """Run `file` as __main__ via runpy with a controlled argv/stdin and
    capture stdout AND stderr separately so tests can assert routing."""
    code = (
        "import runpy, sys, io\n"
        "from contextlib import redirect_stdout, redirect_stderr\n"
        "sys.path.insert(0, '.')\n"
    )
    for fname, content in fixtures:
        code += (
            f"open({fname!r}, 'w', encoding='utf-8').write({content!r})\n"
        )
    code += (
        f"sys.argv = {list(argv)!r}\n"
    )
    if stdin is not None:
        code += f"sys.stdin = io.StringIO({stdin!r})\n"
    code += (
        "out = io.StringIO()\n"
        "err = io.StringIO()\n"
        "try:\n"
        "    with redirect_stdout(out), redirect_stderr(err):\n"
        f"        runpy.run_path({file!r}, run_name='__main__')\n"
        "except SystemExit:\n"
        "    pass\n"
        "stdout = out.getvalue()\n"
        "stderr = err.getvalue()\n"
    )
    for needle in stdout_contains:
        code += (
            f"assert {needle!r} in stdout, (\n"
            f"    'missing in stdout: ' + {needle!r}\n"
            "    + '\\n--- stdout ---\\n' + stdout\n"
            "    + '\\n--- stderr ---\\n' + stderr\n"
            ")\n"
        )
    for needle in stderr_contains:
        code += (
            f"assert {needle!r} in stderr, (\n"
            f"    'missing in stderr: ' + {needle!r}\n"
            "    + '\\n--- stdout ---\\n' + stdout\n"
            "    + '\\n--- stderr ---\\n' + stderr\n"
            ")\n"
        )
    code += after
    code += "print('OK')\n"
    return InlineCheck(label=label, code=code, timeout=timeout)


# ---------------------------------------------------------------------------
# Exercise 0: ft_ancient_text
# ---------------------------------------------------------------------------

_EX0_FILE = "ft_ancient_text.py"
_EX0_AUTHORIZED = ("open", "len", "print")
_EX0_FIXTURES = ((_FRAGMENT_NAME, _FRAGMENT_CONTENT),)

_EX0 = Exercise(
    module_id="04", id="ex0",
    filenames=(_EX0_FILE,),
    authorized=_EX0_AUTHORIZED,
    checks=(
        AuthorizedCheck(
            _EX0_FILE, _EX0_AUTHORIZED, allow_method_calls=True,
        ),
        _no_with_check(_EX0_FILE),
        _runpy_check(
            "no args: usage message printed",
            _EX0_FILE,
            argv=(_EX0_FILE,),
            stdout_contains=("Usage",),
        ),
        _runpy_check(
            "missing file: error reported (not a crash)",
            _EX0_FILE,
            argv=(_EX0_FILE, "definitely_not_a_real_file_xyz.txt"),
            stdout_contains=("Error",),
        ),
        _runpy_check(
            "valid file: header, content and close message",
            _EX0_FILE,
            argv=(_EX0_FILE, _FRAGMENT_NAME),
            fixtures=_EX0_FIXTURES,
            stdout_contains=(
                "=== Cyber Archives Recovery ===",
                f"Accessing file '{_FRAGMENT_NAME}'",
                "[FRAGMENT 001] Digital preservation protocols established 2087",
                "[FRAGMENT 002] Knowledge must survive the entropy wars",
                "[FRAGMENT 003] Every byte saved is a victory against oblivion",
                f"File '{_FRAGMENT_NAME}' closed.",
            ),
        ),
    ),
    explain=(
        "Read sys.argv[1] as a filename, print a banner, then open/read/"
        "print/close the file content (cat-style with separators). On no "
        "argument print a Usage line; on missing/inaccessible file print "
        "an Error message instead of crashing."
    ),
)


# ---------------------------------------------------------------------------
# Exercise 1: ft_archive_creation
# ---------------------------------------------------------------------------

_EX1_FILE = "ft_archive_creation.py"
_EX1_AUTHORIZED = ("open", "len", "print", "input")
_EX1_FIXTURES = ((_FRAGMENT_NAME, _FRAGMENT_CONTENT),)

_EX1 = Exercise(
    module_id="04", id="ex1",
    filenames=(_EX1_FILE,),
    authorized=_EX1_AUTHORIZED,
    checks=(
        AuthorizedCheck(
            _EX1_FILE, _EX1_AUTHORIZED, allow_method_calls=True,
        ),
        _no_with_check(_EX1_FILE),
        _runpy_check(
            "empty filename input: 'Not saving' message",
            _EX1_FILE,
            argv=(_EX1_FILE, _FRAGMENT_NAME),
            stdin="\n",
            fixtures=_EX1_FIXTURES,
            stdout_contains=(
                "=== Cyber Archives Recovery & Preservation ===",
                "[FRAGMENT 001] Digital preservation protocols established 2087",
                "Not saving",
            ),
        ),
        _runpy_check(
            "transformed lines all end with '#'",
            _EX1_FILE,
            argv=(_EX1_FILE, _FRAGMENT_NAME),
            stdin="\n",
            fixtures=_EX1_FIXTURES,
            stdout_contains=(
                "[FRAGMENT 001] Digital preservation protocols established 2087#",
                "[FRAGMENT 002] Knowledge must survive the entropy wars#",
                "[FRAGMENT 003] Every byte saved is a victory against oblivion#",
            ),
        ),
        _runpy_check(
            "filename provided: file is created with '#'-suffixed lines",
            _EX1_FILE,
            argv=(_EX1_FILE, _FRAGMENT_NAME),
            stdin="new_fragment.txt\n",
            fixtures=_EX1_FIXTURES,
            stdout_contains=("new_fragment.txt",),
            after=(
                "import os\n"
                "assert os.path.isfile('new_fragment.txt'), (\n"
                "    'expected new_fragment.txt to be written'\n"
                ")\n"
                "saved = open('new_fragment.txt', encoding='utf-8').read()\n"
                "lines = [ln for ln in saved.splitlines() if ln]\n"
                "assert lines and all(ln.endswith('#') for ln in lines), (\n"
                "    'saved file must have every line ending with #, got:\\n'\n"
                "    + saved\n"
                ")\n"
            ),
        ),
    ),
    explain=(
        "Reuse ft_ancient_text. After printing the original content, "
        "append '#' at the end of each line, print the transform, then "
        "ask for a destination filename via input(): empty -> skip save; "
        "otherwise create/replace that file with the transformed content."
    ),
)


# ---------------------------------------------------------------------------
# Exercise 2: ft_stream_management
# ---------------------------------------------------------------------------

_EX2_FILE = "ft_stream_management.py"
# input() is forbidden in ex2 — use sys.stdin.readline() instead.
_EX2_AUTHORIZED = ("open", "len", "print")


def _no_input_check(file: str) -> InlineCheck:
    return InlineCheck(
        label="ex2: input() is forbidden — use sys.stdin instead",
        code=(
            "import ast\n"
            "from pathlib import Path\n"
            f"src = Path({file!r}).read_text(encoding='utf-8')\n"
            f"tree = ast.parse(src, filename={file!r})\n"
            "bad = []\n"
            "for n in ast.walk(tree):\n"
            "    if (\n"
            "        isinstance(n, ast.Call)\n"
            "        and isinstance(n.func, ast.Name)\n"
            "        and n.func.id == 'input'\n"
            "    ):\n"
            "        bad.append(n.lineno)\n"
            "assert not bad, (\n"
            "    f'input() must not be called (use sys.stdin.readline()) '\n"
            "    f'— found at line(s) {bad!r}'\n"
            ")\n"
            "print('OK')\n"
        ),
    )


_EX2 = Exercise(
    module_id="04", id="ex2",
    filenames=(_EX2_FILE,),
    authorized=_EX2_AUTHORIZED,
    checks=(
        AuthorizedCheck(
            _EX2_FILE, _EX2_AUTHORIZED, allow_method_calls=True,
        ),
        _no_with_check(_EX2_FILE),
        _no_input_check(_EX2_FILE),
        _runpy_check(
            "missing input file: '[STDERR]' prefix routed to stderr",
            _EX2_FILE,
            argv=(_EX2_FILE, "definitely_not_a_real_file_xyz.txt"),
            stdin="\n",
            stdout_contains=("=== Cyber Archives Recovery & Preservation ===",),
            stderr_contains=("[STDERR]",),
        ),
        _runpy_check(
            "valid file then empty filename: read flow on stdout",
            _EX2_FILE,
            argv=(_EX2_FILE, _FRAGMENT_NAME),
            stdin="\n",
            fixtures=((_FRAGMENT_NAME, _FRAGMENT_CONTENT),),
            stdout_contains=(
                "=== Cyber Archives Recovery & Preservation ===",
                "[FRAGMENT 001] Digital preservation protocols established 2087",
                "[FRAGMENT 003] Every byte saved is a victory against oblivion#",
            ),
        ),
        _runpy_check(
            "save to inaccessible path: error routed to stderr with prefix",
            _EX2_FILE,
            argv=(_EX2_FILE, _FRAGMENT_NAME),
            stdin="/root/forbidden_archive.txt\n",
            fixtures=((_FRAGMENT_NAME, _FRAGMENT_CONTENT),),
            stderr_contains=("[STDERR]",),
        ),
    ),
    explain=(
        "Same flow as ex1 but read user input via sys.stdin.readline() "
        "(input() is forbidden) and route every exception message to "
        "sys.stderr prefixed with '[STDERR]' instead of stdout."
    ),
)


# ---------------------------------------------------------------------------
# Exercise 3: ft_vault_security
# ---------------------------------------------------------------------------

_EX3_FILE = "ft_vault_security.py"
# Subject: open(), read(), write(), print(). We add common helpers to keep
# the AST-level check tight without rejecting reasonable error formatting.
_EX3_AUTHORIZED = ("open", "print", "len", "isinstance", "str", "tuple")


def _with_required_check(file: str) -> InlineCheck:
    return InlineCheck(
        label="ex3 must use the 'with' context manager",
        code=(
            "import ast\n"
            "from pathlib import Path\n"
            f"src = Path({file!r}).read_text(encoding='utf-8')\n"
            f"tree = ast.parse(src, filename={file!r})\n"
            "good = any(\n"
            "    isinstance(n, (ast.With, ast.AsyncWith))\n"
            "    for n in ast.walk(tree)\n"
            ")\n"
            "assert good, (\n"
            "    'ex3 must use a with statement to manage file handles'\n"
            ")\n"
            "print('OK')\n"
        ),
    )


_EX3_CONTRACT_CODE = (
    "import sys, os, io\n"
    "from contextlib import redirect_stdout, redirect_stderr\n"
    "sys.path.insert(0, '.')\n"
    f"open({_FRAGMENT_NAME!r}, 'w', encoding='utf-8').write("
    f"{_FRAGMENT_CONTENT!r})\n"
    "# Importing the script may run a top-level demo; mute it so we can\n"
    "# enforce the exact 'OK' stdout contract for this check.\n"
    "with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):\n"
    "    from ft_vault_security import secure_archive\n"
    "# 1. read existing\n"
    f"ok = secure_archive({_FRAGMENT_NAME!r})\n"
    "assert isinstance(ok, tuple) and len(ok) == 2, (\n"
    "    f'secure_archive must return a (bool, str) tuple, got {ok!r}'\n"
    ")\n"
    "assert isinstance(ok[0], bool) and isinstance(ok[1], str), (\n"
    "    f'tuple must be (bool, str), got types '\n"
    "    f'({type(ok[0]).__name__}, {type(ok[1]).__name__})'\n"
    ")\n"
    "assert ok[0] is True, (\n"
    "    f'reading an existing file must return True, got {ok!r}'\n"
    ")\n"
    "assert '[FRAGMENT 001]' in ok[1], (\n"
    "    f'returned content must include the file body, got {ok!r}'\n"
    ")\n"
    "# 2. read missing\n"
    "miss = secure_archive('/not/existing/file/xyz')\n"
    "assert isinstance(miss, tuple) and len(miss) == 2, miss\n"
    "assert miss[0] is False, (\n"
    "    f'missing file must return False, got {miss!r}'\n"
    ")\n"
    "assert isinstance(miss[1], str) and miss[1], (\n"
    "    f'missing file must return a non-empty error message, got {miss!r}'\n"
    ")\n"
    "# 3. write\n"
    "out = '_vault_security_test_output.txt'\n"
    "if os.path.exists(out):\n"
    "    os.remove(out)\n"
    "try:\n"
    "    wrote = secure_archive(out, 'write', 'vault payload')\n"
    "except TypeError:\n"
    "    # Allow int 'mode' instead of str — try a few common conventions.\n"
    "    wrote = None\n"
    "    for mode in (1, 2, 'w'):\n"
    "        try:\n"
    "            wrote = secure_archive(out, mode, 'vault payload')\n"
    "            break\n"
    "        except TypeError:\n"
    "            continue\n"
    "    assert wrote is not None, (\n"
    "        'secure_archive must accept an action argument and a content '\n"
    "        'argument for writing'\n"
    "    )\n"
    "assert isinstance(wrote, tuple) and len(wrote) == 2, wrote\n"
    "assert wrote[0] is True, (\n"
    "    f'writing must return True on success, got {wrote!r}'\n"
    ")\n"
    "assert os.path.isfile(out), (\n"
    "    f'write returned True but {out!r} was not created'\n"
    ")\n"
    "saved = open(out, encoding='utf-8').read()\n"
    "assert 'vault payload' in saved, (\n"
    "    f'written file must contain the payload, got {saved!r}'\n"
    ")\n"
    "os.remove(out)\n"
    "print('OK')\n"
)


_EX3 = Exercise(
    module_id="04", id="ex3",
    filenames=(_EX3_FILE,),
    authorized=_EX3_AUTHORIZED,
    checks=(
        _required_functions(_EX3_FILE, ("secure_archive",)),
        AuthorizedCheck(
            _EX3_FILE, _EX3_AUTHORIZED, allow_method_calls=True,
        ),
        _with_required_check(_EX3_FILE),
        InlineCheck(
            label="secure_archive contract: read ok / read missing / write",
            code=_EX3_CONTRACT_CODE,
        ),
        _runpy_check(
            "script demo: '=== Cyber Archives Security ===' banner",
            _EX3_FILE,
            argv=(_EX3_FILE,),
            fixtures=((_FRAGMENT_NAME, _FRAGMENT_CONTENT),),
            stdout_contains=("=== Cyber Archives Security ===",),
        ),
    ),
    explain=(
        "Define secure_archive(filename, action='read', content='') -> "
        "tuple[bool, str]. Use a 'with' block to open the file: on read "
        "return (True, file_content); on write return (True, success "
        "message) and create/replace the file; on any OSError return "
        "(False, str(error)). The script prints a banner and demos all "
        "three cases."
    ),
)


MODULE_04 = Module(
    id="04",
    title="Data Archivist — Digital Preservation in the Cyber Archives",
    exercises=(_EX0, _EX1, _EX2, _EX3),
)
