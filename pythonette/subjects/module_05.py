from pythonette.checks import InlineCheck
from pythonette.subjects.registry import Exercise, Module


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------

def _allowed_imports_check(file: str) -> InlineCheck:
    """Subject III: 'Authorized imports: abc and typing.' Anything else is
    rejected."""
    return InlineCheck(
        label=f"{file}: only 'abc' and 'typing' may be imported",
        code=(
            "import ast\n"
            "from pathlib import Path\n"
            f"src = Path({file!r}).read_text(encoding='utf-8')\n"
            f"tree = ast.parse(src, filename={file!r})\n"
            "allowed = {'abc', 'typing'}\n"
            "bad = []\n"
            "for n in ast.walk(tree):\n"
            "    if isinstance(n, ast.Import):\n"
            "        for a in n.names:\n"
            "            top = a.name.split('.', 1)[0]\n"
            "            if top not in allowed:\n"
            "                bad.append((n.lineno, a.name))\n"
            "    elif isinstance(n, ast.ImportFrom):\n"
            "        top = (n.module or '').split('.', 1)[0]\n"
            "        if top not in allowed:\n"
            "            bad.append((n.lineno, n.module))\n"
            "assert not bad, (\n"
            "    f'forbidden import(s) — only abc/typing allowed: {bad!r}'\n"
            ")\n"
            "print('OK')\n"
        ),
    )


def _classes_methods_check(
    label: str, file: str, expected: dict[str, tuple[str, ...]],
) -> InlineCheck:
    """For each class name → required method names: assert presence."""
    return InlineCheck(
        label=label,
        code=(
            "import ast\n"
            "from pathlib import Path\n"
            f"src = Path({file!r}).read_text(encoding='utf-8')\n"
            f"tree = ast.parse(src, filename={file!r})\n"
            "by_class = {}\n"
            "for n in ast.walk(tree):\n"
            "    if isinstance(n, ast.ClassDef):\n"
            "        by_class[n.name] = {\n"
            "            f.name for f in n.body\n"
            "            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))\n"
            "        }\n"
            f"expected = {expected!r}\n"
            "for cls, methods in expected.items():\n"
            "    assert cls in by_class, (\n"
            "        f'missing class {cls!r}; found: {sorted(by_class)!r}'\n"
            "    )\n"
            "    missing = [m for m in methods if m not in by_class[cls]]\n"
            "    assert not missing, (\n"
            "        f'class {cls!r} is missing method(s) {missing!r}; '\n"
            "        f'has: {sorted(by_class[cls])!r}'\n"
            "    )\n"
            "print('OK')\n"
        ),
    )


