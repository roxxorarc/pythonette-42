from pythonette.subjects.registry import Exercise, Module, TestCase


def _harness(module: str, body: str) -> str:
    return (
        "import sys\n"
        "sys.path.insert(0, '.')\n"
        f"from {module} import *  # noqa: F401,F403\n"
        f"{body}\n"
    )


def _harness_no_input(module: str, body: str) -> str:
    return (
        "import builtins\n"
        "import sys\n"
        "sys.path.insert(0, '.')\n"
        "def _fail_input(*_a, **_kw):\n"
        "    raise AssertionError('input() must not be called')\n"
        "builtins.input = _fail_input\n"
        f"from {module} import *  # noqa: F401,F403\n"
        f"{body}\n"
    )


def _harness_structure(
    module: str,
    expected_functions: tuple[str, ...],
    *,
    allow_extra_functions: bool = False,
) -> str:
    expected_repr = repr(list(expected_functions))
    if allow_extra_functions:
        check = (
            "for fname in expected:\n"
            "    assert fname in functions, (\n"
            "        f'missing function {fname!r} (top-level={functions!r})'\n"
            "    )\n"
        )
    else:
        check = (
            "assert functions == expected, (\n"
            "    f'top-level functions: got={functions!r} '\n"
            "    f'expected={expected!r} '\n"
            "    f'(no main guard, no extras)'\n"
            ")\n"
        )
    return (
        "import ast\n"
        "from pathlib import Path\n"
        f"src = Path('{module}.py').read_text(encoding='utf-8')\n"
        f"tree = ast.parse(src, filename='{module}.py')\n"
        "_FN = (ast.FunctionDef, ast.AsyncFunctionDef)\n"
        "for idx, node in enumerate(tree.body):\n"
        "    if isinstance(node, _FN):\n"
        "        continue\n"
        "    if (\n"
        "        idx == 0\n"
        "        and isinstance(node, ast.Expr)\n"
        "        and isinstance(node.value, ast.Constant)\n"
        "        and isinstance(node.value.value, str)\n"
        "    ):\n"
        "        continue\n"
        "    raise AssertionError(\n"
        "        f'forbidden top-level statement at line {node.lineno}: '\n"
        "        f'{type(node).__name__} '\n"
        "        f'(no main guard, no top-level code, no imports needed)'\n"
        "    )\n"
        "functions = [n.name for n in tree.body if isinstance(n, _FN)]\n"
        f"expected = {expected_repr}\n"
        + check +
        "print('OK')\n"
    )


def _structure_case(
    module: str,
    expected_functions: tuple[str, ...],
    name: str = "structure: only the requested function(s), no main, no top-level code",
    *,
    allow_extra_functions: bool = False,
) -> TestCase:
    return TestCase(
        name=name,
        harness=_harness_structure(
            module, expected_functions,
            allow_extra_functions=allow_extra_functions,
        ),
        expected_stdout="OK",
    )


def _harness_signature(
    module: str,
    function: str,
    expected_params: tuple[str, ...],
    *,
    allow_defaults: bool = False,
    require_callable_no_args: bool = False,
    param_annotations: dict[str, str] | None = None,
    return_annotation: str | None = None,
) -> str:
    lines = [
        "import inspect\n",
        "import sys\n",
        "sys.path.insert(0, '.')\n",
        f"from {module} import {function}\n",
        f"sig = inspect.signature({function})\n",
        "got = list(sig.parameters)\n",
    ]
    if expected_params:
        lines.append(
            f"expected = {list(expected_params)!r}\n"
            "assert got == expected, (\n"
            f"    f'{function}() params: got={{got!r}} expected={{expected!r}}'\n"
            ")\n"
        )
    elif not require_callable_no_args:
        lines.append(
            "assert got == [], (\n"
            f"    f'{function}() must take no parameters, got {{got!r}}'\n"
            ")\n"
        )
    if require_callable_no_args:
        lines.append(
            "for p in sig.parameters.values():\n"
            "    assert p.default is not inspect.Parameter.empty, (\n"
            f"        f'{function}(): param {{p.name!r}} needs a default — '\n"
            "        f'function must be callable with no arguments'\n"
            "    )\n"
        )
    elif not allow_defaults:
        lines.append(
            "for p in sig.parameters.values():\n"
            "    assert p.default is inspect.Parameter.empty, (\n"
            f"        f'{function}(): param {{p.name!r}} must have no default'\n"
            "    )\n"
        )
    if param_annotations:
        for pname, annot in param_annotations.items():
            lines.append(
                f"assert sig.parameters[{pname!r}].annotation is {annot}, (\n"
                f"    f'{function}({pname}): annotation must be {annot}, got '\n"
                f"    f'{{sig.parameters[{pname!r}].annotation!r}}'\n"
                ")\n"
            )
    if return_annotation is not None:
        if return_annotation == "None":
            lines.append(
                "assert sig.return_annotation is None, (\n"
                f"    f'{function}(): return must be None, got '\n"
                "    f'{sig.return_annotation!r}'\n"
                ")\n"
            )
        else:
            lines.append(
                f"assert sig.return_annotation is {return_annotation}, (\n"
                f"    f'{function}(): return must be {return_annotation}, '\n"
                "    f'got {sig.return_annotation!r}'\n"
                ")\n"
            )
    lines.append("print('OK')\n")
    return "".join(lines)


