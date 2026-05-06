from pythonette.checks import (
    AssertCheck,
    AuthorizedCheck,
    Eq,
    FunctionTryFinallyReturnCheck,
    FunctionTryHandlersCheck,
    NoNodeTypesCheck,
    NotRaises,
    Raises,
    RequireNodeTypesCheck,
    ScriptCheck,
    StructureCheck,
    Subclass,
    Truthy,
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
        NoNodeTypesCheck(
            label="input_temperature() must not contain try/except",
            scope=("ft_first_exception.py",),
            node_types=("Try",),
            inside_function="input_temperature",
            reason=(
                "input_temperature must not contain try/except — "
                "let it fail and catch in test_temperature"
            ),
        ),
        RequireNodeTypesCheck(
            label="test_temperature() catches with try/except",
            scope=("ft_first_exception.py",),
            node_types=("Try",),
            inside_function="test_temperature",
            reason=(
                "test_temperature must catch input_temperature failures "
                "with try/except"
            ),
        ),
        AssertCheck(
            label="input_temperature('25') == 25",
            setup="from ft_first_exception import input_temperature",
            assertions=(Eq("input_temperature('25')", 25),),
        ),
        AssertCheck(
            label="input_temperature('abc') raises (caught at test level)",
            setup="from ft_first_exception import input_temperature",
            assertions=(
                Raises(
                    "input_temperature('abc')",
                    message="expected exception on abc input",
                ),
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
        AssertCheck(
            label="input_temperature('25') == 25 (in range)",
            setup="from ft_raise_exception import input_temperature",
            assertions=(Eq("input_temperature('25')", 25),),
        ),
        AssertCheck(
            label="boundaries 0 and 40 are valid",
            setup="from ft_raise_exception import input_temperature",
            assertions=(
                Eq("input_temperature('0')", 0),
                Eq("input_temperature('40')", 40),
            ),
        ),
        AssertCheck(
            label="input_temperature('100') raises (>40)",
            setup="from ft_raise_exception import input_temperature",
            assertions=(
                Raises(
                    "input_temperature('100')",
                    message="100 must raise (max 40)",
                ),
            ),
        ),
        AssertCheck(
            label="input_temperature('-50') raises (<0)",
            setup="from ft_raise_exception import input_temperature",
            assertions=(
                Raises(
                    "input_temperature('-50')",
                    message="-50 must raise (min 0)",
                ),
            ),
        ),
        AssertCheck(
            label="input_temperature('abc') raises",
            setup="from ft_raise_exception import input_temperature",
            assertions=(
                Raises(
                    "input_temperature('abc')",
                    message="abc must raise",
                ),
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
        NoNodeTypesCheck(
            label="garden_operations triggers real faults (no manual raise)",
            scope=("ft_different_errors.py",),
            node_types=("Raise",),
            inside_function="garden_operations",
            reason=(
                "garden_operations must trigger real faulty code "
                "(int('abc'), 1/0, open(missing), str+int), not "
                "manual raise"
            ),
        ),
        FunctionTryHandlersCheck(
            label="test_error_types catches multiple error types in one try",
            file="ft_different_errors.py",
            function="test_error_types",
            min_handlers=2,
            reason=(
                "test_error_types must include a try block that catches "
                "multiple exception types — either via a tuple "
                "(except (E1, E2):) or multiple except handlers"
            ),
        ),
        AssertCheck(
            label="garden_operations(0) raises ValueError",
            setup="from ft_different_errors import garden_operations",
            assertions=(
                Raises(
                    "garden_operations(0)",
                    exception_types=("ValueError",),
                    message="op 0 must raise ValueError",
                ),
            ),
        ),
        AssertCheck(
            label="garden_operations(1) raises ZeroDivisionError",
            setup="from ft_different_errors import garden_operations",
            assertions=(
                Raises(
                    "garden_operations(1)",
                    exception_types=("ZeroDivisionError",),
                    message="op 1 must raise ZeroDivisionError",
                ),
            ),
        ),
        AssertCheck(
            label="garden_operations(2) raises FileNotFoundError",
            setup="from ft_different_errors import garden_operations",
            assertions=(
                Raises(
                    "garden_operations(2)",
                    exception_types=("FileNotFoundError",),
                    message="op 2 must raise FileNotFoundError",
                ),
            ),
        ),
        AssertCheck(
            label="garden_operations(3) raises TypeError",
            setup="from ft_different_errors import garden_operations",
            assertions=(
                Raises(
                    "garden_operations(3)",
                    exception_types=("TypeError",),
                    message="op 3 must raise TypeError",
                ),
            ),
        ),
        AssertCheck(
            label="garden_operations(4) does not raise",
            setup="from ft_different_errors import garden_operations",
            assertions=(NotRaises("garden_operations(4)"),),
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
        AssertCheck(
            label=(
                "GardenError(Exception), PlantError(GardenError), "
                "WaterError(GardenError)"
            ),
            setup=(
                "from ft_custom_errors import "
                "GardenError, PlantError, WaterError"
            ),
            assertions=(
                Subclass("GardenError", "Exception"),
                Subclass("PlantError", "GardenError"),
                Subclass("WaterError", "GardenError"),
            ),
        ),
        AssertCheck(
            label="custom errors expose a non-empty default message",
            setup=(
                "from ft_custom_errors import "
                "GardenError, PlantError, WaterError"
            ),
            assertions=(
                Truthy(
                    "str(GardenError())",
                    message="GardenError() must have a default message",
                ),
                Truthy(
                    "str(PlantError())",
                    message="PlantError() must have a default message",
                ),
                Truthy(
                    "str(WaterError())",
                    message="WaterError() must have a default message",
                ),
            ),
        ),
        AssertCheck(
            label="catching GardenError catches PlantError and WaterError",
            setup=(
                "from ft_custom_errors import "
                "GardenError, PlantError, WaterError"
            ),
            assertions=(
                Raises(
                    "raise PlantError('boom')",
                    exception_types=("GardenError",),
                    message="PlantError not caught by GardenError",
                ),
                Raises(
                    "raise WaterError('boom')",
                    exception_types=("GardenError",),
                    message="WaterError not caught by GardenError",
                ),
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
        AssertCheck(
            label="water_plant('Tomato') succeeds (capitalized)",
            setup="from ft_finally_block import water_plant",
            quiet=True,
            assertions=(NotRaises("water_plant('Tomato')"),),
        ),
        AssertCheck(
            label="water_plant('lettuce') raises (not capitalized)",
            setup="from ft_finally_block import water_plant",
            quiet=True,
            assertions=(
                Raises(
                    "water_plant('lettuce')",
                    message="water_plant('lettuce') must raise",
                ),
            ),
        ),
        FunctionTryFinallyReturnCheck(
            label=(
                "test_watering_system has try/except/finally with return "
                "on error"
            ),
            file="ft_finally_block.py",
            function="test_watering_system",
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
