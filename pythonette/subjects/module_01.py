"""Module 01 — Code Cultivation: object-oriented garden systems."""

from pythonette.checks import (
    AssertCheck,
    AuthorizedCheck,
    HasAttr,
    HasClassMethod,
    HasNestedClass,
    HasStaticMethod,
    IsNot,
    MethodArityCheck,
    MethodSignatureCheck,
    NotRaises,
    RequireNodeTypesCheck,
    ScriptCheck,
    StructureCheck,
    Subclass,
    Truthy,
)
from pythonette.subjects.registry import Exercise, Module


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Exercise 0: ft_garden_intro
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Exercise 1: ft_garden_data
# ---------------------------------------------------------------------------

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
        AssertCheck(
            label="Plant class exposes show()",
            setup="from ft_garden_data import Plant",
            assertions=(HasAttr("Plant", "show", message="Plant.show missing"),),
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

# ---------------------------------------------------------------------------
# Exercise 2: ft_plant_growth
# ---------------------------------------------------------------------------

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
        AssertCheck(
            label="Plant exposes grow / age",
            setup="from ft_plant_growth import Plant",
            assertions=(
                HasAttr("Plant", "grow", message="Plant.grow missing"),
                HasAttr("Plant", "age", message="Plant.age missing"),
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

# ---------------------------------------------------------------------------
# Exercise 3: ft_plant_factory
# ---------------------------------------------------------------------------

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
        AssertCheck(
            label="constructor accepts (name, height, age) positionally",
            setup="from ft_plant_factory import Plant",
            assertions=(
                NotRaises(
                    "Plant('Rose', 25.0, 30)",
                    message=(
                        "Plant.__init__ must accept (name, height, age) "
                        "positionally"
                    ),
                ),
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

# ---------------------------------------------------------------------------
# Exercise 4: ft_garden_security
# ---------------------------------------------------------------------------

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
        AssertCheck(
            label="setters reject negative values",
            quiet=True,
            setup=(
                "from ft_garden_security import Plant\n"
                "p = Plant('Rose', 15.0, 10)\n"
                "p.set_height(25)\n"
                "p.set_age(30)\n"
                "h_ok, a_ok = p.get_height(), p.get_age()\n"
                "p.set_height(-5)\n"
                "p.set_age(-3)"
            ),
            assertions=(
                Truthy(
                    "p.get_height() == h_ok",
                    message="negative height was accepted",
                ),
                Truthy(
                    "p.get_age() == a_ok",
                    message="negative age was accepted",
                ),
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

# ---------------------------------------------------------------------------
# Exercise 5: ft_plant_types
# ---------------------------------------------------------------------------

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
        AssertCheck(
            label="Flower / Tree / Vegetable inherit Plant",
            setup=(
                "from ft_plant_types import Plant, Flower, Tree, Vegetable"
            ),
            assertions=(
                Subclass("Flower", "Plant"),
                Subclass("Tree", "Plant"),
                Subclass("Vegetable", "Plant"),
            ),
        ),
        MethodArityCheck("ft_plant_types", "Flower", "bloom", 0),
        MethodArityCheck("ft_plant_types", "Tree", "produce_shade", 0),
        AssertCheck(
            label="Flower(name, height, age, color) accepted",
            setup="from ft_plant_types import Flower",
            quiet=True,
            assertions=(
                NotRaises(
                    "Flower('Rose', 15.0, 10, 'red')",
                    exception_types=("TypeError",),
                    message=(
                        "Flower.__init__ must accept 4 parameters: "
                        "name, height, age, color"
                    ),
                ),
            ),
        ),
        AssertCheck(
            label="Tree(name, height, age, trunk_diameter) accepted",
            setup="from ft_plant_types import Tree",
            quiet=True,
            assertions=(
                NotRaises(
                    "Tree('Oak', 200.0, 365, 5.0)",
                    exception_types=("TypeError",),
                    message=(
                        "Tree.__init__ must accept 4 parameters: "
                        "name, height, age, trunk_diameter"
                    ),
                ),
            ),
        ),
        AssertCheck(
            label=(
                "Vegetable(name, height, age, harvest_season, "
                "nutritional_value) accepted"
            ),
            setup="from ft_plant_types import Vegetable",
            quiet=True,
            assertions=(
                NotRaises(
                    "Vegetable('Tomato', 5.0, 10, 'April', 0)",
                    exception_types=("TypeError",),
                    message=(
                        "Vegetable.__init__ must accept 5 parameters: "
                        "name, height, age, harvest_season, "
                        "nutritional_value"
                    ),
                ),
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

# ---------------------------------------------------------------------------
# Exercise 6: ft_garden_analytics
# ---------------------------------------------------------------------------

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
        AssertCheck(
            label="Seed inherits Flower",
            setup="from ft_garden_analytics import Flower, Seed",
            assertions=(Subclass("Seed", "Flower"),),
        ),
        AssertCheck(
            label="Plant exposes a static and a class method",
            setup="from ft_garden_analytics import Plant",
            assertions=(
                HasStaticMethod("Plant"),
                HasClassMethod("Plant"),
            ),
        ),
        AssertCheck(
            label="Plant has a nested class for stats",
            setup="from ft_garden_analytics import Plant",
            assertions=(
                HasNestedClass(
                    "Plant", message="no nested class in Plant for stats",
                ),
            ),
        ),
        RequireNodeTypesCheck(
            label="module exposes a free function (not a method)",
            scope=("ft_garden_analytics.py",),
            node_types=("FunctionDef",),
            top_level_only=True,
            reason=(
                "no top-level function — the spec asks for a unique "
                "function (not part of any class) that displays stats"
            ),
        ),
        AssertCheck(
            label="Seed overrides show()",
            setup="from ft_garden_analytics import Seed, Flower",
            assertions=(
                Truthy(
                    "getattr(Seed, 'show', None) is not None",
                    message="Seed.show missing",
                ),
                IsNot(
                    "Seed.show", "Flower.show",
                    message="Seed must override show()",
                ),
            ),
        ),
        AssertCheck(
            label="Seed(name, height, age, color) accepted",
            setup="from ft_garden_analytics import Seed",
            quiet=True,
            assertions=(
                NotRaises("Seed('Sunflower', 80.0, 45, 'yellow')"),
            ),
        ),
        AssertCheck(
            label="Plant has a classmethod callable with no args (anonymous)",
            quiet=True,
            setup="from ft_garden_analytics import Plant",
            assertions=(
                HasClassMethod(
                    "Plant",
                    callable_no_args=True,
                    message=(
                        "no @classmethod on Plant callable with no "
                        "arguments (anonymous)"
                    ),
                ),
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