def _signature_case(
    module: str,
    function: str,
    expected_params: tuple[str, ...] = (),
    *,
    allow_defaults: bool = False,
    require_callable_no_args: bool = False,
    param_annotations: dict[str, str] | None = None,
    return_annotation: str | None = None,
    name: str | None = None,
) -> TestCase:
    if name is None:
        if expected_params:
            name = f"signature: {function}({', '.join(expected_params)})"
        elif require_callable_no_args:
            name = f"signature: {function}() callable with no arguments"
        else:
            name = f"signature: {function}() takes no arguments"
    return TestCase(
        name=name,
        harness=_harness_signature(
            module, function, expected_params,
            allow_defaults=allow_defaults,
            require_callable_no_args=require_callable_no_args,
            param_annotations=param_annotations,
            return_annotation=return_annotation,
        ),
        expected_stdout="OK",
    )


def _harness_authorized(
    module: str,
    authorized: tuple[str, ...],
    *,
    allow_method_calls: bool = True,
) -> str:
    authorized_repr = repr(set(authorized))
    method_check = (
        "" if allow_method_calls else
        "    if isinstance(node.func, ast.Attribute):\n"
        "        raise AssertionError(\n"
        "            f'forbidden method call .{node.func.attr}() at line '\n"
        "            f'{node.lineno} (only the listed builtins are allowed)'\n"
        "        )\n"
    )
    return (
        "import ast\n"
        "from pathlib import Path\n"
        f"src = Path('{module}.py').read_text(encoding='utf-8')\n"
        f"tree = ast.parse(src, filename='{module}.py')\n"
        "_FN = (ast.FunctionDef, ast.AsyncFunctionDef)\n"
        "local = {n.name for n in ast.walk(tree) if isinstance(n, _FN)}\n"
        f"authorized = {authorized_repr}\n"
        "allowed = local | authorized\n"
        "for node in ast.walk(tree):\n"
        "    if not isinstance(node, ast.Call):\n"
        "        continue\n"
        + method_check +
        "    if isinstance(node.func, ast.Name):\n"
        "        name = node.func.id\n"
        "        if name not in allowed:\n"
        "            raise AssertionError(\n"
        "                f'forbidden call {name}() at line {node.lineno} '\n"
        "                f'(authorized: {sorted(authorized)})'\n"
        "            )\n"
        "print('OK')\n"
    )


def _authorized_case(
    module: str,
    authorized: tuple[str, ...],
    *,
    allow_method_calls: bool = True,
) -> TestCase:
    return TestCase(
        name=f"authorized: only {', '.join(authorized)}() may be called",
        harness=_harness_authorized(
            module, authorized, allow_method_calls=allow_method_calls,
        ),
        expected_stdout="OK",
    )


def _harness_official_main(
    choice: str,
    stdin_lines: tuple[str, ...],
    expected_pieces: tuple[str, ...],
) -> str:
    inputs = (choice,) + stdin_lines
    return (
        "import builtins\n"
        "import io\n"
        "import sys\n"
        "from contextlib import redirect_stdout\n"
        "from pathlib import Path\n"
        "import pythonette.subjects\n"
        "sys.path.insert(0, '.')\n"
        "helper = Path(pythonette.subjects.__file__).parent / 'main.py'\n"
        f"_inputs = iter({list(inputs)!r})\n"
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
        "    exec(compile(src, str(helper), 'exec'), {'__name__': '__main__'})\n"
        "out = stream.getvalue()\n"
        "assert '\\u274c' not in out, (\n"
        "    f'official helper reported an error:\\n{out}'\n"
        ")\n"
        f"for piece in {list(expected_pieces)!r}:\n"
        "    assert piece in out, (\n"
        "        f'official helper output missing {piece!r}:\\n{out}'\n"
        "    )\n"
        "print('OK')\n"
    )


