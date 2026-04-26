from pythonette.checks import (
    AuthorizedCheck,
    CallCheck,
    OfficialMainCheck,
    SignatureCheck,
    StructureCheck,
)
from pythonette.subjects.registry import Exercise, Module


_EX0 = Exercise(
    module_id="00", id="ex0",
    filenames=("ft_hello_garden.py",),
    authorized=("print",),
    checks=(
        StructureCheck("ft_hello_garden.py", functions=("ft_hello_garden",)),
        SignatureCheck("ft_hello_garden", "ft_hello_garden"),
        AuthorizedCheck(
            "ft_hello_garden.py", ("print",), allow_method_calls=False,
        ),
        CallCheck(
            label="prints welcome",
            module="ft_hello_garden", function="ft_hello_garden",
            expected_stdout="Hello, Garden Community!",
        ),
        OfficialMainCheck(
            choice="0", expected_pieces=("Hello, Garden Community!",),
        ),
    ),
    explain=(
        "ft_hello_garden() must print exactly 'Hello, Garden Community!'. "
        "No prompts, no input — just one print."
    ),
)

_EX1 = Exercise(
    module_id="00", id="ex1",
    filenames=("ft_garden_name.py",),
    authorized=("input", "print"),
    checks=(
        StructureCheck("ft_garden_name.py", functions=("ft_garden_name",)),
        SignatureCheck("ft_garden_name", "ft_garden_name"),
        AuthorizedCheck(
            "ft_garden_name.py", ("input", "print"),
            allow_method_calls=False,
        ),
        CallCheck(
            label="exact stdout — Community Garden",
            module="ft_garden_name", function="ft_garden_name",
            stdin="Community Garden\n",
            expected_stdout=(
                "Enter garden name: Garden: Community Garden\n"
                "Status: Growing well!"
            ),
        ),
        CallCheck(
            label="exact stdout — Herb Patch",
            module="ft_garden_name", function="ft_garden_name",
            stdin="Herb Patch\n",
            expected_stdout=(
                "Enter garden name: Garden: Herb Patch\n"
                "Status: Growing well!"
            ),
        ),
        OfficialMainCheck(
            choice="1", inputs=("My Garden",),
            expected_pieces=("Garden: My Garden", "Status: Growing well!"),
        ),
    ),
    explain=(
        "Read a garden name with input('Enter garden name: '), then print "
        "'Garden: <name>' and 'Status: Growing well!'."
    ),
)

_EX2 = Exercise(
    module_id="00", id="ex2",
    filenames=("ft_plot_area.py",),
    authorized=("input", "int", "print"),
    checks=(
        StructureCheck("ft_plot_area.py", functions=("ft_plot_area",)),
        SignatureCheck("ft_plot_area", "ft_plot_area"),
        AuthorizedCheck(
            "ft_plot_area.py", ("input", "int", "print"),
            allow_method_calls=False,
        ),
        CallCheck(
            label="5x3 → 15", module="ft_plot_area", function="ft_plot_area",
            stdin="5\n3\n",
            expected_stdout="Enter length: Enter width: Plot area: 15",
        ),
        CallCheck(
            label="10x10 → 100", module="ft_plot_area", function="ft_plot_area",
            stdin="10\n10\n",
            expected_stdout="Enter length: Enter width: Plot area: 100",
        ),
        CallCheck(
            label="0x7 → 0", module="ft_plot_area", function="ft_plot_area",
            stdin="0\n7\n",
            expected_stdout="Enter length: Enter width: Plot area: 0",
        ),
        OfficialMainCheck(
            choice="2", inputs=("5", "3"),
            expected_pieces=("Plot area: 15",),
        ),
    ),
    explain=(
        "Prompts: 'Enter length: ', 'Enter width: '. "
        "Output: 'Plot area: <length*width>'."
    ),
)

_EX3 = Exercise(
    module_id="00", id="ex3",
    filenames=("ft_harvest_total.py",),
    authorized=("input", "int", "print"),
    checks=(
        StructureCheck(
            "ft_harvest_total.py", functions=("ft_harvest_total",),
        ),
        SignatureCheck("ft_harvest_total", "ft_harvest_total"),
        AuthorizedCheck(
            "ft_harvest_total.py", ("input", "int", "print"),
            allow_method_calls=False,
        ),
        CallCheck(
            label="5+8+3 → 16",
            module="ft_harvest_total", function="ft_harvest_total",
            stdin="5\n8\n3\n",
            expected_stdout=(
                "Day 1 harvest: Day 2 harvest: Day 3 harvest: "
                "Total harvest: 16"
            ),
        ),
        CallCheck(
            label="0+0+0 → 0",
            module="ft_harvest_total", function="ft_harvest_total",
            stdin="0\n0\n0\n",
            expected_stdout=(
                "Day 1 harvest: Day 2 harvest: Day 3 harvest: "
                "Total harvest: 0"
            ),
        ),
        OfficialMainCheck(
            choice="3", inputs=("5", "8", "3"),
            expected_pieces=("Total harvest: 16",),
        ),
    ),
    explain=(
        "Prompts: 'Day 1 harvest: ', 'Day 2 harvest: ', 'Day 3 harvest: '. "
        "Final: 'Total harvest: <sum>'."
    ),
)

