from pythonette.subjects.registry import Exercise, Module, TestCase


def _harness(module: str, body: str) -> str:
    return (
        "import sys\n"
        "sys.path.insert(0, '.')\n"
        f"from {module} import *  # noqa: F401,F403\n"
        f"{body}\n"
    )


_EX00 = Exercise(
    module_id="00",
    id="ex00",
    filenames=("ft_hello_garden.py",),
    authorized=("print",),
    cases=(
        TestCase(
            name="prints welcome",
            harness=_harness("ft_hello_garden", "ft_hello_garden()"),
            expected_stdout="Hello, Garden Community!",
        ),
    ),
    explain=(
        "ft_hello_garden() must print exactly 'Hello, Garden Community!'. "
        "No prompts, no input — just one print."
    ),
)

_EX01 = Exercise(
    module_id="00",
    id="ex01",
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
    ),
    explain=(
        "Read a garden name with input(), then print 'Garden: <name>' on one "
        "line and 'Status: Growing well!' on the next. The status string is "
        "fixed."
    ),
)

_EX02 = Exercise(
    module_id="00",
    id="ex02",
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
    ),
    explain=(
        "Read length then width as ints, print 'Plot area: <length*width>'."
    ),
)

_EX03 = Exercise(
    module_id="00",
    id="ex03",
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
    ),
    explain="Read three int harvests and print 'Total harvest: <sum>'.",
)

_EX04 = Exercise(
    module_id="00",
    id="ex04",
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
    ),
    explain=(
        "Strict comparison: only ages >60 are ready. The boundary 60 is NOT "
        "ready. Watch the dot at the end of the 'needs more time' message."
    ),
)

_EX05 = Exercise(
    module_id="00",
    id="ex05",
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
    ),
    explain="Strictly more than 2 days → water. Exactly 2 → still fine.",
)

_EX06 = Exercise(
    module_id="00",
    id="ex06",
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
    ),
    explain=(
        "Print Day 1 .. Day N (one per line) then 'Harvest time!'. The "
        "iterative and recursive versions must produce identical output."
    ),
)

_EX07 = Exercise(
    module_id="00",
    id="ex07",
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
