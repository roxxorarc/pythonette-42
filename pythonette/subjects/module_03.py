"""Module 03 — Data Quest: mastering Python collections."""

from pythonette.checks import (
    AssertCheck,
    AuthorizedCheck,
    Eq,
    ImportCheck,
    IsInstance,
    RequireNodeTypesCheck,
    RunCheck,
    ScriptCheck,
    StructureCheck,
    Truthy,
)
from pythonette.subjects.registry import Exercise, Module


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _struct(
    file: str,
    functions: tuple[str, ...] = (),
    classes: tuple[str, ...] = (),
    *,
    label: str | None = None,
) -> StructureCheck:
    """Module-03 StructureCheck: scripts demonstrating collection patterns.
    Imports, top-level assigns and __main__ guard are all permitted."""
    return StructureCheck(
        file=file,
        functions=functions,
        classes=classes,
        allow_extra_functions=True,
        allow_extra_classes=True,
        allow_imports=True,
        allow_top_level_assigns=True,
        allow_main_guard=True,
        label=label,
    )


def _argv_contains(
    label: str, file: str, argv: tuple[str, ...], needles: tuple[str, ...],
) -> RunCheck:
    """Run `file` with a given argv and assert each substring is in the
    captured stdout (case-insensitive). Used when several markers all
    describe the same 'thing' (e.g. 'most abundant' + 'least abundant')."""
    return RunCheck(
        label=label,
        file=file,
        argv=argv,
        stdout_contains=needles,
        case_insensitive=True,
    )