_EX4 = Exercise(
    module_id="00", id="ex4",
    filenames=("ft_plant_age.py",),
    authorized=("input", "int", "print"),
    checks=(
        StructureCheck("ft_plant_age.py", functions=("ft_plant_age",)),
        SignatureCheck("ft_plant_age", "ft_plant_age"),
        AuthorizedCheck(
            "ft_plant_age.py", ("input", "int", "print"),
            allow_method_calls=False,
        ),
        CallCheck(
            label="age 75 → ready",
            module="ft_plant_age", function="ft_plant_age",
            stdin="75\n",
            expected_stdout="Enter plant age in days: Plant is ready to harvest!",
        ),
        CallCheck(
            label="age 45 → not ready",
            module="ft_plant_age", function="ft_plant_age",
            stdin="45\n",
            expected_stdout=(
                "Enter plant age in days: Plant needs more time to grow."
            ),
        ),
        CallCheck(
            label="age 60 boundary → not ready",
            module="ft_plant_age", function="ft_plant_age",
            stdin="60\n",
            expected_stdout=(
                "Enter plant age in days: Plant needs more time to grow."
            ),
        ),
        CallCheck(
            label="age 61 boundary → ready",
            module="ft_plant_age", function="ft_plant_age",
            stdin="61\n",
            expected_stdout="Enter plant age in days: Plant is ready to harvest!",
        ),
        OfficialMainCheck(
            choice="4", inputs=("75",),
            expected_pieces=("Plant is ready to harvest!",),
        ),
    ),
    explain=(
        "Strict comparison: only ages >60 are ready. The boundary 60 is NOT "
        "ready. Watch the dot on 'needs more time to grow.'."
    ),
)

_EX5 = Exercise(
    module_id="00", id="ex5",
    filenames=("ft_water_reminder.py",),
    authorized=("input", "int", "print"),
    checks=(
        StructureCheck(
            "ft_water_reminder.py", functions=("ft_water_reminder",),
        ),
        SignatureCheck("ft_water_reminder", "ft_water_reminder"),
        AuthorizedCheck(
            "ft_water_reminder.py", ("input", "int", "print"),
            allow_method_calls=False,
        ),
        CallCheck(
            label="4 days → water",
            module="ft_water_reminder", function="ft_water_reminder",
            stdin="4\n",
            expected_stdout="Days since last watering: Water the plants!",
        ),
        CallCheck(
            label="1 day → fine",
            module="ft_water_reminder", function="ft_water_reminder",
            stdin="1\n",
            expected_stdout="Days since last watering: Plants are fine",
        ),
        CallCheck(
            label="2 days boundary → fine",
            module="ft_water_reminder", function="ft_water_reminder",
            stdin="2\n",
            expected_stdout="Days since last watering: Plants are fine",
        ),
        CallCheck(
            label="3 days boundary → water",
            module="ft_water_reminder", function="ft_water_reminder",
            stdin="3\n",
            expected_stdout="Days since last watering: Water the plants!",
        ),
        OfficialMainCheck(
            choice="5", inputs=("4",),
            expected_pieces=("Water the plants!",),
        ),
    ),
    explain="Strictly >2 → water. Exactly 2 → fine.",
)

