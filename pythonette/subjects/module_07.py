"""Module 07 — DataDeck: abstract card architecture."""

from pythonette.checks import (
    AssertCheck,
    Eq,
    FilesExistCheck,
    HasAttr,
    ImportCheck,
    LacksAttr,
    NoForbiddenCallsCheck,
    NoSysPathMutationCheck,
    Raises,
    RunCheck,
    Subclass,
    Truthy,
)
from pythonette.subjects.registry import Exercise, Module


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

# Subject IV: "Authorized: builtins, standard types, import typing, import abc."
_BASE_AUTHORIZED = ("abc", "typing")


def _imports_check(file: str, allowed: tuple[str, ...]) -> ImportCheck:
    """Walks `file` (or every .py under it if it's a directory) and rejects
    any absolute top-level import that is not in `allowed`. Relative
    imports are unconditionally allowed (project-local by definition)."""
    return ImportCheck(
        file=file,
        allowed=allowed,
        allow_relative=True,
    )


def _hygiene_checks(
    scope_files: tuple[str, ...],
) -> tuple[NoForbiddenCallsCheck, NoSysPathMutationCheck]:
    """Subject hygiene: no eval()/exec(), no sys.path mutation."""
    return (
        NoForbiddenCallsCheck(
            label="no eval() / exec() calls",
            scope=scope_files,
            forbidden=("eval", "exec"),
        ),
        NoSysPathMutationCheck(
            label="no sys.path mutation",
            scope=scope_files,
        ),
    )


def _structure_check(required: tuple[str, ...]) -> FilesExistCheck:
    return FilesExistCheck(
        label="required project files exist on disk",
        paths=required,
    )


