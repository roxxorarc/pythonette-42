from pythonette.checks import (
    AssertCheck,
    ClassMethodsCheck,
    Eq,
    Exec,
    HasAttr,
    ImportCheck,
    IsInstance,
    Raises,
    RunCheck,
    Subclass,
    Truthy,
)
from pythonette.subjects.registry import Exercise, Module


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------

def _allowed_imports_check(file: str) -> ImportCheck:
    """Subject III: 'Authorized imports: abc and typing.' Anything else is
    rejected."""
    return ImportCheck(
        file=file,
        allowed=("abc", "typing"),
    )


def _classes_methods_check(
    label: str, file: str, expected: dict[str, tuple[str, ...]],
) -> ClassMethodsCheck:
    """For each class name → required method names: assert presence."""
    return ClassMethodsCheck(
        label=label,
        file=file,
        expected=tuple(expected.items()),
    )


def _runpy_check(
    label: str, file: str, *,
    stdout_contains: tuple[str, ...] = (),
    timeout: float = 5.0,
) -> RunCheck:
    return RunCheck(
        label=label,
        file=file,
        stdout_contains=stdout_contains,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Exercise 0: data_processor.py
# ---------------------------------------------------------------------------

_EX0_FILE = "data_processor.py"

_EX0_ABSTRACT_CHECK = AssertCheck(
    label="DataProcessor is an ABC with abstract validate + ingest",
    quiet=True,
    setup=(
        "import abc, inspect\n"
        "from data_processor import DataProcessor"
    ),
    assertions=(
        Truthy(
            "inspect.isabstract(DataProcessor)",
            message="DataProcessor must be abstract (cannot be instantiated)",
        ),
        Truthy(
            "'validate' in getattr(DataProcessor, '__abstractmethods__', "
            "frozenset())",
            message="'validate' must be @abstractmethod on DataProcessor",
        ),
        Truthy(
            "'ingest' in getattr(DataProcessor, '__abstractmethods__', "
            "frozenset())",
            message="'ingest' must be @abstractmethod on DataProcessor",
        ),
        Subclass(
            "DataProcessor", "abc.ABC",
            message="DataProcessor must inherit from abc.ABC",
        ),
    ),
)


_EX0_INHERITANCE_CHECK = AssertCheck(
    label=(
        "NumericProcessor / TextProcessor / LogProcessor inherit "
        "DataProcessor"
    ),
    quiet=True,
    setup=(
        "from data_processor import (\n"
        "    DataProcessor, NumericProcessor, TextProcessor, LogProcessor,\n"
        ")"
    ),
    assertions=(
        Subclass("NumericProcessor", "DataProcessor"),
        Subclass("TextProcessor", "DataProcessor"),
        Subclass("LogProcessor", "DataProcessor"),
    ),
)


_EX0_NUMERIC_CHECK = AssertCheck(
    label="NumericProcessor: validate / ingest / output round-trip",
    quiet=True,
    setup=(
        "from data_processor import NumericProcessor\n"
        "p = NumericProcessor()"
    ),
    assertions=(
        Eq("p.validate(42)", True),
        Eq("p.validate(3.14)", True),
        Eq("p.validate([1, 2.5, 3])", True),
        Eq("p.validate('Hello')", False),
        Eq("p.validate({'a': 'b'})", False),
        Exec("p.ingest([1, 2, 3])"),
        Exec("rank, val = p.output()"),
        IsInstance("rank", "int"),
        IsInstance("val", "str"),
        Eq("val", "1"),
        Exec("_, val2 = p.output()"),
        Eq("val2", "2"),
        Raises(
            "p.ingest('foo')",
            message="NumericProcessor.ingest('foo') must raise",
        ),
    ),
)


_EX0_TEXT_CHECK = AssertCheck(
    label="TextProcessor: validate / ingest / output round-trip",
    quiet=True,
    setup=(
        "from data_processor import TextProcessor\n"
        "p = TextProcessor()"
    ),
    assertions=(
        Eq("p.validate('hi')", True),
        Eq("p.validate(['a', 'b'])", True),
        Eq("p.validate(42)", False),
        Eq("p.validate([1, 'a'])", False),
        Exec("p.ingest(['Hello', 'World'])"),
        Exec("_, v = p.output()"),
        Eq("v", "Hello"),
        Raises(
            "p.ingest(42)",
            message="TextProcessor.ingest(42) must raise",
        ),
    ),
)


_EX0_LOG_CHECK = AssertCheck(
    label="LogProcessor: validate / ingest / output round-trip",
    quiet=True,
    setup=(
        "from data_processor import LogProcessor\n"
        "p = LogProcessor()\n"
        "good = {'log_level': 'INFO', 'log_message': 'hello'}"
    ),
    assertions=(
        Eq("p.validate(good)", True),
        Eq("p.validate([good, good])", True),
        Eq("p.validate('hello')", False),
        Eq("p.validate({'a': 1})", False),
        Exec("p.ingest([good])"),
        Exec("_, v = p.output()"),
        IsInstance("v", "str"),
        Truthy("'INFO' in v and 'hello' in v"),
        Raises(
            "p.ingest('foo')",
            message="LogProcessor.ingest('foo') must raise",
        ),
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

_EX1_ROUTING_CHECK = AssertCheck(
    label="DataStream routes elements to the correct processor",
    quiet=True,
    setup=(
        "from data_stream import (\n"
        "    DataStream, NumericProcessor, TextProcessor, LogProcessor,\n"
        ")\n"
        "ds = DataStream()\n"
        "num, txt, log = NumericProcessor(), TextProcessor(), LogProcessor()\n"
        "ds.register_processor(num)\n"
        "ds.register_processor(txt)\n"
        "ds.register_processor(log)\n"
        "ds.process_stream([\n"
        "    42, 'hello', [1, 2, 3], ['a', 'b'],\n"
        "    {'log_level': 'INFO', 'log_message': 'm'},\n"
        "])"
    ),
    assertions=(
        Eq("num.output()[1]", "42"),
        Eq("txt.output()[1]", "hello"),
        Truthy(
            "'INFO' in log.output()[1]",
            message="LogProcessor must ingest the dict log entry",
        ),
    ),
)


_EX1_UNHANDLED_CHECK = AssertCheck(
    label="DataStream: unmatched element triggers an error message",
    quiet=True,
    setup=(
        "import io\n"
        "from contextlib import redirect_stdout\n"
        "from data_stream import DataStream, NumericProcessor\n"
        "ds = DataStream()\n"
        "ds.register_processor(NumericProcessor())\n"
        "buf = io.StringIO()\n"
        "with redirect_stdout(buf):\n"
        "    ds.process_stream(['no-processor-for-me'])\n"
        "out = buf.getvalue().lower()"
    ),
    assertions=(
        Truthy(
            "'error' in out or \"can't\" in out or 'cannot' in out",
            message="process_stream must report unhandled elements",
        ),
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


_EX2_PROTOCOL_CHECK = AssertCheck(
    label="ExportPlugin inherits typing.Protocol with process_output",
    quiet=True,
    setup=(
        "import inspect\n"
        "from data_pipeline import ExportPlugin\n"
        "params = list(\n"
        "    inspect.signature(ExportPlugin.process_output).parameters\n"
        ")"
    ),
    assertions=(
        Truthy(
            "getattr(ExportPlugin, '_is_protocol', False)",
            message="ExportPlugin must inherit from typing.Protocol",
        ),
        HasAttr(
            "ExportPlugin", "process_output",
            message="ExportPlugin must declare process_output(...)",
        ),
        Eq("params[:2]", ["self", "data"]),
    ),
)


_EX2_PLUGINS_CHECK = AssertCheck(
    label="data_pipeline defines a CSV plugin and a JSON plugin class",
    setup=(
        "import ast\n"
        "from pathlib import Path\n"
        f"src = Path({_EX2_FILE!r}).read_text(encoding='utf-8')\n"
        f"tree = ast.parse(src, filename={_EX2_FILE!r})\n"
        "names = [\n"
        "    n.name for n in ast.walk(tree)\n"
        "    if isinstance(n, ast.ClassDef)\n"
        "]"
    ),
    assertions=(
        Truthy(
            "any('csv' in n.lower() for n in names)",
            message="expected a CSV plugin class",
        ),
        Truthy(
            "any('json' in n.lower() for n in names)",
            message="expected a JSON plugin class",
        ),
    ),
)


_EX2_PIPELINE_CHECK = AssertCheck(
    label="output_pipeline routes processed data through a custom plugin",
    quiet=True,
    setup=(
        "from data_pipeline import (\n"
        "    DataStream, NumericProcessor, TextProcessor,\n"
        ")\n"
        "ds = DataStream()\n"
        "ds.register_processor(NumericProcessor())\n"
        "ds.register_processor(TextProcessor())\n"
        "ds.process_stream([1, 2, 3, 'a', 'b'])\n"
        "captured = []\n"
        "class _Spy:\n"
        "    def process_output(self, data):\n"
        "        captured.append(list(data))\n"
        "ds.output_pipeline(2, _Spy())\n"
        "flat = [item for batch in captured for item in batch]\n"
        "values = [it[1] for it in flat]"
    ),
    assertions=(
        Truthy(
            "len(captured) >= 1",
            message="plugin.process_output never called",
        ),
        Truthy(
            "all(isinstance(it, tuple) and len(it) == 2 for it in flat)",
            message="each plugin item must be a 2-tuple",
        ),
        Truthy(
            "all("
            "isinstance(it[0], int) and isinstance(it[1], str) "
            "for it in flat"
            ")",
            message="each plugin item must be (int, str)",
        ),
        Truthy(
            "'1' in values and 'a' in values",
            message="plugin must receive items from each processor",
        ),
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