def _script_contains(
    label: str, file: str, needles: tuple[str, ...], *,
    stdin: str | None = None, timeout: float = 5.0,
) -> ScriptCheck:
    return ScriptCheck(
        label=label, file=file, stdin=stdin,
        expected_contains=needles, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Exercise 0: ft_command_quest
# ---------------------------------------------------------------------------

_EX0_FILE = "ft_command_quest.py"

_EX0 = Exercise(
    module_id="03", id="ex0",
    filenames=(_EX0_FILE,),
    authorized=("len", "print"),
    checks=(
        _struct(_EX0_FILE, label="ft_command_quest top-level structure"),
        ImportCheck(_EX0_FILE, ("sys",)),
        AuthorizedCheck(
            _EX0_FILE, ("len", "print"), allow_method_calls=False,
        ),
        _argv_contains(
            "no args: banner + 'No arguments provided!'",
            _EX0_FILE, (_EX0_FILE,),
            ("Command Quest", "no arguments provided"),
        ),
        _argv_contains(
            "3 args: 'Arguments received: 3' + first argument echoed",
            _EX0_FILE, (_EX0_FILE, "hello", "world", "42"),
            ("arguments received: 3", "argument 1: hello"),
        ),
    ),
    explain=(
        "Read sys.argv: handle no-arg case, print each argument with its "
        "1-based index, plus the total argv length."
    ),
)

# ---------------------------------------------------------------------------
# Exercise 1: ft_score_analytics
# ---------------------------------------------------------------------------

_EX1_FILE = "ft_score_analytics.py"
_EX1_FIVE = (
    _EX1_FILE, "1500", "2300", "1800", "2100", "1950",
)

_EX1 = Exercise(
    module_id="03", id="ex1",
    filenames=(_EX1_FILE,),
    authorized=("len", "sum", "max", "min", "print"),
    checks=(
        _struct(_EX1_FILE, label="ft_score_analytics top-level structure"),
        ImportCheck(_EX1_FILE, ("sys",)),
        AuthorizedCheck(
            _EX1_FILE,
            ("len", "sum", "max", "min", "print", "int", "float"),
            allow_method_calls=True,
        ),
        _argv_contains(
            "five scores: total computed",
            _EX1_FILE, _EX1_FIVE, ("total",),
        ),
        _argv_contains(
            "five scores: average computed",
            _EX1_FILE, _EX1_FIVE, ("average",),
        ),
        _argv_contains(
            "five scores: high score reported",
            _EX1_FILE, _EX1_FIVE, ("high",),
        ),
        _argv_contains(
            "five scores: low score reported",
            _EX1_FILE, _EX1_FIVE, ("low",),
        ),
        _argv_contains(
            "five scores: score range reported",
            _EX1_FILE, _EX1_FIVE, ("range",),
        ),
        _argv_contains(
            "no args: graceful 'no scores' message",
            _EX1_FILE, (_EX1_FILE,), ("no scores",),
        ),
        _argv_contains(
            "non-numeric input is rejected",
            _EX1_FILE, (_EX1_FILE, "ab", "ac"), ("invalid",),
        ),
    ),
    explain=(
        "Parse argv as numeric scores. Discard non-numeric (with 'Invalid "
        "parameter' message), compute total/average/max/min/range. Empty "
        "input prints a usage line."
    ),
)

# ---------------------------------------------------------------------------
# Exercise 2: ft_coordinate_system
# ---------------------------------------------------------------------------

_EX2_FILE = "ft_coordinate_system.py"
# (3,4,0) -> distance to center = 5.0 ; distance to (4,5,6) = sqrt(38).
_EX2_STDIN_OK = "3,4,0\n4,5,6\n"
_EX2_STDIN_RETRY = "3,abc,0\n3,4,0\n4,5,6\n"

_EX2 = Exercise(
    module_id="03", id="ex2",
    filenames=(_EX2_FILE,),
    authorized=("input", "round", "print", "sqrt"),
    checks=(
        _struct(
            _EX2_FILE,
            functions=("get_player_pos",),
            label="get_player_pos defined",
        ),
        ImportCheck(_EX2_FILE, ("math",)),
        AuthorizedCheck(
            _EX2_FILE,
            ("input", "round", "print", "sqrt", "float"),
            allow_method_calls=True,
        ),
        _script_contains(
            "valid input: banner + tuple + distance to center",
            _EX2_FILE,
            (
                "Game Coordinate System",
                "(3.0, 4.0, 0.0)",
                "5.0",
            ),
            stdin=_EX2_STDIN_OK,
        ),
        _script_contains(
            "valid input: distance between two points",
            _EX2_FILE, ("6.1644",), stdin=_EX2_STDIN_OK,
        ),
        _script_contains(
            "invalid input is rejected then retried",
            _EX2_FILE, ("(3.0, 4.0, 0.0)",), stdin=_EX2_STDIN_RETRY,
        ),
    ),
    explain=(
        "get_player_pos() loops on input() until it gets 'x,y,z' floats and "
        "returns a tuple. The script then computes Euclidean distances "
        "(rounded to 4 decimals) to (0,0,0) and between two points."
    ),
)

# ---------------------------------------------------------------------------
# Exercise 3: ft_achievement_tracker
# ---------------------------------------------------------------------------

_EX3_FILE = "ft_achievement_tracker.py"

_EX3 = Exercise(
    module_id="03", id="ex3",
    filenames=(_EX3_FILE,),
    authorized=("len", "print", "set"),
    checks=(
        _struct(
            _EX3_FILE,
            functions=("gen_player_achievements",),
            label="gen_player_achievements defined",
        ),
        ImportCheck(_EX3_FILE, ("random",)),
        AuthorizedCheck(
            _EX3_FILE, ("len", "print", "set"), allow_method_calls=True,
        ),
        AssertCheck(
            label="gen_player_achievements() returns a set",
            setup=(
                "from ft_achievement_tracker import "
                "gen_player_achievements"
            ),
            assertions=(IsInstance("gen_player_achievements()", "set"),),
        ),
        _script_contains(
            "all four players are listed",
            _EX3_FILE,
            (
                "Player Alice:",
                "Player Bob:",
                "Player Charlie:",
                "Player Dylan:",
            ),
        ),
        _script_contains(
            "union and intersection printed",
            _EX3_FILE,
            ("All distinct achievements:", "Common achievements:"),
        ),
        _script_contains(
            "per-player unique sets printed",
            _EX3_FILE,
            (
                "Only Alice has:",
                "Only Bob has:",
                "Only Charlie has:",
                "Only Dylan has:",
            ),
        ),
        _script_contains(
            "per-player missing sets printed",
            _EX3_FILE,
            (
                "Alice is missing:",
                "Bob is missing:",
                "Charlie is missing:",
                "Dylan is missing:",
            ),
        ),
    ),
    explain=(
        "gen_player_achievements() returns a set chosen at random from a "
        "fixed list. Build sets for Alice/Bob/Charlie/Dylan and print the "
        "union, the intersection, the unique-per-player set, and the "
        "missing set for each player."
    ),
)

# ---------------------------------------------------------------------------
# Exercise 4: ft_inventory_system
# ---------------------------------------------------------------------------

_EX4_FILE = "ft_inventory_system.py"
_EX4_ARGV = (
    _EX4_FILE,
    "sword:1", "potion:5", "shield:2",
    "armor:3", "helmet:1",
    "sword:2", "hello", "key:value",
)

_EX4 = Exercise(
    module_id="03", id="ex4",
    filenames=(_EX4_FILE,),
    authorized=("len", "print", "sum", "list", "round"),
    checks=(
        _struct(_EX4_FILE, label="ft_inventory_system top-level structure"),
        ImportCheck(_EX4_FILE, ("sys",)),
        AuthorizedCheck(
            _EX4_FILE,
            ("len", "print", "sum", "list", "round", "int", "float"),
            allow_method_calls=True,
        ),
        _argv_contains(
            "validation: duplicates and malformed entries are rejected",
            _EX4_FILE, _EX4_ARGV,
            ("redundant item", "invalid parameter"),
        ),
        _argv_contains(
            "stats: total quantity and per-item percentage",
            _EX4_FILE, _EX4_ARGV,
            ("total quantity", "represents"),
        ),
        _argv_contains(
            "ranking: most / least abundant + final update",
            _EX4_FILE, _EX4_ARGV,
            (
                "most abundant",
                "least abundant",
                "updated inventory",
            ),
        ),
    ),
    explain=(
        "Parse argv items 'name:quantity' into a dict. Reject duplicates "
        "and malformed entries with messages. Then list keys, total, "
        "per-item percentage, most/least abundant (first wins on tie), and "
        "add a final new item via dict.update()."
    ),
)

# ---------------------------------------------------------------------------
# Exercise 5: ft_data_stream
# ---------------------------------------------------------------------------

_EX5_FILE = "ft_data_stream.py"

_EX5 = Exercise(
    module_id="03", id="ex5",
    filenames=(_EX5_FILE,),
    authorized=("next", "range", "len", "print"),
    checks=(
        _struct(
            _EX5_FILE,
            functions=("gen_event", "consume_event"),
            label="gen_event + consume_event defined",
        ),
        AuthorizedCheck(
            _EX5_FILE,
            ("next", "range", "len", "print"),
            allow_method_calls=True,
        ),
        AssertCheck(
            label="gen_event and consume_event are generator functions",
            setup=(
                "import inspect\n"
                "from ft_data_stream import gen_event, consume_event\n"
                "ev = next(gen_event())"
            ),
            assertions=(
                Truthy(
                    "inspect.isgeneratorfunction(gen_event)",
                    message=(
                        "gen_event must be a generator function (use yield)"
                    ),
                ),
                Truthy(
                    "inspect.isgeneratorfunction(consume_event)",
                    message=(
                        "consume_event must be a generator function "
                        "(use yield)"
                    ),
                ),
                IsInstance("ev", "tuple"),
                Eq("len(ev)", 2),
            ),
        ),
        AssertCheck(
            label="consume_event drains the input list to empty",
            setup=(
                "from ft_data_stream import consume_event\n"
                "data = [('a', 'x'), ('b', 'y'), ('c', 'z')]\n"
                "seen = [ev for ev in consume_event(data)]"
            ),
            assertions=(
                Eq("len(seen)", 3),
                Eq("data", []),
            ),
        ),
        _script_contains(
            "1000-event loop reaches Event 0 .. Event 999",
            _EX5_FILE, ("Event 0:", "Event 999:"), timeout=10.0,
        ),
        _script_contains(
            "consume_event flow over the 10-event list",
            _EX5_FILE,
            (
                "Built list of 10 events:",
                "Got event from list:",
                "Remains in list:",
            ),
            timeout=10.0,
        ),
    ),
    explain=(
        "gen_event() yields infinite (player, action) tuples. The script "
        "loops 1000 times to print events, then builds a 10-event list and "
        "passes it to consume_event(), a generator that pops a random "
        "element each step until empty."
    ),
)

# ---------------------------------------------------------------------------
# Exercise 6: ft_data_alchemist
# ---------------------------------------------------------------------------

_EX6_FILE = "ft_data_alchemist.py"

_EX6 = Exercise(
    module_id="03", id="ex6",
    filenames=(_EX6_FILE,),
    authorized=("print", "len", "sum", "round"),
    checks=(
        _struct(_EX6_FILE, label="ft_data_alchemist top-level structure"),
        AuthorizedCheck(
            _EX6_FILE,
            ("print", "len", "sum", "round"),
            allow_method_calls=True,
        ),
        RequireNodeTypesCheck(
            label="uses both list and dict comprehensions",
            scope=("ft_data_alchemist.py",),
            node_types=("ListComp", "DictComp"),
            reason="Script must use list AND dict comprehensions",
        ),
        _script_contains(
            "script: capitalized lists (all + filtered) printed",
            _EX6_FILE,
            (
                "all names capitalized",
                "capitalized names only",
            ),
        ),
        _script_contains(
            "script: score dict + average + high-scores filtered dict",
            _EX6_FILE,
            (
                "Score dict",
                "average",
                "High scores",
            ),
        ),
    ),
    explain=(
        "Two list comprehensions (capitalize all / filter capitalized) and "
        "two dict comprehensions (build name→score dict / filter scores "
        "above the average)."
    ),
)


MODULE_03 = Module(
    id="03",
    title="Data Quest — mastering Python collections",
    exercises=(_EX0, _EX1, _EX2, _EX3, _EX4, _EX5, _EX6),
)
