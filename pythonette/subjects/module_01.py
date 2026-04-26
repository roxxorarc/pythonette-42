from pythonette.checks import (
    AuthorizedCheck,
    InlineCheck,
    MethodArityCheck,
    MethodSignatureCheck,
    ScriptCheck,
    StructureCheck,
)
from pythonette.subjects.registry import Exercise, Module


def _struct_oop(
    file: str,
    classes: tuple[str, ...] = (),
    functions: tuple[str, ...] = (),
    *,
    require_main_guard: bool = False,
    label: str | None = None,
) -> StructureCheck:
    """Module-01-flavoured StructureCheck: imports / top-level assigns /
    main guard are typically all allowed in OOP exercises."""
    return StructureCheck(
        file=file,
        classes=classes,
        functions=functions,
        allow_extra_classes=True,
        allow_extra_functions=True,
        allow_imports=True,
        allow_top_level_assigns=True,
        allow_main_guard=True,
        require_main_guard=require_main_guard,
        label=label,
    )


_EX0 = Exercise(
    module_id="01", id="ex0",
    filenames=("ft_garden_intro.py",),
    authorized=("print",),
    checks=(
        _struct_oop(
            "ft_garden_intro.py",
            require_main_guard=True,
            label="requires if __name__ == '__main__' guard",
        ),
        AuthorizedCheck(
            "ft_garden_intro.py", ("print",), allow_method_calls=False,
        ),
        ScriptCheck(    
            label="runs as __main__ with full banner",
            file="ft_garden_intro.py",
            expected_contains=(
                "=== Welcome to My Garden ===",
                "Plant:",
                "Height:",
                "Age:",
                "=== End of Program ===",
            ),
        ),
    ),
    explain=(
        "Use the if __name__ == '__main__' guard, store name/height/age in "
        "variables, and print the welcome banner, plant info, and end "
        "banner."
    ),
)

_EX1 = Exercise(
    module_id="01", id="ex1",
    filenames=("ft_garden_data.py",),
    authorized=("print",),
    checks=(
        _struct_oop(
            "ft_garden_data.py", classes=("Plant",),
            require_main_guard=True,
            label="Plant class + __main__ guard",
        ),
        InlineCheck(
            label="Plant class exposes show()",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_garden_data import Plant\n"
                "assert hasattr(Plant, 'show'), 'Plant.show missing'\n"
                "print('OK')\n"
            ),
        ),
        MethodSignatureCheck(
            "ft_garden_data", "Plant", "show", ("self",),
        ),
        AuthorizedCheck("ft_garden_data.py", ("print",)),
        ScriptCheck(
            label="script prints the registry banner",
            file="ft_garden_data.py",
            expected_contains=("=== Garden Plant Registry ===",),
        ),
    ),
    explain=(
        "Define a Plant class with name/height/age attributes and a show() "
        "method. Under __main__: build at least 3 plants and print the "
        "'Garden Plant Registry' banner."
    ),
)

_EX2 = Exercise(
    module_id="01", id="ex2",
    filenames=("ft_plant_growth.py",),
    authorized=("print", "range", "round"),
    checks=(
        _struct_oop(
            "ft_plant_growth.py", classes=("Plant",),
            require_main_guard=True,
            label="Plant class + __main__ guard",
        ),
        InlineCheck(
            label="Plant exposes grow / age",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_plant_growth import Plant\n"
                "assert hasattr(Plant, 'grow'), 'Plant.grow missing'\n"
                "assert hasattr(Plant, 'age'), 'Plant.age missing'\n"
                "print('OK')\n"
            ),
        ),
        MethodArityCheck("ft_plant_growth", "Plant", "grow", 0),
        MethodArityCheck("ft_plant_growth", "Plant", "age", 0),
        AuthorizedCheck("ft_plant_growth.py", ("print", "range", "round")),
        ScriptCheck(
            label="script simulates a 7-day week",
            file="ft_plant_growth.py",
            expected_contains=(
                "=== Garden Plant Growth ===",
                "=== Day 1 ===",
                "=== Day 7 ===",
                "Growth this week:",
            ),
        ),
    ),
    explain=(
        "Reuse Plant and add grow() (height) and age() methods. The script "
        "simulates 7 days and ends with a 'Growth this week' summary."
    ),
)

_EX3 = Exercise(
    module_id="01", id="ex3",
    filenames=("ft_plant_factory.py",),
    authorized=("print", "range", "round"),
    checks=(
        _struct_oop(
            "ft_plant_factory.py", classes=("Plant",),
            require_main_guard=True,
            label="Plant class + __main__ guard",
        ),
        MethodArityCheck("ft_plant_factory", "Plant", "__init__", 3),
        InlineCheck(
            label="constructor accepts (name, height, age) positionally",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_plant_factory import Plant\n"
                "p = Plant('Rose', 25.0, 30)\n"
                "assert p is not None\n"
                "print('OK')\n"
            ),
        ),
        AuthorizedCheck("ft_plant_factory.py", ("print", "range", "round")),
        ScriptCheck(
            label="script prints factory output",
            file="ft_plant_factory.py",
            expected_contains=("=== Plant Factory Output ===", "Created:"),
        ),
    ),
    explain=(
        "Add __init__(self, name, height, age). The script must instantiate "
        "at least 5 distinct plants directly via the constructor."
    ),
)