def _official_case(
    choice: str,
    stdin_lines: tuple[str, ...] = (),
    expected_pieces: tuple[str, ...] = (),
) -> TestCase:
    return TestCase(
        name="official main.py helper runs cleanly",
        harness=_harness_official_main(choice, stdin_lines, expected_pieces),
        expected_stdout="OK",
    )


_EX00 = Exercise(
    module_id="00",
    id="ex0",
    filenames=("ft_hello_garden.py",),
    authorized=("print",),
    cases=(
        TestCase(
            name="prints welcome",
            harness=_harness("ft_hello_garden", "ft_hello_garden()"),
            expected_stdout="Hello, Garden Community!",
        ),
        _signature_case("ft_hello_garden", "ft_hello_garden"),
        _structure_case("ft_hello_garden", ("ft_hello_garden",)),
        _authorized_case(
            "ft_hello_garden", ("print",), allow_method_calls=False,
        ),
        _official_case(
            "0",
            expected_pieces=("Hello, Garden Community!",),
        ),
    ),
    explain=(
        "ft_hello_garden() must print exactly 'Hello, Garden Community!'. "
        "No prompts, no input — just one print."
    ),
)

_EX01 = Exercise(
    module_id="00",
    id="ex1",
    filenames=("ft_garden_name.py",),
    authorized=("input", "print"),
    cases=(
        TestCase(
            name="echoes name + status",
            harness=_harness("ft_garden_name", "ft_garden_name()"),
            stdin="Community Garden\n",
            expected_contains=(
                "Garden: Community Garden",
                "Status: Growing well!",
            ),
        ),
        _signature_case("ft_garden_name", "ft_garden_name"),
        _structure_case("ft_garden_name", ("ft_garden_name",)),
        _authorized_case(
            "ft_garden_name", ("input", "print"), allow_method_calls=False,
        ),
        _official_case(
            "1",
            stdin_lines=("My Garden",),
            expected_pieces=(
                "Garden: My Garden",
                "Status: Growing well!",
            ),
        ),
    ),
    explain=(
        "Read a garden name with input(), then print 'Garden: <name>' on one "
        "line and 'Status: Growing well!' on the next. The status string is "
        "fixed."
    ),
)

_EX02 = Exercise(
    module_id="00",
    id="ex2",
    filenames=("ft_plot_area.py",),
    authorized=("input", "int", "print"),
    cases=(
        TestCase(
            name="5x3 area",
            harness=_harness("ft_plot_area", "ft_plot_area()"),
            stdin="5\n3\n",
            expected_contains=("Plot area: 15",),
        ),
        TestCase(
            name="10x10 area",
            harness=_harness("ft_plot_area", "ft_plot_area()"),
            stdin="10\n10\n",
            expected_contains=("Plot area: 100",),
        ),
        _signature_case("ft_plot_area", "ft_plot_area"),
        _structure_case("ft_plot_area", ("ft_plot_area",)),
        _authorized_case(
            "ft_plot_area", ("input", "int", "print"),
            allow_method_calls=False,
        ),
        _official_case(
            "2",
            stdin_lines=("5", "3"),
            expected_pieces=("Plot area: 15",),
        ),
    ),
    explain=(
        "Read length then width as ints, print 'Plot area: <length*width>'."
    ),
)

