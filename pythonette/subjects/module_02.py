from pythonette.checks import (
    AuthorizedCheck,
    InlineCheck,
    ScriptCheck,
    StructureCheck,
)
from pythonette.subjects.registry import Exercise, Module


def _struct_pipeline(
    file: str,
    functions: tuple[str, ...] = (),
    classes: tuple[str, ...] = (),
    *,
    label: str | None = None,
) -> StructureCheck:
    """Module-02 StructureCheck: scripts that may have a __main__ guard,
    imports, and top-level assigns. We only assert presence of the
    required functions/classes."""
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


def _ast_helper(filename: str) -> str:
    """Return Python source that loads filename, parses it, and exposes a
    `_fn(name)` helper to find a top-level FunctionDef by name."""
    return (
        "import ast\n"
        "from pathlib import Path\n"
        f"src = Path({filename!r}).read_text(encoding='utf-8')\n"
        f"tree = ast.parse(src, filename={filename!r})\n"
        "def _fn(name):\n"
        "    for n in ast.walk(tree):\n"
        "        if isinstance(n, ast.FunctionDef) and n.name == name:\n"
        "            return n\n"
        "    return None\n"
    )


_EX0 = Exercise(
    module_id="02", id="ex0",
    filenames=("ft_first_exception.py",),
    authorized=("int", "print"),
    checks=(
        _struct_pipeline(
            "ft_first_exception.py",
            functions=("input_temperature", "test_temperature"),
            label="input_temperature + test_temperature",
        ),
        AuthorizedCheck(
            "ft_first_exception.py", ("int", "print"),
            allow_method_calls=False,
        ),
        InlineCheck(
            label=(
                "exception handling lives in test_temperature(), "
                "not input_temperature()"
            ),
            code=(
                _ast_helper("ft_first_exception.py")
                + "in_fn = _fn('input_temperature')\n"
                "test_fn = _fn('test_temperature')\n"
                "assert in_fn is not None, 'input_temperature missing'\n"
                "assert test_fn is not None, 'test_temperature missing'\n"
                "assert not any(\n"
                "    isinstance(n, ast.Try) for n in ast.walk(in_fn)\n"
                "), (\n"
                "    'input_temperature must not contain try/except — '\n"
                "    'let it fail and catch in test_temperature'\n"
                ")\n"
                "assert any(\n"
                "    isinstance(n, ast.Try) for n in ast.walk(test_fn)\n"
                "), (\n"
                "    'test_temperature must catch input_temperature '\n"
                "    'failures with try/except'\n"
                ")\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="input_temperature('25') == 25",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_first_exception import input_temperature\n"
                "got = input_temperature('25')\n"
                "assert got == 25, f'expected 25, got {got!r}'\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="input_temperature('abc') raises (caught at test level)",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_first_exception import input_temperature\n"
                "try:\n"
                "    input_temperature('abc')\n"
                "except Exception:\n"
                "    print('OK')\n"
                "else:\n"
                "    raise AssertionError('expected exception on abc input')\n"
            ),
        ),
        ScriptCheck(
            label="script prints temperature banner and runs all tests",
            file="ft_first_exception.py",
            expected_contains=(
                "=== Garden Temperature ===",
                "25",
                "abc",
                "All tests completed",
            ),
        ),
    ),
    explain=(
        "input_temperature(temp_str) converts and returns an int — it must "
        "let exceptions propagate. test_temperature() runs valid + invalid "
        "cases inside try/except, prints the error, keeps going."
    ),
)

_EX1 = Exercise(
    module_id="02", id="ex1",
    filenames=("ft_raise_exception.py",),
    authorized=("int", "print"),
    checks=(
        _struct_pipeline(
            "ft_raise_exception.py",
            functions=("input_temperature", "test_temperature"),
            label="input_temperature + test_temperature",
        ),
        AuthorizedCheck(
            "ft_raise_exception.py", ("int", "print"),
            allow_method_calls=False,
        ),
        InlineCheck(
            label="input_temperature('25') == 25 (in range)",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_raise_exception import input_temperature\n"
                "assert input_temperature('25') == 25\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="boundaries 0 and 40 are valid",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_raise_exception import input_temperature\n"
                "assert input_temperature('0') == 0\n"
                "assert input_temperature('40') == 40\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="input_temperature('100') raises (>40)",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_raise_exception import input_temperature\n"
                "try:\n"
                "    input_temperature('100')\n"
                "except Exception:\n"
                "    print('OK')\n"
                "else:\n"
                "    raise AssertionError('100 must raise (max 40)')\n"
            ),
        ),
        InlineCheck(
            label="input_temperature('-50') raises (<0)",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_raise_exception import input_temperature\n"
                "try:\n"
                "    input_temperature('-50')\n"
                "except Exception:\n"
                "    print('OK')\n"
                "else:\n"
                "    raise AssertionError('-50 must raise (min 0)')\n"
            ),
        ),
        InlineCheck(
            label="input_temperature('abc') raises",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_raise_exception import input_temperature\n"
                "try:\n"
                "    input_temperature('abc')\n"
                "except Exception:\n"
                "    print('OK')\n"
                "else:\n"
                "    raise AssertionError('abc must raise')\n"
            ),
        ),
        ScriptCheck(
            label="script prints checker banner",
            file="ft_raise_exception.py",
            expected_contains=(
                "=== Garden Temperature Checker ===",
                "All tests completed",
            ),
        ),
    ),
    explain=(
        "Same as ex0 plus range validation: temperature must be 0..40 "
        "inclusive. Out-of-range values raise an exception."
    ),
)