_EX4 = Exercise(
    module_id="01", id="ex4",
    filenames=("ft_garden_security.py",),
    authorized=("print", "range", "round"),
    checks=(
        _struct_oop(
            "ft_garden_security.py", classes=("Plant",),
            require_main_guard=True,
            label="Plant class + __main__ guard",
        ),
        MethodArityCheck("ft_garden_security", "Plant", "set_height", 1),
        MethodArityCheck("ft_garden_security", "Plant", "set_age", 1),
        MethodArityCheck("ft_garden_security", "Plant", "get_height", 0),
        MethodArityCheck("ft_garden_security", "Plant", "get_age", 0),
        InlineCheck(
            label="setters reject negative values",
            code=(
                "import io, sys\n"
                "from contextlib import redirect_stdout\n"
                "sys.path.insert(0, '.')\n"
                "from ft_garden_security import Plant\n"
                "with redirect_stdout(io.StringIO()):\n"
                "    p = Plant('Rose', 15.0, 10)\n"
                "    p.set_height(25); p.set_age(30)\n"
                "    h_ok, a_ok = p.get_height(), p.get_age()\n"
                "    p.set_height(-5); p.set_age(-3)\n"
                "assert p.get_height() == h_ok, 'neg height accepted'\n"
                "assert p.get_age() == a_ok, 'neg age accepted'\n"
                "print('OK')\n"
            ),
        ),
        AuthorizedCheck(
            "ft_garden_security.py", ("print", "range", "round"),
        ),
        ScriptCheck(
            label="script prints the security banner and a rejection",
            file="ft_garden_security.py",
            expected_contains=(
                "=== Garden Security System ===", "rejected",
            ),
        ),
    ),
    explain=(
        "Validated setters/getters. Negative values rejected with an error "
        "message; previous value preserved."
    ),
)