def _runpy_check(
    label: str, file: str, *,
    stdout_contains: tuple[str, ...] = (),
    timeout: float = 5.0,
) -> InlineCheck:
    code = (
        "import runpy, sys, io\n"
        "from contextlib import redirect_stdout, redirect_stderr\n"
        "sys.path.insert(0, '.')\n"
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
    code += "print('OK')\n"
    return InlineCheck(label=label, code=code, timeout=timeout)


def _import_silent(module: str) -> str:
    """Snippet that imports the student module without letting its top-level
    demo pollute stdout/stderr — needed since these scripts are designed to
    be run as __main__ but we want to introspect their classes."""
    return (
        "import sys, io\n"
        "from contextlib import redirect_stdout, redirect_stderr\n"
        "sys.path.insert(0, '.')\n"
        "with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):\n"
        f"    mod = __import__({module!r})\n"
    )


# ---------------------------------------------------------------------------
# Exercise 0: data_processor.py
# ---------------------------------------------------------------------------

_EX0_FILE = "data_processor.py"

_EX0_ABSTRACT_CHECK = InlineCheck(
    label="DataProcessor is an ABC with abstract validate + ingest",
    code=(
        _import_silent("data_processor")
        + "import inspect, abc\n"
        "DP = mod.DataProcessor\n"
        "assert inspect.isabstract(DP), (\n"
        "    'DataProcessor must be abstract (cannot be instantiated)'\n"
        ")\n"
        "abstracts = getattr(DP, '__abstractmethods__', frozenset())\n"
        "for name in ('validate', 'ingest'):\n"
        "    assert name in abstracts, (\n"
        "        f'{name!r} must be marked @abstractmethod on DataProcessor; '\n"
        "        f'abstract methods: {sorted(abstracts)!r}'\n"
        "    )\n"
        "assert issubclass(DP, abc.ABC), 'DataProcessor must inherit from abc.ABC'\n"
        "print('OK')\n"
    ),
)


_EX0_INHERITANCE_CHECK = InlineCheck(
    label="NumericProcessor / TextProcessor / LogProcessor inherit DataProcessor",
    code=(
        _import_silent("data_processor")
        + "for name in ('NumericProcessor', 'TextProcessor', 'LogProcessor'):\n"
        "    cls = getattr(mod, name)\n"
        "    assert issubclass(cls, mod.DataProcessor), (\n"
        "        f'{name} must inherit from DataProcessor'\n"
        "    )\n"
        "print('OK')\n"
    ),
)


_EX0_NUMERIC_CHECK = InlineCheck(
    label="NumericProcessor: validate / ingest / output round-trip",
    code=(
        _import_silent("data_processor")
        + "p = mod.NumericProcessor()\n"
        "assert p.validate(42) is True, 'NumericProcessor.validate(42) must be True'\n"
        "assert p.validate(3.14) is True\n"
        "assert p.validate([1, 2.5, 3]) is True\n"
        "assert p.validate('Hello') is False\n"
        "assert p.validate({'a': 'b'}) is False\n"
        "p.ingest([1, 2, 3])\n"
        "rank, val = p.output()\n"
        "assert isinstance(rank, int) and isinstance(val, str), (\n"
        "    f'output() must return tuple[int, str], got {(rank, val)!r}'\n"
        ")\n"
        "assert val == '1', f'oldest item first; got {val!r}'\n"
        "rank2, val2 = p.output()\n"
        "assert val2 == '2', f'second oldest = 2; got {val2!r}'\n"
        "# invalid ingest must raise (subject explicitly requires it)\n"
        "raised = False\n"
        "try:\n"
        "    p.ingest('foo')  # type: ignore[arg-type]\n"
        "except Exception:\n"
        "    raised = True\n"
        "assert raised, 'NumericProcessor.ingest(\"foo\") must raise'\n"
        "print('OK')\n"
    ),
)


_EX0_TEXT_CHECK = InlineCheck(
    label="TextProcessor: validate / ingest / output round-trip",
    code=(
        _import_silent("data_processor")
        + "p = mod.TextProcessor()\n"
        "assert p.validate('hi') is True\n"
        "assert p.validate(['a', 'b']) is True\n"
        "assert p.validate(42) is False\n"
        "assert p.validate([1, 'a']) is False\n"
        "p.ingest(['Hello', 'World'])\n"
        "_, v = p.output()\n"
        "assert v == 'Hello', f'oldest first; got {v!r}'\n"
        "raised = False\n"
        "try:\n"
        "    p.ingest(42)  # type: ignore[arg-type]\n"
        "except Exception:\n"
        "    raised = True\n"
        "assert raised, 'TextProcessor.ingest(42) must raise'\n"
        "print('OK')\n"
    ),
)


_EX0_LOG_CHECK = InlineCheck(
    label="LogProcessor: validate / ingest / output round-trip",
    code=(
        _import_silent("data_processor")
        + "p = mod.LogProcessor()\n"
        "good = {'log_level': 'INFO', 'log_message': 'hello'}\n"
        "assert p.validate(good) is True\n"
        "assert p.validate([good, good]) is True\n"
        "assert p.validate('hello') is False\n"
        "assert p.validate({'a': 1}) is False  # values must be str\n"
        "p.ingest([good])\n"
        "_, v = p.output()\n"
        "assert isinstance(v, str) and 'INFO' in v and 'hello' in v, (\n"
        "    f'log entry should be stringified; got {v!r}'\n"
        ")\n"
        "raised = False\n"
        "try:\n"
        "    p.ingest('foo')  # type: ignore[arg-type]\n"
        "except Exception:\n"
        "    raised = True\n"
        "assert raised, 'LogProcessor.ingest(\"foo\") must raise'\n"
        "print('OK')\n"
    ),
)


_EX0 = Exercise(
    module_id="05", id="ex0",
    filenames=(_EX0_FILE,),
    checks=(
        _allowed_imports_check(_EX0_FILE),
        _classes_methods_check(
            "ex0: required classes and methods defined",
            _EX0_FILE,
            {
                "DataProcessor": ("validate", "ingest", "output"),
                "NumericProcessor": ("validate", "ingest"),
                "TextProcessor": ("validate", "ingest"),
                "LogProcessor": ("validate", "ingest"),
            },
        ),
        _EX0_ABSTRACT_CHECK,
        _EX0_INHERITANCE_CHECK,
        _EX0_NUMERIC_CHECK,
        _EX0_TEXT_CHECK,
        _EX0_LOG_CHECK,
        _runpy_check(
            "script demo prints the data-processor banner",
            _EX0_FILE,
            stdout_contains=(
                "=== Code Nexus - Data Processor ===",
                "Numeric Processor",
                "Text Processor",
                "Log Processor",
            ),
        ),
    ),
    explain=(
        "Abstract base DataProcessor(abc.ABC) with @abstractmethod validate "
        "and ingest, concrete output() -> tuple[int, str] returning the "
        "oldest stored item and its rank (FIFO). Three subclasses: "
        "NumericProcessor (int/float/lists), TextProcessor (str/list[str]), "
        "LogProcessor (dict[str,str]/list of those). ingest() raises on "
        "invalid data."
    ),
)


# ---------------------------------------------------------------------------
# Exercise 1: data_stream.py
# ---------------------------------------------------------------------------

_EX1_FILE = "data_stream.py"

_EX1_ROUTING_CHECK = InlineCheck(
    label="DataStream routes elements to the correct processor",
    code=(
        _import_silent("data_stream")
        + "ds = mod.DataStream()\n"
        "num = mod.NumericProcessor()\n"
        "txt = mod.TextProcessor()\n"
        "log = mod.LogProcessor()\n"
        "ds.register_processor(num)\n"
        "ds.register_processor(txt)\n"
        "ds.register_processor(log)\n"
        "ds.process_stream([\n"
        "    42, 'hello', [1, 2, 3], ['a', 'b'],\n"
        "    {'log_level': 'INFO', 'log_message': 'm'},\n"
        "])\n"
        "# Each processor must have at least 1 item ingested.\n"
        "got_num = num.output()\n"
        "got_txt = txt.output()\n"
        "got_log = log.output()\n"
        "assert got_num[1] == '42', got_num\n"
        "assert got_txt[1] == 'hello', got_txt\n"
        "assert 'INFO' in got_log[1], got_log\n"
        "print('OK')\n"
    ),
)


_EX1_UNHANDLED_CHECK = InlineCheck(
    label="DataStream: unmatched element triggers an error message",
    code=(
        _import_silent("data_stream")
        + "import io\n"
        "from contextlib import redirect_stdout\n"
        "ds = mod.DataStream()\n"
        "ds.register_processor(mod.NumericProcessor())\n"
        "buf = io.StringIO()\n"
        "with redirect_stdout(buf):\n"
        "    ds.process_stream(['no-processor-for-me'])\n"
        "out = buf.getvalue().lower()\n"
        "assert ('error' in out or \"can't\" in out or 'cannot' in out), (\n"
        "    f'process_stream must report unhandled elements; got {out!r}'\n"
        ")\n"
        "print('OK')\n"
    ),
)


_EX1 = Exercise(
    module_id="05", id="ex1",
    filenames=(_EX1_FILE,),
    checks=(
        _allowed_imports_check(_EX1_FILE),
        _classes_methods_check(
            "ex1: DataStream and DataProcessor hierarchy still defined",
            _EX1_FILE,
            {
                "DataProcessor": ("validate", "ingest", "output"),
                "NumericProcessor": ("validate", "ingest"),
                "TextProcessor": ("validate", "ingest"),
                "LogProcessor": ("validate", "ingest"),
                "DataStream": (
                    "register_processor",
                    "process_stream",
                    "print_processors_stats",
                ),
            },
        ),
        _EX1_ROUTING_CHECK,
        _EX1_UNHANDLED_CHECK,
        _runpy_check(
            "script demo prints the data-stream banner and stats",
            _EX1_FILE,
            stdout_contains=(
                "=== Code Nexus - Data Stream ===",
                "DataStream statistics",
            ),
        ),
    ),
    explain=(
        "Carry over ex0's classes. Add DataStream with register_processor, "
        "process_stream (validates each item against every registered "
        "processor and ingests via the first match; prints an error line "
        "when nothing matches) and print_processors_stats (total ingested "
        "+ remaining per processor)."
    ),
)


# ---------------------------------------------------------------------------
# Exercise 2: data_pipeline.py
# ---------------------------------------------------------------------------

_EX2_FILE = "data_pipeline.py"


_EX2_PROTOCOL_CHECK = InlineCheck(
    label="ExportPlugin inherits typing.Protocol with process_output",
    code=(
        _import_silent("data_pipeline")
        + "import typing, inspect\n"
        "EP = mod.ExportPlugin\n"
        "is_protocol = getattr(EP, '_is_protocol', False)\n"
        "assert is_protocol, (\n"
        "    'ExportPlugin must inherit from typing.Protocol'\n"
        ")\n"
        "assert hasattr(EP, 'process_output'), (\n"
        "    'ExportPlugin must declare process_output(...)'\n"
        ")\n"
        "sig = inspect.signature(EP.process_output)\n"
        "params = list(sig.parameters)\n"
        "assert params[:2] == ['self', 'data'], (\n"
        "    f'process_output(self, data) expected; got {params!r}'\n"
        ")\n"
        "print('OK')\n"
    ),
)


_EX2_PLUGINS_CHECK = InlineCheck(
    label="data_pipeline defines a CSV plugin and a JSON plugin class",
    code=(
        "import ast\n"
        "from pathlib import Path\n"
        f"src = Path({_EX2_FILE!r}).read_text(encoding='utf-8')\n"
        f"tree = ast.parse(src, filename={_EX2_FILE!r})\n"
        "names = [n.name for n in ast.walk(tree)\n"
        "         if isinstance(n, ast.ClassDef)]\n"
        "has_csv = any('csv' in n.lower() for n in names)\n"
        "has_json = any('json' in n.lower() for n in names)\n"
        "assert has_csv, f'expected a CSV plugin class; got {names!r}'\n"
        "assert has_json, f'expected a JSON plugin class; got {names!r}'\n"
        "print('OK')\n"
    ),
)


_EX2_PIPELINE_CHECK = InlineCheck(
    label="output_pipeline routes processed data through a custom plugin",
    code=(
        _import_silent("data_pipeline")
        + "ds = mod.DataStream()\n"
        "ds.register_processor(mod.NumericProcessor())\n"
        "ds.register_processor(mod.TextProcessor())\n"
        "ds.process_stream([1, 2, 3, 'a', 'b'])\n"
        "captured = []\n"
        "class _Spy:\n"
        "    def process_output(self, data):\n"
        "        captured.append(list(data))\n"
        "ds.output_pipeline(2, _Spy())\n"
        "assert len(captured) >= 1, (\n"
        "    f'plugin.process_output never called; captured={captured!r}'\n"
        ")\n"
        "flat = [item for batch in captured for item in batch]\n"
        "for it in flat:\n"
        "    assert isinstance(it, tuple) and len(it) == 2, (\n"
        "        f'each plugin item must be (int, str), got {it!r}'\n"
        "    )\n"
        "    assert isinstance(it[0], int) and isinstance(it[1], str), it\n"
        "values = [it[1] for it in flat]\n"
        "assert '1' in values and 'a' in values, (\n"
        "    f'plugin must receive items from each processor; got {values!r}'\n"
        ")\n"
        "print('OK')\n"
    ),
)


_EX2 = Exercise(
    module_id="05", id="ex2",
    filenames=(_EX2_FILE,),
    checks=(
        _allowed_imports_check(_EX2_FILE),
        _classes_methods_check(
            "ex2: ExportPlugin + DataStream.output_pipeline defined",
            _EX2_FILE,
            {
                "DataProcessor": ("validate", "ingest", "output"),
                "DataStream": (
                    "register_processor",
                    "process_stream",
                    "print_processors_stats",
                    "output_pipeline",
                ),
                "ExportPlugin": ("process_output",),
            },
        ),
        _EX2_PROTOCOL_CHECK,
        _EX2_PLUGINS_CHECK,
        _EX2_PIPELINE_CHECK,
        _runpy_check(
            "script demo runs the full pipeline with CSV + JSON output",
            _EX2_FILE,
            stdout_contains=(
                "=== Code Nexus - Data Pipeline ===",
                "DataStream statistics",
                "CSV",
                "JSON",
            ),
        ),
    ),
    explain=(
        "Carry over ex1. Add ExportPlugin(typing.Protocol) with "
        "process_output(self, data: list[tuple[int, str]]) -> None. "
        "DataStream gets output_pipeline(nb, plugin): pop nb items from "
        "each processor and feed them to plugin.process_output. Provide "
        "at least a CSV-style and a JSON-style plugin (duck-typed against "
        "the Protocol)."
    ),
)


MODULE_05 = Module(
    id="05",
    title="Code Nexus — Polymorphic Data Streams in the Digital Matrix",
    exercises=(_EX0, _EX1, _EX2),
)