_EX2 = Exercise(
    module_id="02", id="ex2",
    filenames=("ft_different_errors.py",),
    authorized=("print", "open", "int"),
    checks=(
        _struct_pipeline(
            "ft_different_errors.py",
            functions=("garden_operations", "test_error_types"),
            label="garden_operations + test_error_types",
        ),
        AuthorizedCheck(
            "ft_different_errors.py", ("print", "open", "int", "range"),
            allow_method_calls=False,
        ),
        InlineCheck(
            label="garden_operations triggers real faults (no manual raise)",
            code=(
                _ast_helper("ft_different_errors.py")
                + "op = _fn('garden_operations')\n"
                "assert op is not None, 'garden_operations missing'\n"
                "assert not any(\n"
                "    isinstance(n, ast.Raise) for n in ast.walk(op)\n"
                "), (\n"
                "    'garden_operations must trigger real faulty code '\n"
                "    \"(int('abc'), 1/0, open(missing), str+int), \"\n"
                "    'not manual raise'\n"
                ")\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="test_error_types catches multiple error types in one try",
            code=(
                _ast_helper("ft_different_errors.py")
                + "test_fn = _fn('test_error_types')\n"
                "assert test_fn is not None, 'test_error_types missing'\n"
                "ok = False\n"
                "for n in ast.walk(test_fn):\n"
                "    if not isinstance(n, ast.Try):\n"
                "        continue\n"
                "    if len(n.handlers) >= 2:\n"
                "        ok = True\n"
                "        break\n"
                "    for h in n.handlers:\n"
                "        if (\n"
                "            isinstance(h.type, ast.Tuple)\n"
                "            and len(h.type.elts) >= 2\n"
                "        ):\n"
                "            ok = True\n"
                "            break\n"
                "    if ok:\n"
                "        break\n"
                "assert ok, (\n"
                "    'test_error_types must include a try block that '\n"
                "    'catches multiple exception types — either via a tuple '\n"
                "    '(except (E1, E2):) or multiple except handlers on the '\n"
                "    'same try'\n"
                ")\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="garden_operations(0) raises ValueError",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_different_errors import garden_operations\n"
                "try:\n"
                "    garden_operations(0)\n"
                "except ValueError:\n"
                "    print('OK')\n"
                "else:\n"
                "    raise AssertionError('op 0 must raise ValueError')\n"
            ),
        ),
        InlineCheck(
            label="garden_operations(1) raises ZeroDivisionError",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_different_errors import garden_operations\n"
                "try:\n"
                "    garden_operations(1)\n"
                "except ZeroDivisionError:\n"
                "    print('OK')\n"
                "else:\n"
                "    raise AssertionError('op 1 must raise ZeroDivisionError')\n"
            ),
        ),
        InlineCheck(
            label="garden_operations(2) raises FileNotFoundError",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_different_errors import garden_operations\n"
                "try:\n"
                "    garden_operations(2)\n"
                "except FileNotFoundError:\n"
                "    print('OK')\n"
                "else:\n"
                "    raise AssertionError('op 2 must raise FileNotFoundError')\n"
            ),
        ),
        InlineCheck(
            label="garden_operations(3) raises TypeError",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_different_errors import garden_operations\n"
                "try:\n"
                "    garden_operations(3)\n"
                "except TypeError:\n"
                "    print('OK')\n"
                "else:\n"
                "    raise AssertionError('op 3 must raise TypeError')\n"
            ),
        ),
        InlineCheck(
            label="garden_operations(4) does not raise",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_different_errors import garden_operations\n"
                "garden_operations(4)\n"
                "print('OK')\n"
            ),
        ),
        ScriptCheck(
            label="script prints all four error types",
            file="ft_different_errors.py",
            expected_contains=(
                "=== Garden Error Types Demo ===",
                "ValueError",
                "ZeroDivisionError",
                "FileNotFoundError",
                "TypeError",
                "All error types tested successfully",
            ),
        ),
    ),
    explain=(
        "garden_operations(n) is faulty by design: 0→ValueError, "
        "1→ZeroDivisionError, 2→FileNotFoundError, 3→TypeError, 4+→no error. "
        "test_error_types must catch multiple types in one except block."
    ),
)