def _runpy_check(
    label: str,
    file: str,
    *,
    contains: tuple[str, ...] = (),
    allow_exception: bool = False,
    timeout: float = 5.0,
) -> RunCheck:
    """Run `file` as __main__, asserting each needle appears in the
    combined stdout/stderr."""
    return RunCheck(
        label=label,
        file=file,
        combined_contains=contains,
        allow_exception=allow_exception,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Exercise 0 — Creature Factory
# ---------------------------------------------------------------------------

_EX0_SCRIPT = "battle.py"
_EX0_SUPPORT = ("ex0",)
_EX0_SCOPE = (_EX0_SCRIPT,) + _EX0_SUPPORT
_EX0_ALLOWED = _BASE_AUTHORIZED + ("ex0",)


_EX0_CREATURE_ABC_CHECK = AssertCheck(
    label="ex0: Creature is an abstract class with abstract attack",
    quiet=True,
    setup=(
        "import abc, inspect\n"
        "from ex0 import FlameFactory\n"
        "_creature = FlameFactory().create_base()\n"
        "Creature = type(_creature).__mro__[-2] "
        "if abc.ABC in type(_creature).__mro__ else None\n"
        "for _cls in type(_creature).__mro__:\n"
        "    if _cls is object or _cls is abc.ABC:\n"
        "        continue\n"
        "    if getattr(_cls, '__abstractmethods__', None):\n"
        "        Creature = _cls\n"
        "        break\n"
    ),
    assertions=(
        Truthy(
            "Creature is not None",
            message="could not locate the Creature abstract base class",
        ),
        Truthy(
            "inspect.isabstract(Creature)",
            message="Creature must be abstract (cannot be instantiated)",
        ),
        Truthy(
            "'attack' in getattr(Creature, '__abstractmethods__', "
            "frozenset())",
            message="'attack' must be @abstractmethod on Creature",
        ),
        Truthy(
            "callable(getattr(Creature, 'describe', None))",
            message="Creature must define a concrete describe() method",
        ),
        Truthy(
            "'describe' not in getattr(Creature, '__abstractmethods__', "
            "frozenset())",
            message="describe() must be concrete, not abstract",
        ),
    ),
)


_EX0_FACTORY_ABC_CHECK = AssertCheck(
    label="ex0: CreatureFactory is abstract with create_base / create_evolved",
    quiet=True,
    setup=(
        "import abc, inspect\n"
        "from ex0 import FlameFactory, AquaFactory\n"
        "Factory = None\n"
        "for _cls in FlameFactory.__mro__:\n"
        "    if _cls is object or _cls is abc.ABC:\n"
        "        continue\n"
        "    if _cls is FlameFactory:\n"
        "        continue\n"
        "    if getattr(_cls, '__abstractmethods__', None):\n"
        "        Factory = _cls\n"
        "        break\n"
    ),
    assertions=(
        Truthy(
            "Factory is not None",
            message="could not locate an abstract CreatureFactory base",
        ),
        Truthy(
            "inspect.isabstract(Factory)",
            message="CreatureFactory must be abstract",
        ),
        Truthy(
            "'create_base' in getattr(Factory, '__abstractmethods__', "
            "frozenset())",
            message="'create_base' must be @abstractmethod on the factory",
        ),
        Truthy(
            "'create_evolved' in getattr(Factory, "
            "'__abstractmethods__', frozenset())",
            message="'create_evolved' must be @abstractmethod on the factory",
        ),
        Subclass(
            "FlameFactory", "Factory",
            message="FlameFactory must inherit from CreatureFactory",
        ),
        Subclass(
            "AquaFactory", "Factory",
            message="AquaFactory must inherit from CreatureFactory",
        ),
    ),
)


_EX0_FACTORY_BEHAVIOR_CHECK = AssertCheck(
    label="ex0: factories produce describable + attacking Creatures",
    quiet=True,
    setup=(
        "from ex0 import FlameFactory, AquaFactory\n"
        "ff, af = FlameFactory(), AquaFactory()\n"
        "fb, fe = ff.create_base(), ff.create_evolved()\n"
        "ab, ae = af.create_base(), af.create_evolved()"
    ),
    assertions=(
        Truthy(
            "type(fb) is not type(fe)",
            message="base and evolved must be distinct concrete classes",
        ),
        Truthy(
            "type(ab) is not type(ae)",
            message="base and evolved must be distinct concrete classes",
        ),
        Truthy(
            "type(fb) is not type(ab)",
            message="different families must produce different Creatures",
        ),
        Truthy(
            "isinstance(fb.describe(), str) and len(fb.describe()) > 0",
            message="describe() must return a non-empty string",
        ),
        Truthy(
            "isinstance(fb.attack(), str) and len(fb.attack()) > 0",
            message="attack() must return a non-empty string",
        ),
        Truthy(
            "isinstance(ae.attack(), str) and len(ae.attack()) > 0",
            message="evolved attack() must return a non-empty string",
        ),
    ),
)


_EX0_ENCAPSULATION_CHECK = AssertCheck(
    label="ex0: package exposes factories but hides concrete Creatures",
    quiet=True,
    setup="import ex0",
    assertions=(
        HasAttr(
            "ex0", "FlameFactory",
            message="ex0 must expose FlameFactory",
        ),
        HasAttr(
            "ex0", "AquaFactory",
            message="ex0 must expose AquaFactory",
        ),
        LacksAttr(
            "ex0", "Flameling",
            message="ex0 must NOT expose concrete Creature 'Flameling'",
        ),
        LacksAttr(
            "ex0", "Pyrodon",
            message="ex0 must NOT expose concrete Creature 'Pyrodon'",
        ),
        LacksAttr(
            "ex0", "Aquabub",
            message="ex0 must NOT expose concrete Creature 'Aquabub'",
        ),
        LacksAttr(
            "ex0", "Torragon",
            message="ex0 must NOT expose concrete Creature 'Torragon'",
        ),
    ),
)


_EX0 = Exercise(
    module_id="07", id="ex0",
    filenames=(_EX0_SCRIPT,),
    support_paths=_EX0_SUPPORT,
    checks=(
        _structure_check((
            _EX0_SCRIPT,
            "ex0/__init__.py",
        )),
        _imports_check(_EX0_SCRIPT, _EX0_ALLOWED),
        _imports_check("ex0", _BASE_AUTHORIZED),
        *_hygiene_checks(_EX0_SCOPE),
        _EX0_CREATURE_ABC_CHECK,
        _EX0_FACTORY_ABC_CHECK,
        _EX0_FACTORY_BEHAVIOR_CHECK,
        _EX0_ENCAPSULATION_CHECK,
        _runpy_check(
            "battle.py runs the factory + battle scenario",
            _EX0_SCRIPT,
            contains=(
                "Testing factory",
                "type Creature",
                "Testing battle",
                "vs.",
                "fight!",
            ),
        ),
    ),
    explain=(
        "Exercise 0 (Creature Factory): build the ex0/ package with a "
        "Creature ABC (abstract attack, concrete describe), a "
        "CreatureFactory ABC (abstract create_base / create_evolved), and "
        "two concrete factories FlameFactory + AquaFactory. The package "
        "must expose factories only — concrete Creature classes stay "
        "private. battle.py exercises both factories and stages a fight."
    ),
)


# ---------------------------------------------------------------------------
# Exercise 1 — Capabilities
# ---------------------------------------------------------------------------

_EX1_SCRIPT = "capacitor.py"
_EX1_SUPPORT = ("ex0", "ex1")
_EX1_SCOPE = (_EX1_SCRIPT,) + _EX1_SUPPORT
_EX1_ALLOWED = _BASE_AUTHORIZED + ("ex0", "ex1")


_EX1_CAPABILITY_ABC_CHECK = AssertCheck(
    label="ex1: HealCapability and TransformCapability are abstract",
    quiet=True,
    setup=(
        "import abc, inspect\n"
        "from ex1 import HealCapability, TransformCapability"
    ),
    assertions=(
        Truthy(
            "inspect.isabstract(HealCapability)",
            message="HealCapability must be abstract",
        ),
        Truthy(
            "'heal' in getattr(HealCapability, '__abstractmethods__', "
            "frozenset())",
            message="HealCapability.heal must be @abstractmethod",
        ),
        Truthy(
            "inspect.isabstract(TransformCapability)",
            message="TransformCapability must be abstract",
        ),
        Truthy(
            "'transform' in getattr(TransformCapability, "
            "'__abstractmethods__', frozenset())",
            message="TransformCapability.transform must be @abstractmethod",
        ),
        Truthy(
            "'revert' in getattr(TransformCapability, "
            "'__abstractmethods__', frozenset())",
            message="TransformCapability.revert must be @abstractmethod",
        ),
    ),
)


_EX1_INDEPENDENCE_CHECK = AssertCheck(
    label=(
        "ex1: capability classes do NOT inherit from Creature"
    ),
    quiet=True,
    setup=(
        "from ex1 import HealCapability, TransformCapability\n"
        "from ex0 import FlameFactory\n"
        "Creature = None\n"
        "for _cls in type(FlameFactory().create_base()).__mro__:\n"
        "    if getattr(_cls, '__abstractmethods__', None) and "
        "_cls.__name__ == 'Creature':\n"
        "        Creature = _cls\n"
        "        break\n"
        "if Creature is None:\n"
        "    for _cls in type(FlameFactory().create_base()).__mro__:\n"
        "        if getattr(_cls, '__abstractmethods__', None):\n"
        "            Creature = _cls\n"
        "            break\n"
    ),
    assertions=(
        Truthy(
            "Creature is not None and not issubclass(HealCapability, "
            "Creature)",
            message=(
                "HealCapability must not inherit from Creature — "
                "capabilities are kept separate"
            ),
        ),
        Truthy(
            "not issubclass(TransformCapability, Creature)",
            message=(
                "TransformCapability must not inherit from Creature — "
                "capabilities are kept separate"
            ),
        ),
    ),
)


_EX1_FACTORIES_CHECK = AssertCheck(
    label=(
        "ex1: HealingCreatureFactory + TransformCreatureFactory inherit "
        "the ex0 CreatureFactory and produce capable Creatures"
    ),
    quiet=True,
    setup=(
        "from ex0 import FlameFactory\n"
        "from ex1 import (\n"
        "    HealingCreatureFactory, TransformCreatureFactory,\n"
        "    HealCapability, TransformCapability,\n"
        ")\n"
        "Factory = None\n"
        "for _cls in FlameFactory.__mro__:\n"
        "    if getattr(_cls, '__abstractmethods__', None) and _cls is not "
        "FlameFactory:\n"
        "        Factory = _cls\n"
        "        break\n"
        "hf, tf = HealingCreatureFactory(), TransformCreatureFactory()\n"
        "hb, he = hf.create_base(), hf.create_evolved()\n"
        "tb, te = tf.create_base(), tf.create_evolved()"
    ),
    assertions=(
        Subclass(
            "HealingCreatureFactory", "Factory",
            message=(
                "HealingCreatureFactory must inherit from the ex0 "
                "CreatureFactory"
            ),
        ),
        Subclass(
            "TransformCreatureFactory", "Factory",
            message=(
                "TransformCreatureFactory must inherit from the ex0 "
                "CreatureFactory"
            ),
        ),
        Truthy(
            "isinstance(hb, HealCapability) and isinstance(he, "
            "HealCapability)",
            message="healing factory must yield HealCapability instances",
        ),
        Truthy(
            "isinstance(tb, TransformCapability) and isinstance(te, "
            "TransformCapability)",
            message="transform factory must yield TransformCapability "
            "instances",
        ),
        Truthy(
            "isinstance(hb.attack(), str) and isinstance(hb.heal(), str)",
            message="heal() and attack() must return strings",
        ),
        Truthy(
            "isinstance(tb.transform(), str) and isinstance(tb.revert(), "
            "str)",
            message="transform() and revert() must return strings",
        ),
    ),
)


_EX1_TRANSFORM_STATE_CHECK = AssertCheck(
    label="ex1: transform state persists and changes attack output",
    quiet=True,
    setup=(
        "from ex1 import TransformCreatureFactory\n"
        "c = TransformCreatureFactory().create_base()\n"
        "before = c.attack()\n"
        "c.transform()\n"
        "during = c.attack()\n"
        "c.revert()\n"
        "after = c.attack()"
    ),
    assertions=(
        Truthy(
            "before != during",
            message=(
                "attack() must differ once the Creature has transformed"
            ),
        ),
        Eq("before", "after"),
    ),
)


_EX1_ENCAPSULATION_CHECK = AssertCheck(
    label="ex1: package exposes factories + capabilities, not Creatures",
    quiet=True,
    setup="import ex1",
    assertions=(
        HasAttr("ex1", "HealingCreatureFactory"),
        HasAttr("ex1", "TransformCreatureFactory"),
        HasAttr("ex1", "HealCapability"),
        HasAttr("ex1", "TransformCapability"),
        LacksAttr(
            "ex1", "Sproutling",
            message="ex1 must NOT expose concrete Creature 'Sproutling'",
        ),
        LacksAttr(
            "ex1", "Bloomelle",
            message="ex1 must NOT expose concrete Creature 'Bloomelle'",
        ),
        LacksAttr(
            "ex1", "Shiftling",
            message="ex1 must NOT expose concrete Creature 'Shiftling'",
        ),
        LacksAttr(
            "ex1", "Morphagon",
            message="ex1 must NOT expose concrete Creature 'Morphagon'",
        ),
    ),
)


_EX1 = Exercise(
    module_id="07", id="ex1",
    filenames=(_EX1_SCRIPT,),
    support_paths=_EX1_SUPPORT,
    checks=(
        _structure_check((
            _EX1_SCRIPT,
            "ex0/__init__.py",
            "ex1/__init__.py",
        )),
        _imports_check(_EX1_SCRIPT, _EX1_ALLOWED),
        _imports_check("ex1", _BASE_AUTHORIZED + ("ex0",)),
        *_hygiene_checks(_EX1_SCOPE),
        _EX1_CAPABILITY_ABC_CHECK,
        _EX1_INDEPENDENCE_CHECK,
        _EX1_FACTORIES_CHECK,
        _EX1_TRANSFORM_STATE_CHECK,
        _EX1_ENCAPSULATION_CHECK,
        _runpy_check(
            "capacitor.py exercises healing + transform Creatures",
            _EX1_SCRIPT,
            contains=(
                "Testing Creature with healing capability",
                "Testing Creature with transform capability",
                "type Creature",
            ),
        ),
    ),
    explain=(
        "Exercise 1 (Capabilities): add ex1/ with HealCapability and "
        "TransformCapability ABCs that DO NOT inherit from Creature. "
        "Concrete classes inherit from both Creature and one capability, "
        "and are produced by HealingCreatureFactory / "
        "TransformCreatureFactory (subclasses of the ex0 CreatureFactory). "
        "Transform state persists and alters attack(). capacitor.py is "
        "the demo script."
    ),
)


# ---------------------------------------------------------------------------
# Exercise 2 — Abstract Strategy
# ---------------------------------------------------------------------------

_EX2_SCRIPT = "tournament.py"
_EX2_SUPPORT = ("ex0", "ex1", "ex2")
_EX2_SCOPE = (_EX2_SCRIPT,) + _EX2_SUPPORT
_EX2_ALLOWED = _BASE_AUTHORIZED + ("ex0", "ex1", "ex2")


_EX2_STRATEGY_ABC_CHECK = AssertCheck(
    label="ex2: BattleStrategy is abstract with act + is_valid",
    quiet=True,
    setup=(
        "import abc, inspect\n"
        "from ex2 import (\n"
        "    BattleStrategy, NormalStrategy, AggressiveStrategy,\n"
        "    DefensiveStrategy,\n"
        ")"
    ),
    assertions=(
        Truthy(
            "inspect.isabstract(BattleStrategy)",
            message="BattleStrategy must be abstract",
        ),
        Truthy(
            "'act' in getattr(BattleStrategy, '__abstractmethods__', "
            "frozenset())",
            message="BattleStrategy.act must be @abstractmethod",
        ),
        Truthy(
            "'is_valid' in getattr(BattleStrategy, '__abstractmethods__', "
            "frozenset())",
            message="BattleStrategy.is_valid must be @abstractmethod",
        ),
        Subclass("NormalStrategy", "BattleStrategy"),
        Subclass("AggressiveStrategy", "BattleStrategy"),
        Subclass("DefensiveStrategy", "BattleStrategy"),
    ),
)


_EX2_VALIDITY_CHECK = AssertCheck(
    label=(
        "ex2: is_valid maps strategies to suitable Creature capabilities"
    ),
    quiet=True,
    setup=(
        "from ex0 import FlameFactory\n"
        "from ex1 import HealingCreatureFactory, TransformCreatureFactory\n"
        "from ex2 import (\n"
        "    NormalStrategy, AggressiveStrategy, DefensiveStrategy,\n"
        ")\n"
        "plain = FlameFactory().create_base()\n"
        "healer = HealingCreatureFactory().create_base()\n"
        "shifter = TransformCreatureFactory().create_base()\n"
        "n, a, d = NormalStrategy(), AggressiveStrategy(), "
        "DefensiveStrategy()"
    ),
    assertions=(
        Eq("n.is_valid(plain)", True),
        Eq("n.is_valid(healer)", True),
        Eq("n.is_valid(shifter)", True),
        Eq("a.is_valid(shifter)", True),
        Eq("a.is_valid(plain)", False),
        Eq("a.is_valid(healer)", False),
        Eq("d.is_valid(healer)", True),
        Eq("d.is_valid(plain)", False),
        Eq("d.is_valid(shifter)", False),
    ),
)


_EX2_ACT_CHECK = AssertCheck(
    label="ex2: act() raises on invalid Creature-strategy combos",
    quiet=True,
    setup=(
        "from ex0 import FlameFactory\n"
        "from ex1 import HealingCreatureFactory, TransformCreatureFactory\n"
        "from ex2 import (\n"
        "    NormalStrategy, AggressiveStrategy, DefensiveStrategy,\n"
        ")\n"
        "plain = FlameFactory().create_base()\n"
        "healer = HealingCreatureFactory().create_base()\n"
        "shifter = TransformCreatureFactory().create_base()\n"
        "n, a, d = NormalStrategy(), AggressiveStrategy(), "
        "DefensiveStrategy()"
    ),
    assertions=(
        Truthy(
            "n.act(plain) is None or isinstance(n.act(plain), (str, list, "
            "tuple, type(None)))",
            message="NormalStrategy.act on a basic Creature must not raise",
        ),
        Truthy(
            "a.act(shifter) is None or isinstance(a.act(shifter), (str, "
            "list, tuple, type(None)))",
            message=(
                "AggressiveStrategy.act on a transform Creature must not "
                "raise"
            ),
        ),
        Truthy(
            "d.act(healer) is None or isinstance(d.act(healer), (str, "
            "list, tuple, type(None)))",
            message=(
                "DefensiveStrategy.act on a healing Creature must not raise"
            ),
        ),
        Raises(
            "a.act(plain)",
            message=(
                "AggressiveStrategy.act on a non-transform Creature must "
                "raise a dedicated exception"
            ),
        ),
        Raises(
            "d.act(plain)",
            message=(
                "DefensiveStrategy.act on a non-healing Creature must "
                "raise a dedicated exception"
            ),
        ),
    ),
)


_EX2 = Exercise(
    module_id="07", id="ex2",
    filenames=(_EX2_SCRIPT,),
    support_paths=_EX2_SUPPORT,
    checks=(
        _structure_check((
            _EX2_SCRIPT,
            "ex0/__init__.py",
            "ex1/__init__.py",
            "ex2/__init__.py",
        )),
        _imports_check(_EX2_SCRIPT, _EX2_ALLOWED),
        _imports_check("ex2", _BASE_AUTHORIZED + ("ex0", "ex1")),
        *_hygiene_checks(_EX2_SCOPE),
        _EX2_STRATEGY_ABC_CHECK,
        _EX2_VALIDITY_CHECK,
        _EX2_ACT_CHECK,
        _runpy_check(
            "tournament.py runs basic + error + multi-opponent rounds",
            _EX2_SCRIPT,
            contains=(
                "Tournament",
                "opponents involved",
                "Battle",
                "vs.",
                "now fight!",
                "aborting tournament",
            ),
            allow_exception=True,
        ),
    ),
    explain=(
        "Exercise 2 (Abstract Strategy): add ex2/ with the BattleStrategy "
        "ABC (abstract act + is_valid) and three concrete strategies — "
        "NormalStrategy (any Creature), AggressiveStrategy (transform "
        "capability only) and DefensiveStrategy (healing capability "
        "only). is_valid filters; act raises a dedicated exception on an "
        "invalid combo. tournament.py runs a single battle() function "
        "that pairs every opponent and dispatches via each Creature's "
        "strategy."
    ),
)


MODULE_07 = Module(
    id="07",
    title="DataDeck — Abstract Card Architecture",
    exercises=(_EX0, _EX1, _EX2),
)
