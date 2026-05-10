"""Module 06 — The Codex: mastering Python's import mysteries."""

from pythonette.checks import (
    AssertCheck,
    Contains,
    ContainsAll,
    Eq,
    FilesExistCheck,
    HasAttr,
    ImportCheck,
    ImportStyleCheck,
    LacksAttr,
    NoForbiddenCallsCheck,
    NoSysPathMutationCheck,
    Raises,
    RunCheck,
    Truthy,
)
from pythonette.subjects.registry import Exercise, Module


_SUPPORT = ("alchemy", "elements.py")
_PROJECT_IMPORTS = ("alchemy", "elements")


def _imports_check(file: str) -> ImportCheck:
    """Subject III: 'Only imports of the modules and files you will create
    in this project are allowed.' Walks `file` (or every .py under it if
    it's a directory) and rejects any absolute top-level import that is
    neither `alchemy` nor `elements`. Relative imports are unconditionally
    allowed (they're project-local by definition)."""
    return ImportCheck(
        file=file,
        allowed=_PROJECT_IMPORTS,
        allow_relative=True,
    )


def _imports_checks(scripts: tuple[str, ...]) -> tuple[ImportCheck, ...]:
    """One ImportCheck per script + one over the whole alchemy package +
    one over the top-level elements.py."""
    return (
        *(_imports_check(f) for f in scripts),
        _imports_check("alchemy"),
        _imports_check("elements.py"),
    )