_EX03 = Exercise(
    module_id="00",
    id="ex3",
    filenames=("ft_harvest_total.py",),
    authorized=("input", "int", "print"),
    cases=(
        TestCase(
            name="5+8+3",
            harness=_harness("ft_harvest_total", "ft_harvest_total()"),
            stdin="5\n8\n3\n",
            expected_contains=("Total harvest: 16",),
        ),
        TestCase(
            name="0+0+0",
            harness=_harness("ft_harvest_total", "ft_harvest_total()"),
            stdin="0\n0\n0\n",
            expected_contains=("Total harvest: 0",),
        ),
        _signature_case("ft_harvest_total", "ft_harvest_total"),
        _structure_case("ft_harvest_total", ("ft_harvest_total",)),
        _authorized_case(
            "ft_harvest_total", ("input", "int", "print"),
            allow_method_calls=False,
        ),
        _official_case(
            "3",
            stdin_lines=("5", "8", "3"),
            expected_pieces=("Total harvest: 16",),
        ),
    ),
    explain="Read three int harvests and print 'Total harvest: <sum>'.",
)

_EX04 = Exercise(
    module_id="00",
    id="ex4",
    filenames=("ft_plant_age.py",),
    authorized=("input", "int", "print"),
    cases=(
        TestCase(
            name="ready (>60)",
            harness=_harness("ft_plant_age", "ft_plant_age()"),
            stdin="75\n",
            expected_contains=("Plant is ready to harvest!",),
        ),
        TestCase(
            name="not ready (<=60)",
            harness=_harness("ft_plant_age", "ft_plant_age()"),
            stdin="45\n",
            expected_contains=("Plant needs more time to grow.",),
        ),
        TestCase(
            name="boundary 60 (not ready)",
            harness=_harness("ft_plant_age", "ft_plant_age()"),
            stdin="60\n",
            expected_contains=("Plant needs more time to grow.",),
        ),
        _signature_case("ft_plant_age", "ft_plant_age"),
        _structure_case("ft_plant_age", ("ft_plant_age",)),
        _authorized_case(
            "ft_plant_age", ("input", "int", "print"),
            allow_method_calls=False,
        ),
        _official_case(
            "4",
            stdin_lines=("75",),
            expected_pieces=("Plant is ready to harvest!",),
        ),
    ),
    explain=(
        "Strict comparison: only ages >60 are ready. The boundary 60 is NOT "
        "ready. Watch the dot at the end of the 'needs more time' message."
    ),
)

_EX05 = Exercise(
    module_id="00",
    id="ex5",
    filenames=("ft_water_reminder.py",),
    authorized=("input", "int", "print"),
    cases=(
        TestCase(
            name="needs water (>2)",
            harness=_harness("ft_water_reminder", "ft_water_reminder()"),
            stdin="4\n",
            expected_contains=("Water the plants!",),
        ),
        TestCase(
            name="fine (<=2)",
            harness=_harness("ft_water_reminder", "ft_water_reminder()"),
            stdin="1\n",
            expected_contains=("Plants are fine",),
        ),
        TestCase(
            name="boundary 2 (fine)",
            harness=_harness("ft_water_reminder", "ft_water_reminder()"),
            stdin="2\n",
            expected_contains=("Plants are fine",),
        ),
        _signature_case("ft_water_reminder", "ft_water_reminder"),
        _structure_case("ft_water_reminder", ("ft_water_reminder",)),
        _authorized_case(
            "ft_water_reminder", ("input", "int", "print"),
            allow_method_calls=False,
        ),
        _official_case(
            "5",
            stdin_lines=("4",),
            expected_pieces=("Water the plants!",),
        ),
    ),
    explain="Strictly more than 2 days → water. Exactly 2 → still fine.",
)