_EX3 = Exercise(
    module_id="02", id="ex3",
    filenames=("ft_custom_errors.py",),
    authorized=("print", "super"),
    checks=(
        _struct_pipeline(
            "ft_custom_errors.py",
            classes=("GardenError", "PlantError", "WaterError"),
            label="GardenError + PlantError + WaterError",
        ),
        AuthorizedCheck(
            "ft_custom_errors.py", ("print", "super"),
            allow_method_calls=True,
        ),
        InlineCheck(
            label=(
                "GardenError(Exception), PlantError(GardenError), "
                "WaterError(GardenError)"
            ),
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_custom_errors import GardenError, PlantError, WaterError\n"
                "assert issubclass(GardenError, Exception)\n"
                "assert issubclass(PlantError, GardenError)\n"
                "assert issubclass(WaterError, GardenError)\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="custom errors expose a non-empty default message",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_custom_errors import GardenError, PlantError, WaterError\n"
                "for cls in (GardenError, PlantError, WaterError):\n"
                "    msg = str(cls())\n"
                "    assert msg, (\n"
                "        f'{cls.__name__}() must have a default message'\n"
                "    )\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="catching GardenError catches PlantError and WaterError",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_custom_errors import GardenError, PlantError, WaterError\n"
                "for sub in (PlantError, WaterError):\n"
                "    try:\n"
                "        raise sub('boom')\n"
                "    except GardenError:\n"
                "        pass\n"
                "    else:\n"
                "        raise AssertionError(\n"
                "            f'{sub.__name__} not caught by GardenError'\n"
                "        )\n"
                "print('OK')\n"
            ),
        ),
        ScriptCheck(
            label="script demonstrates custom errors",
            file="ft_custom_errors.py",
            expected_contains=(
                "=== Custom Garden Errors Demo ===",
                "PlantError",
                "WaterError",
                "GardenError",
                "All custom error types work correctly",
            ),
        ),
    ),
    explain=(
        "Three custom exceptions: GardenError(Exception), "
        "PlantError(GardenError), WaterError(GardenError). Each has a "
        "default message. Catching GardenError catches all subclasses."
    ),
)

_EX4 = Exercise(
    module_id="02", id="ex4",
    filenames=("ft_finally_block.py",),
    authorized=("print",),
    checks=(
        _struct_pipeline(
            "ft_finally_block.py",
            functions=("water_plant", "test_watering_system"),
            label="water_plant + test_watering_system",
        ),
        AuthorizedCheck(
            "ft_finally_block.py", ("print",),
            allow_method_calls=True,
        ),
        InlineCheck(
            label="water_plant('Tomato') succeeds (capitalized)",
            code=(
                "import io, sys\n"
                "from contextlib import redirect_stdout\n"
                "sys.path.insert(0, '.')\n"
                "from ft_finally_block import water_plant\n"
                "with redirect_stdout(io.StringIO()):\n"
                "    water_plant('Tomato')\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="water_plant('lettuce') raises (not capitalized)",
            code=(
                "import io, sys\n"
                "from contextlib import redirect_stdout\n"
                "sys.path.insert(0, '.')\n"
                "from ft_finally_block import water_plant\n"
                "with redirect_stdout(io.StringIO()):\n"
                "    try:\n"
                "        water_plant('lettuce')\n"
                "    except Exception:\n"
                "        pass\n"
                "    else:\n"
                "        raise AssertionError(\n"
                "            \"water_plant('lettuce') must raise\"\n"
                "        )\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label=(
                "test_watering_system has try/except/finally with return "
                "on error"
            ),
            code=(
                _ast_helper("ft_finally_block.py")
                + "fn = _fn('test_watering_system')\n"
                "assert fn is not None, 'test_watering_system missing'\n"
                "tries = [n for n in ast.walk(fn) if isinstance(n, ast.Try)]\n"
                "assert tries, (\n"
                "    'test_watering_system must use try/except/finally'\n"
                ")\n"
                "has_finally = any(tr.finalbody for tr in tries)\n"
                "assert has_finally, (\n"
                "    'test_watering_system must include a finally block '\n"
                "    'to always close the watering system'\n"
                ")\n"
                "has_return_in_except = any(\n"
                "    isinstance(s, ast.Return)\n"
                "    for tr in tries\n"
                "    for h in tr.handlers\n"
                "    for s in ast.walk(h)\n"
                ")\n"
                "assert has_return_in_except, (\n"
                "    'test_watering_system must return from an except '\n"
                "    'handler when an error occurs (stop tests, return '\n"
                "    'to main)'\n"
                ")\n"
                "print('OK')\n"
            ),
        ),
        ScriptCheck(
            label="script prints watering banner and cleanup runs",
            file="ft_finally_block.py",
            expected_contains=(
                "=== Garden Watering System ===",
                "Opening watering system",
                "Closing watering system",
                "Cleanup always happens",
            ),
        ),
    ),
    explain=(
        "water_plant(plant_name) succeeds on capitalized names, raises "
        "PlantError otherwise. test_watering_system must use try/except "
        "and finally so the system always closes, and return from except "
        "immediately on error."
    ),
)


MODULE_02 = Module(
    id="02",
    title="Garden Guardian — data engineering for smart agriculture",
    exercises=(_EX0, _EX1, _EX2, _EX3, _EX4),
)
