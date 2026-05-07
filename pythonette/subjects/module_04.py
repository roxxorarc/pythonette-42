"""Module 04 — Data Archivist: digital preservation in the cyber archives."""

from pythonette.checks import (
    AssertCheck,
    AuthorizedCheck,
    Eq,
    Exec,
    FileWritten,
    IsInstance,
    NoForbiddenCallsCheck,
    NoNodeTypesCheck,
    RequireNodeTypesCheck,
    RunCheck,
    TopLevelFunctionsCheck,
    Truthy,
)
from pythonette.subjects.registry import Exercise, Module


_FRAGMENT_NAME = "ancient_fragment.txt"
_FRAGMENT_CONTENT = (
    "[FRAGMENT 001] Digital preservation protocols established 2087\n"
    "[FRAGMENT 002] Knowledge must survive the entropy wars\n"
    "[FRAGMENT 003] Every byte saved is a victory against oblivion\n"
)


def _required_functions(
    file: str, functions: tuple[str, ...],
) -> TopLevelFunctionsCheck:
    """Module-04 scripts may freely use top-level statements (including
    a bare `main()` call). Only assert presence of named top-level defs."""
    return TopLevelFunctionsCheck(
        label=(
            f"{file}: top-level function(s) defined: "
            f"{', '.join(functions)}"
        ),
        file=file,
        functions=functions,
    )


def _no_with_check(file: str) -> NoNodeTypesCheck:
    """Subject: 'with' statement is introduced in ex3 only."""
    return NoNodeTypesCheck(
        label="no use of 'with' statement before exercise 3",
        scope=(file,),
        node_types=("With", "AsyncWith"),
        reason="with statement is introduced in exercise 3 only",
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
    timeout: float = 5.0,
) -> RunCheck:
    """Run `file` as __main__ with controlled argv/stdin/fixtures and
    capture stdout and stderr separately."""
    return RunCheck(
        label=label,
        file=file,
        argv=argv,
        stdin=stdin,
        fixtures=fixtures,
        stdout_contains=stdout_contains,
        stderr_contains=stderr_contains,
        timeout=timeout,
    )


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
        RunCheck(
            label=(
                "filename provided: file is created with '#'-suffixed lines"
            ),
            file=_EX1_FILE,
            argv=(_EX1_FILE, _FRAGMENT_NAME),
            stdin="new_fragment.txt\n",
            fixtures=_EX1_FIXTURES,
            stdout_contains=("new_fragment.txt",),
            post_assertions=(
                FileWritten("new_fragment.txt", line_suffix="#"),
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


def _no_input_check(file: str) -> NoForbiddenCallsCheck:
    return NoForbiddenCallsCheck(
        label="ex2: input() is forbidden — use sys.stdin instead",
        scope=(file,),
        forbidden=("input",),
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


def _with_required_check(file: str) -> RequireNodeTypesCheck:
    return RequireNodeTypesCheck(
        label="ex3 must use the 'with' context manager",
        scope=(file,),
        node_types=("With",),
        reason="ex3 must use a with statement to manage file handles",
    )


_EX3_CONTRACT_CHECK = AssertCheck(
    label="secure_archive contract: read ok / read missing / write",
    quiet=True,
    setup=(
        "import os\n"
        "from pathlib import Path\n"
        f"Path({_FRAGMENT_NAME!r}).write_text(\n"
        f"    {_FRAGMENT_CONTENT!r}, encoding='utf-8',\n"
        ")\n"
        "from ft_vault_security import secure_archive\n"
        f"ok = secure_archive({_FRAGMENT_NAME!r})\n"
        "miss = secure_archive('/not/existing/file/xyz')\n"
        "out_path = '_vault_security_test_output.txt'\n"
        "if os.path.exists(out_path):\n"
        "    os.remove(out_path)\n"
        "wrote = None\n"
        "for _mode in ('write', 1, 2, 'w'):\n"
        "    try:\n"
        "        wrote = secure_archive(out_path, _mode, 'vault payload')\n"
        "        break\n"
        "    except TypeError:\n"
        "        continue\n"
        "saved = (\n"
        "    Path(out_path).read_text(encoding='utf-8')\n"
        "    if Path(out_path).is_file() else ''\n"
        ")"
    ),
    assertions=(
        IsInstance("ok", "tuple"),
        Eq("len(ok)", 2),
        IsInstance("ok[0]", "bool"),
        IsInstance("ok[1]", "str"),
        Eq("ok[0]", True),
        Truthy(
            "'[FRAGMENT 001]' in ok[1]",
            message="returned content must include the file body",
        ),
        IsInstance("miss", "tuple"),
        Eq("len(miss)", 2),
        Eq("miss[0]", False),
        IsInstance("miss[1]", "str"),
        Truthy(
            "miss[1]",
            message="missing file must return a non-empty error message",
        ),
        Truthy(
            "wrote is not None",
            message=(
                "secure_archive must accept an action and content "
                "argument for writing"
            ),
        ),
        IsInstance("wrote", "tuple"),
        Eq("len(wrote)", 2),
        Eq("wrote[0]", True),
        Truthy(
            "Path(out_path).is_file()",
            message="write returned True but file was not created",
        ),
        Truthy(
            "'vault payload' in saved",
            message="written file must contain the payload",
        ),
    ),
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
        _EX3_CONTRACT_CHECK,
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