_EX06 = Exercise(
    module_id="00",
    id="ex6",
    filenames=(
        "ft_count_harvest_iterative.py",
        "ft_count_harvest_recursive.py",
    ),
    authorized=("input", "int", "print", "range"),
    cases=(
        TestCase(
            name="iterative count to 3",
            harness=_harness(
                "ft_count_harvest_iterative", "ft_count_harvest_iterative()"
            ),
            stdin="3\n",
            expected_contains=("Day 1", "Day 2", "Day 3", "Harvest time!"),
        ),
        TestCase(
            name="recursive count to 3",
            harness=_harness(
                "ft_count_harvest_recursive", "ft_count_harvest_recursive()"
            ),
            stdin="3\n",
            expected_contains=("Day 1", "Day 2", "Day 3", "Harvest time!"),
        ),
        TestCase(
            name="recursive count to 5 — same output as iterative",
            harness=_harness(
                "ft_count_harvest_recursive", "ft_count_harvest_recursive()"
            ),
            stdin="5\n",
            expected_contains=(
                "Day 1",
                "Day 2",
                "Day 3",
                "Day 4",
                "Day 5",
                "Harvest time!",
            ),
        ),
        _signature_case(
            "ft_count_harvest_iterative",
            "ft_count_harvest_iterative",
        ),
        _signature_case(
            "ft_count_harvest_recursive",
            "ft_count_harvest_recursive",
            require_callable_no_args=True,
            name="signature: ft_count_harvest_recursive() callable with no arguments (defaults allowed)",
        ),
        _structure_case(
            "ft_count_harvest_iterative",
            ("ft_count_harvest_iterative",),
            "iterative structure: only ft_count_harvest_iterative, no main, no extras",
        ),
        _structure_case(
            "ft_count_harvest_recursive",
            ("ft_count_harvest_recursive",),
            "recursive structure: ft_count_harvest_recursive present, helpers ok, no main",
            allow_extra_functions=True,
        ),
        _authorized_case(
            "ft_count_harvest_iterative",
            ("input", "int", "print", "range"),
            allow_method_calls=False,
        ),
        _authorized_case(
            "ft_count_harvest_recursive",
            ("input", "int", "print", "range"),
            allow_method_calls=False,
        ),
        _official_case(
            "6",
            stdin_lines=("3", "3"),
            expected_pieces=(
                "Day 1",
                "Day 2",
                "Day 3",
                "Harvest time!",
            ),
        ),
    ),
    explain=(
        "Print Day 1 .. Day N (one per line) then 'Harvest time!'. The "
        "iterative and recursive versions must produce identical output. "
        "Iterative file: only the requested function. Recursive file: "
        "helpers / default args / nested function all allowed."
    ),
)

_EX07 = Exercise(
    module_id="00",
    id="ex7",
    filenames=("ft_seed_inventory.py",),
    authorized=("print",),
    cases=(
        TestCase(
            name="packets",
            harness=_harness(
                "ft_seed_inventory",
                "ft_seed_inventory('tomato', 15, 'packets')",
            ),
            expected_stdout="Tomato seeds: 15 packets available",
        ),
        TestCase(
            name="grams",
            harness=_harness(
                "ft_seed_inventory",
                "ft_seed_inventory('carrot', 8, 'grams')",
            ),
            expected_stdout="Carrot seeds: 8 grams total",
        ),
        TestCase(
            name="area",
            harness=_harness(
                "ft_seed_inventory",
                "ft_seed_inventory('lettuce', 12, 'area')",
            ),
            expected_stdout="Lettuce seeds: covers 12 square meters",
        ),
        TestCase(
            name="unknown unit",
            harness=_harness(
                "ft_seed_inventory",
                "ft_seed_inventory('basil', 5, 'liters')",
            ),
            expected_stdout="Unknown unit type",
        ),
        TestCase(
            name="does not call input()",
            harness=_harness_no_input(
                "ft_seed_inventory",
                "ft_seed_inventory('tomato', 15, 'packets')",
            ),
            expected_stdout="Tomato seeds: 15 packets available",
        ),
        _signature_case(
            "ft_seed_inventory",
            "ft_seed_inventory",
            ("seed_type", "quantity", "unit"),
            param_annotations={
                "seed_type": "str",
                "quantity": "int",
                "unit": "str",
            },
            return_annotation="None",
            name=(
                "signature: ft_seed_inventory(seed_type: str, "
                "quantity: int, unit: str) -> None"
            ),
        ),
        _structure_case("ft_seed_inventory", ("ft_seed_inventory",)),
        _authorized_case(
            "ft_seed_inventory", ("print",), allow_method_calls=True,
        ),
        _official_case(
            "7",
            expected_pieces=(
                "Tomato seeds: 15 packets available",
                "Carrot seeds: 8 grams total",
                "Lettuce seeds: covers 12 square meters",
                "Unknown unit type",
            ),
        ),
    ),
    explain=(
        "Signature: ft_seed_inventory(seed_type: str, quantity: int, "
        "unit: str) -> None. Capitalize seed_type. Units 'packets', "
        "'grams', 'area' format their own line; anything else prints "
        "exactly 'Unknown unit type'."
    ),
)


MODULE_00 = Module(
    id="00",
    title="Growing Code — Python fundamentals through garden data",
    exercises=(_EX00, _EX01, _EX02, _EX03, _EX04, _EX05, _EX06, _EX07),
)