_EX5 = Exercise(
    module_id="01", id="ex5",
    filenames=("ft_plant_types.py",),
    authorized=("super", "print", "range", "round"),
    checks=(
        _struct_oop(
            "ft_plant_types.py",
            classes=("Plant", "Flower", "Tree", "Vegetable"),
            require_main_guard=True,
            label="Plant/Flower/Tree/Vegetable + __main__ guard",
        ),
        InlineCheck(
            label="Flower / Tree / Vegetable inherit Plant",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_plant_types import Plant, Flower, Tree, Vegetable\n"
                "assert issubclass(Flower, Plant)\n"
                "assert issubclass(Tree, Plant)\n"
                "assert issubclass(Vegetable, Plant)\n"
                "print('OK')\n"
            ),
        ),
        MethodArityCheck("ft_plant_types", "Flower", "bloom", 0),
        MethodArityCheck("ft_plant_types", "Tree", "produce_shade", 0),
        InlineCheck(
            label="Flower(name, height, age, color) accepted",
            code=(
                "import io, sys\n"
                "from contextlib import redirect_stdout\n"
                "sys.path.insert(0, '.')\n"
                "from ft_plant_types import Flower\n"
                "with redirect_stdout(io.StringIO()):\n"
                "    f = Flower('Rose', 15.0, 10, 'red')\n"
                "assert f is not None\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="Tree(name, height, age, trunk_diameter) accepted",
            code=(
                "import io, sys\n"
                "from contextlib import redirect_stdout\n"
                "sys.path.insert(0, '.')\n"
                "from ft_plant_types import Tree\n"
                "with redirect_stdout(io.StringIO()):\n"
                "    t = Tree('Oak', 200.0, 365, 5.0)\n"
                "assert t is not None\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="Vegetable(name, height, age, harvest_season, nutritional_value) accepted",
            code=(
                "import io, sys\n"
                "from contextlib import redirect_stdout\n"
                "sys.path.insert(0, '.')\n"
                "from ft_plant_types import Vegetable\n"
                "with redirect_stdout(io.StringIO()):\n"
                "    v = Vegetable('Tomato', 5.0, 10, 'April', 0)\n"
                "assert v is not None\n"
                "print('OK')\n"
            ),
        ),
        AuthorizedCheck(
            "ft_plant_types.py", ("super", "print", "range", "round"),
        ),
        ScriptCheck(
            label="script displays per-type details",
            file="ft_plant_types.py",
            expected_contains=(
                "=== Garden Plant Types ===",
                "=== Flower",
                "=== Tree",
                "=== Vegetable",
                "Color:",
                "Trunk diameter:",
                "Harvest season:",
                "Nutritional value:",
            ),
        ),
    ),
    explain=(
        "Flower(color), Tree(trunk_diameter), Vegetable(harvest_season, "
        "nutritional_value) inherit Plant via super(). Each subclass "
        "overrides show()."
    ),
)

_EX6 = Exercise(
    module_id="01", id="ex6",
    filenames=("ft_garden_analytics.py",),
    authorized=(
        "super", "print", "range", "round", "staticmethod", "classmethod",
    ),
    checks=(
        _struct_oop(
            "ft_garden_analytics.py",
            classes=("Plant", "Flower", "Seed"),
            require_main_guard=True,
            label="Plant/Flower/Seed + __main__ guard + free function",
        ),
        InlineCheck(
            label="Seed inherits Flower",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_garden_analytics import Flower, Seed\n"
                "assert issubclass(Seed, Flower)\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="Plant exposes a static and a class method",
            code=(
                "import inspect, sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_garden_analytics import Plant\n"
                "names = [n for n in dir(Plant) if not n.startswith('_')]\n"
                "has_static = any(\n"
                "    isinstance(inspect.getattr_static(Plant, n),\n"
                "               staticmethod) for n in names)\n"
                "has_class = any(\n"
                "    isinstance(inspect.getattr_static(Plant, n),\n"
                "               classmethod) for n in names)\n"
                "assert has_static, 'no @staticmethod on Plant'\n"
                "assert has_class, 'no @classmethod on Plant'\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="Plant has a nested class for stats",
            code=(
                "import inspect, sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_garden_analytics import Plant\n"
                "nested = [\n"
                "    n for n in dir(Plant)\n"
                "    if inspect.isclass(\n"
                "        inspect.getattr_static(Plant, n, None)\n"
                "    )\n"
                "]\n"
                "assert nested, 'no nested class in Plant for stats'\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="module exposes a free function (not a method)",
            code=(
                "import ast\n"
                "from pathlib import Path\n"
                "src = Path('ft_garden_analytics.py').read_text(\n"
                "    encoding='utf-8'\n"
                ")\n"
                "tree = ast.parse(src, filename='ft_garden_analytics.py')\n"
                "free = [\n"
                "    n.name for n in tree.body\n"
                "    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))\n"
                "]\n"
                "assert free, (\n"
                "    'no top-level function — the spec asks for a unique '\n"
                "    'function (not part of any class) that displays stats'\n"
                ")\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="Seed overrides show()",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from ft_garden_analytics import Seed, Flower\n"
                "seed_show = getattr(Seed, 'show', None)\n"
                "flower_show = getattr(Flower, 'show', None)\n"
                "assert seed_show is not None, 'Seed.show missing'\n"
                "assert seed_show is not flower_show, (\n"
                "    'Seed must override show()'\n"
                ")\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="Seed(name, height, age, color) accepted",
            code=(
                "import io, sys\n"
                "from contextlib import redirect_stdout\n"
                "sys.path.insert(0, '.')\n"
                "from ft_garden_analytics import Seed\n"
                "with redirect_stdout(io.StringIO()):\n"
                "    s = Seed('Sunflower', 80.0, 45, 'yellow')\n"
                "assert s is not None\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="Plant has a classmethod callable with no args (anonymous)",
            code=(
                "import inspect, io, sys\n"
                "from contextlib import redirect_stdout\n"
                "sys.path.insert(0, '.')\n"
                "from ft_garden_analytics import Plant\n"
                "cms = [\n"
                "    n for n in dir(Plant)\n"
                "    if not n.startswith('_')\n"
                "    and isinstance(\n"
                "        inspect.getattr_static(Plant, n), classmethod\n"
                "    )\n"
                "]\n"
                "ok = False\n"
                "with redirect_stdout(io.StringIO()):\n"
                "    for n in cms:\n"
                "        try:\n"
                "            getattr(Plant, n)()\n"
                "            ok = True\n"
                "            break\n"
                "        except TypeError:\n"
                "            continue\n"
                "assert ok, (\n"
                "    f'no @classmethod on Plant callable with no args '\n"
                "    f'(found: {cms!r})'\n"
                ")\n"
                "print('OK')\n"
            ),
        ),
        AuthorizedCheck(
            "ft_garden_analytics.py",
            ("super", "print", "range", "round",
             "staticmethod", "classmethod"),
        ),
        ScriptCheck(
            label="script prints the analytics banner",
            file="ft_garden_analytics.py",
            expected_contains=(
                "=== Garden statistics ===",
                "=== Flower",
                "=== Tree",
                "=== Seed",
                "Stats:",
                "Seeds:",
            ),
        ),
    ),
    explain=(
        "Plant gets @staticmethod (e.g. is_old(age)), @classmethod for "
        "anonymous plants, a nested stats class, and a Seed(Flower) subclass. "
        "A free top-level function displays stats for any plant."
    ),
)


MODULE_01 = Module(
    id="01",
    title="Code Cultivation — object-oriented garden systems",
    exercises=(_EX0, _EX1, _EX2, _EX3, _EX4, _EX5, _EX6),
)