_EX6 = Exercise(
    module_id="00", id="ex6",
    filenames=(
        "ft_count_harvest_iterative.py",
        "ft_count_harvest_recursive.py",
    ),
    authorized=("input", "int", "print", "range"),
    checks=(
        StructureCheck(
            "ft_count_harvest_iterative.py",
            functions=("ft_count_harvest_iterative",),
            label="iterative: only ft_count_harvest_iterative",
        ),
        StructureCheck(
            "ft_count_harvest_recursive.py",
            functions=("ft_count_harvest_recursive",),
            allow_extra_functions=True,
            label="recursive: ft_count_harvest_recursive present, helpers ok",
        ),
        SignatureCheck(
            "ft_count_harvest_iterative", "ft_count_harvest_iterative",
        ),
        SignatureCheck(
            "ft_count_harvest_recursive", "ft_count_harvest_recursive",
            require_callable_no_args=True,
            label=(
                "signature: ft_count_harvest_recursive() callable with no "
                "arguments (defaults allowed)"
            ),
        ),
        AuthorizedCheck(
            "ft_count_harvest_iterative.py",
            ("input", "int", "print", "range"),
            allow_method_calls=False,
        ),
        AuthorizedCheck(
            "ft_count_harvest_recursive.py",
            ("input", "int", "print", "range"),
            allow_method_calls=False,
        ),
        CallCheck(
            label="iterative — exact output for 3 days",
            module="ft_count_harvest_iterative",
            function="ft_count_harvest_iterative",
            stdin="3\n",
            expected_stdout=(
                "Days until harvest: Day 1\nDay 2\nDay 3\nHarvest time!"
            ),
        ),
        CallCheck(
            label="recursive — exact output for 3 days",
            module="ft_count_harvest_recursive",
            function="ft_count_harvest_recursive",
            stdin="3\n",
            expected_stdout=(
                "Days until harvest: Day 1\nDay 2\nDay 3\nHarvest time!"
            ),
        ),
        CallCheck(
            label="iterative — exact output for 5 days",
            module="ft_count_harvest_iterative",
            function="ft_count_harvest_iterative",
            stdin="5\n",
            expected_stdout=(
                "Days until harvest: "
                "Day 1\nDay 2\nDay 3\nDay 4\nDay 5\nHarvest time!"
            ),
        ),
        CallCheck(
            label="recursive — exact output for 5 days",
            module="ft_count_harvest_recursive",
            function="ft_count_harvest_recursive",
            stdin="5\n",
            expected_stdout=(
                "Days until harvest: "
                "Day 1\nDay 2\nDay 3\nDay 4\nDay 5\nHarvest time!"
            ),
        ),
        OfficialMainCheck(
            choice="6", inputs=("3", "3"),
            expected_pieces=("Day 1", "Day 2", "Day 3", "Harvest time!"),
        ),
    ),
    explain=(
        "Print 'Days until harvest: ' then 'Day 1' .. 'Day N' (one per "
        "line) then 'Harvest time!'. Iterative: only the requested function. "
        "Recursive: helpers / default args / nested function all allowed."
    ),
)

_EX7 = Exercise(
    module_id="00", id="ex7",
    filenames=("ft_seed_inventory.py",),
    authorized=("print",),
    checks=(
        StructureCheck(
            "ft_seed_inventory.py", functions=("ft_seed_inventory",),
        ),
        SignatureCheck(
            "ft_seed_inventory", "ft_seed_inventory",
            expected_params=("seed_type", "quantity", "unit"),
            param_annotations={
                "seed_type": "str",
                "quantity": "int",
                "unit": "str",
            },
            return_annotation="None",
            label=(
                "signature: ft_seed_inventory(seed_type: str, "
                "quantity: int, unit: str) -> None"
            ),
        ),
        AuthorizedCheck(
            "ft_seed_inventory.py", ("print",),
            allow_method_calls=True,
        ),
        CallCheck(
            label="packets",
            module="ft_seed_inventory", function="ft_seed_inventory",
            args_repr="('tomato', 15, 'packets')",
            expected_stdout="Tomato seeds: 15 packets available",
        ),
        CallCheck(
            label="grams",
            module="ft_seed_inventory", function="ft_seed_inventory",
            args_repr="('carrot', 8, 'grams')",
            expected_stdout="Carrot seeds: 8 grams total",
        ),
        CallCheck(
            label="area",
            module="ft_seed_inventory", function="ft_seed_inventory",
            args_repr="('lettuce', 12, 'area')",
            expected_stdout="Lettuce seeds: covers 12 square meters",
        ),
        CallCheck(
            label="unknown unit",
            module="ft_seed_inventory", function="ft_seed_inventory",
            args_repr="('basil', 5, 'liters')",
            expected_stdout="Unknown unit type",
        ),
        CallCheck(
            label="does not call input()",
            module="ft_seed_inventory", function="ft_seed_inventory",
            args_repr="('tomato', 15, 'packets')",
            forbid_input=True,
            expected_stdout="Tomato seeds: 15 packets available",
        ),
        OfficialMainCheck(
            choice="7",
            expected_pieces=(
                "Tomato seeds: 15 packets available",
                "Carrot seeds: 8 grams total",
                "Lettuce seeds: covers 12 square meters",
                "Unknown unit type",
            ),
        ),
    ),
    explain=(
        "Strict signature: ft_seed_inventory(seed_type: str, quantity: "
        "int, unit: str) -> None. Capitalize seed_type. Units 'packets', "
        "'grams', 'area' format their own line; anything else prints "
        "exactly 'Unknown unit type'."
    ),
)


MODULE_00 = Module(
    id="00",
    title="Growing Code — Python fundamentals through garden data",
    exercises=(_EX0, _EX1, _EX2, _EX3, _EX4, _EX5, _EX6, _EX7),
)