# ---------------------------------------------------------------------------
# Shared check helpers
# ---------------------------------------------------------------------------

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
    """Run `file` as __main__, asserting each needle appears in stdout
    or stderr (the combined output)."""
    return RunCheck(
        label=label,
        file=file,
        combined_contains=contains,
        allow_exception=allow_exception,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Exercise 0 — Part I: The Alembic
# ---------------------------------------------------------------------------

_ALEMBIC_FILES = tuple(f"ft_alembic_{i}.py" for i in range(6))

_EX0 = Exercise(
    module_id="06", id="ex0",
    filenames=_ALEMBIC_FILES,
    support_paths=_SUPPORT,
    # Subject IV.1: ft_alembic_4 intentionally triggers a mypy error
    # ("A mypy error will also raise, again, on purpose").
    mypy_skip=("ft_alembic_4.py",),
    checks=(
        _structure_check((
            "elements.py",
            "alchemy/__init__.py",
            "alchemy/elements.py",
        )),
        *_imports_checks(_ALEMBIC_FILES),
        *_hygiene_checks(_ALEMBIC_FILES + _SUPPORT),
        AssertCheck(
            label="elements.py exposes create_fire / create_water",
            setup="import elements",
            assertions=(
                Eq("elements.create_fire()", "Fire element created"),
                Eq("elements.create_water()", "Water element created"),
            ),
        ),
        AssertCheck(
            label="alchemy/elements.py exposes create_earth / create_air",
            setup="from alchemy import elements as alch_el",
            assertions=(
                Eq("alch_el.create_earth()", "Earth element created"),
                Eq("alch_el.create_air()", "Air element created"),
            ),
        ),
        AssertCheck(
            label=(
                "alchemy package hides create_earth at top level "
                "(see ft_alembic_4)"
            ),
            setup="import alchemy",
            assertions=(
                HasAttr(
                    "alchemy", "create_air",
                    message="alchemy must expose create_air at package level",
                ),
                LacksAttr(
                    "alchemy", "create_earth",
                    message=(
                        "alchemy must NOT expose create_earth at "
                        "package level"
                    ),
                ),
            ),
        ),
        _runpy_check(
            "ft_alembic_0: import elements + create_fire",
            "ft_alembic_0.py",
            contains=("=== Alembic 0 ===", "Fire element created"),
        ),
        _runpy_check(
            "ft_alembic_1: from elements import + create_water",
            "ft_alembic_1.py",
            contains=("=== Alembic 1 ===", "Water element created"),
        ),
        _runpy_check(
            "ft_alembic_2: import alchemy.elements + create_earth",
            "ft_alembic_2.py",
            contains=("=== Alembic 2 ===", "Earth element created"),
        ),
        _runpy_check(
            "ft_alembic_3: from alchemy.elements import + create_air",
            "ft_alembic_3.py",
            contains=("=== Alembic 3 ===", "Air element created"),
        ),
        _runpy_check(
            "ft_alembic_4: import alchemy + create_air + AttributeError",
            "ft_alembic_4.py",
            contains=(
                "=== Alembic 4 ===",
                "Air element created",
                "AttributeError",
            ),
            allow_exception=True,
        ),
        _runpy_check(
            "ft_alembic_5: from alchemy import + create_air",
            "ft_alembic_5.py",
            contains=("=== Alembic 5 ===", "Air element created"),
        ),
    ),
    explain=(
        "Part I (the Alembic): build elements.py + alchemy/elements.py + "
        "alchemy/__init__.py. The 6 ft_alembic_*.py scripts each use a "
        "different import structure to reach create_fire/water/earth/air. "
        "alchemy/__init__.py must expose create_air but NOT create_earth, "
        "so ft_alembic_4 demonstrates AttributeError on the hidden symbol."
    ),
)


# ---------------------------------------------------------------------------
# Exercise 1 — Part II: Distillation
# ---------------------------------------------------------------------------

_DISTILLATION_FILES = ("ft_distillation_0.py", "ft_distillation_1.py")

_EX1 = Exercise(
    module_id="06", id="ex1",
    filenames=_DISTILLATION_FILES,
    support_paths=_SUPPORT,
    checks=(
        _structure_check(("alchemy/potions.py",)),
        *_imports_checks(_DISTILLATION_FILES),
        *_hygiene_checks(_DISTILLATION_FILES + _SUPPORT),
        AssertCheck(
            label="alchemy/potions.py: healing_potion + strength_potion",
            setup="from alchemy import potions",
            assertions=(
                ContainsAll(
                    "potions.healing_potion()",
                    (
                        "Healing potion",
                        "Earth element created",
                        "Air element created",
                    ),
                ),
                ContainsAll(
                    "potions.strength_potion()",
                    (
                        "Strength potion",
                        "Fire element created",
                        "Water element created",
                    ),
                ),
            ),
        ),
        AssertCheck(
            label="alchemy.heal is exposed as alias of healing_potion",
            setup="import alchemy",
            assertions=(
                HasAttr(
                    "alchemy", "heal",
                    message=(
                        "alchemy.__init__.py must expose heal as a "
                        "package alias"
                    ),
                ),
                Contains("alchemy.heal()", "Healing potion"),
            ),
        ),
        _runpy_check(
            "ft_distillation_0: from potions import + brew both potions",
            "ft_distillation_0.py",
            contains=(
                "=== Distillation 0 ===",
                "Strength potion",
                "Fire element created",
                "Water element created",
                "Healing potion",
                "Earth element created",
                "Air element created",
            ),
        ),
        _runpy_check(
            "ft_distillation_1: import alchemy + strength + heal alias",
            "ft_distillation_1.py",
            contains=(
                "=== Distillation 1 ===",
                "Strength potion",
                "Fire element created",
                "Healing potion",
                "Earth element created",
            ),
        ),
    ),
    explain=(
        "Part II (Distillation): add alchemy/potions.py with healing_potion "
        "(uses earth+air) and strength_potion (uses fire+water). Improve "
        "alchemy/__init__.py to expose `heal` as an alias of healing_potion. "
        "Two scripts exercise the new module via direct import and via the "
        "package alias."
    ),
)


# ---------------------------------------------------------------------------
# Exercise 2 — Part III: The Great Transmutation
# ---------------------------------------------------------------------------

_TRANSMUTATION_FILES = (
    "ft_transmutation_0.py",
    "ft_transmutation_1.py",
    "ft_transmutation_2.py",
)


_RECIPES_IMPORT_STYLE_CHECK = ImportStyleCheck(
    label=(
        "alchemy/transmutation/recipes.py uses both an absolute "
        "and a relative import"
    ),
    file="alchemy/transmutation/recipes.py",
    require_absolute=True,
    require_relative=True,
)


_LEAD_SUBSTRINGS = (
    "Lead to Gold",
    "Air element created",
    "Strength potion",
    "Fire element created",
)


_EX2 = Exercise(
    module_id="06", id="ex2",
    filenames=_TRANSMUTATION_FILES,
    support_paths=_SUPPORT,
    checks=(
        _structure_check((
            "alchemy/transmutation/__init__.py",
            "alchemy/transmutation/recipes.py",
        )),
        *_imports_checks(_TRANSMUTATION_FILES),
        *_hygiene_checks(_TRANSMUTATION_FILES + _SUPPORT),
        _RECIPES_IMPORT_STYLE_CHECK,
        AssertCheck(
            label="lead_to_gold() composes air + strength + fire",
            setup="from alchemy.transmutation import recipes",
            assertions=(
                ContainsAll(
                    "recipes.lead_to_gold()",
                    (
                        "Recipe transmuting Lead to Gold",
                        "Air element created",
                        "Strength potion",
                        "Fire element created",
                    ),
                ),
            ),
        ),
        _runpy_check(
            "ft_transmutation_0: direct file access",
            "ft_transmutation_0.py",
            contains=("=== Transmutation 0 ===",) + _LEAD_SUBSTRINGS,
        ),
        _runpy_check(
            "ft_transmutation_1: import transmutation submodule",
            "ft_transmutation_1.py",
            contains=("=== Transmutation 1 ===",) + _LEAD_SUBSTRINGS,
        ),
        _runpy_check(
            "ft_transmutation_2: import alchemy only",
            "ft_transmutation_2.py",
            contains=("=== Transmutation 2 ===",) + _LEAD_SUBSTRINGS,
        ),
    ),
    explain=(
        "Part III (Great Transmutation): add alchemy/transmutation/recipes.py "
        "with lead_to_gold() composing air + strength_potion + fire. The "
        "recipes module must use BOTH an absolute and a relative import. "
        "Three scripts reach lead_to_gold via three different import paths."
    ),
)


# ---------------------------------------------------------------------------
# Exercise 3 — Part IV: Avoid the Explosion
# ---------------------------------------------------------------------------

_KABOOM_FILES = ("ft_kaboom_0.py", "ft_kaboom_1.py")


_EX3 = Exercise(
    module_id="06", id="ex3",
    filenames=_KABOOM_FILES,
    support_paths=_SUPPORT,
    checks=(
        _structure_check((
            "alchemy/grimoire/__init__.py",
            "alchemy/grimoire/light_spellbook.py",
            "alchemy/grimoire/light_validator.py",
            "alchemy/grimoire/dark_spellbook.py",
            "alchemy/grimoire/dark_validator.py",
        )),
        *_imports_checks(_KABOOM_FILES),
        *_hygiene_checks(_KABOOM_FILES + _SUPPORT),
        AssertCheck(
            label="light_spellbook records valid + rejects invalid spells",
            setup=(
                "from alchemy.grimoire.light_spellbook import (\n"
                "    light_spell_record, light_spell_allowed_ingredients,\n"
                ")\n"
                "allowed_lower = "
                "[a.lower() for a in light_spell_allowed_ingredients()]\n"
                "ok = light_spell_record('Fantasy', 'Earth, wind and fire')\n"
                "ko = light_spell_record('Bogus', 'mercury and lead')"
            ),
            assertions=(
                ContainsAll(
                    "allowed_lower", ("earth", "air", "fire", "water"),
                ),
                Contains("ok.lower()", "recorded"),
                Contains("ok", "VALID"),
                Truthy(
                    "'invalid' in ko.lower() or 'rejected' in ko.lower()",
                    message="invalid spell must mention 'invalid' or 'rejected'",
                ),
            ),
        ),
        AssertCheck(
            label=(
                "dark_spellbook intentionally has a circular import "
                "(import fails)"
            ),
            assertions=(
                Raises(
                    "import alchemy.grimoire.dark_spellbook  # noqa: F401",
                    exception_types=("ImportError", "AttributeError"),
                    message=(
                        "alchemy.grimoire.dark_spellbook must fail to "
                        "import due to circular dependency between "
                        "dark_spellbook and dark_validator"
                    ),
                ),
            ),
        ),
        _runpy_check(
            "ft_kaboom_0: light spell recorded successfully",
            "ft_kaboom_0.py",
            contains=("=== Kaboom 0 ===", "recorded", "VALID"),
        ),
        _runpy_check(
            "ft_kaboom_1: dark import explodes (ImportError raised)",
            "ft_kaboom_1.py",
            contains=("=== Kaboom 1 ===", "ImportError"),
            allow_exception=True,
        ),
    ),
    explain=(
        "Part IV (Kaboom): add alchemy/grimoire/ with paired spellbook/"
        "validator files. light_* avoids circular imports (one module "
        "imports the other lazily, or the validator is the leaf). dark_* "
        "is intentionally broken: dark_spellbook and dark_validator import "
        "each other at module top level, producing a circular ImportError."
    ),
)


MODULE_06 = Module(
    id="06",
    title="The Codex — Mastering Python's Import Mysteries",
    exercises=(_EX0, _EX1, _EX2, _EX3),
)
