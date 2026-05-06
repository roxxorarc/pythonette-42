from pythonette.checks import ImportCheck, InlineCheck
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

def _no_eval_exec_check(scope_files: tuple[str, ...]) -> InlineCheck:
    return InlineCheck(
        label="no eval()/exec() and no sys.path mutation",
        code=(
            "import ast\n"
            "from pathlib import Path\n"
            f"scope = {list(scope_files)!r}\n"
            "files = []\n"
            "for entry in scope:\n"
            "    p = Path(entry)\n"
            "    if not p.exists():\n"
            "        continue\n"
            "    if p.is_dir():\n"
            "        files += [\n"
            "            q for q in p.rglob('*.py')\n"
            "            if '__pycache__' not in q.parts\n"
            "        ]\n"
            "    elif p.suffix == '.py':\n"
            "        files.append(p)\n"
            "bad = []\n"
            "for f in files:\n"
            "    tree = ast.parse(f.read_text(encoding='utf-8'),\n"
            "                     filename=str(f))\n"
            "    for n in ast.walk(tree):\n"
            "        if isinstance(n, ast.Call) and isinstance(n.func, "
            "ast.Name):\n"
            "            if n.func.id in ('eval', 'exec'):\n"
            "                bad.append(\n"
            "                    (str(f), n.lineno, f'{n.func.id}() call')\n"
            "                )\n"
            "        if isinstance(n, ast.Attribute) and n.attr == 'path':\n"
            "            v = n.value\n"
            "            if isinstance(v, ast.Name) and v.id == 'sys':\n"
            "                # Reading sys.path is fine; mutating is not.\n"
            "                # Detect attribute store / call on it.\n"
            "                pass\n"
            "    # Detect direct sys.path.append/insert/extend/remove etc.\n"
            "    for n in ast.walk(tree):\n"
            "        if (\n"
            "            isinstance(n, ast.Call)\n"
            "            and isinstance(n.func, ast.Attribute)\n"
            "            and isinstance(n.func.value, ast.Attribute)\n"
            "            and n.func.value.attr == 'path'\n"
            "            and isinstance(n.func.value.value, ast.Name)\n"
            "            and n.func.value.value.id == 'sys'\n"
            "        ):\n"
            "            bad.append(\n"
            "                (str(f), n.lineno,\n"
            "                 f'sys.path.{n.func.attr}() forbidden')\n"
            "            )\n"
            "assert not bad, (\n"
            "    'forbidden constructs:\\n'\n"
            "    + '\\n'.join(f'  {x[0]}:{x[1]} -> {x[2]}' for x in bad)\n"
            ")\n"
            "print('OK')\n"
        ),
    )


def _structure_check(required: tuple[str, ...]) -> InlineCheck:
    return InlineCheck(
        label="required project files exist on disk",
        code=(
            "from pathlib import Path\n"
            f"required = {list(required)!r}\n"
            "missing = [r for r in required if not Path(r).exists()]\n"
            "assert not missing, (\n"
            "    'missing required project file(s):\\n'\n"
            "    + '\\n'.join('  ' + m for m in missing)\n"
            ")\n"
            "print('OK')\n"
        ),
    )


def _runpy_check(
    label: str,
    file: str,
    *,
    contains: tuple[str, ...] = (),
    allow_exception: bool = False,
    timeout: float = 5.0,
) -> InlineCheck:
    """Run `file` as __main__, capture stdout+stderr together, assert each
    needle in `contains` appears in the combined output. If allow_exception,
    a raised exception is swallowed (its traceback ends up in stderr and is
    therefore part of the combined output)."""
    code = (
        "import runpy, sys, io\n"
        "from contextlib import redirect_stdout, redirect_stderr\n"
        "out = io.StringIO()\n"
        "err = io.StringIO()\n"
        "try:\n"
        "    with redirect_stdout(out), redirect_stderr(err):\n"
        f"        runpy.run_path({file!r}, run_name='__main__')\n"
        "except SystemExit:\n"
        "    pass\n"
    )
    if allow_exception:
        code += (
            "except BaseException as exc:\n"
            "    import traceback\n"
            "    traceback.print_exception(\n"
            "        type(exc), exc, exc.__traceback__, file=err\n"
            "    )\n"
        )
    code += (
        "combined = out.getvalue() + '\\n' + err.getvalue()\n"
    )
    for needle in contains:
        code += (
            f"assert {needle!r} in combined, (\n"
            f"    'missing in output: ' + {needle!r} + '\\n--- output ---\\n'\n"
            "    + combined\n"
            ")\n"
        )
    code += "print('OK')\n"
    return InlineCheck(label=label, code=code, timeout=timeout)


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
        _no_eval_exec_check(_ALEMBIC_FILES + _SUPPORT),
        InlineCheck(
            label="elements.py exposes create_fire / create_water",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "import elements\n"
                "assert elements.create_fire() == 'Fire element created'\n"
                "assert elements.create_water() == 'Water element created'\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="alchemy/elements.py exposes create_earth / create_air",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from alchemy import elements as alch_el\n"
                "assert alch_el.create_earth() == 'Earth element created'\n"
                "assert alch_el.create_air() == 'Air element created'\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label=(
                "alchemy package hides create_earth at top level "
                "(see ft_alembic_4)"
            ),
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "import alchemy\n"
                "assert hasattr(alchemy, 'create_air'), (\n"
                "    'alchemy must expose create_air at package level'\n"
                ")\n"
                "assert not hasattr(alchemy, 'create_earth'), (\n"
                "    'alchemy must NOT expose create_earth at package level'\n"
                ")\n"
                "print('OK')\n"
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
        _no_eval_exec_check(_DISTILLATION_FILES + _SUPPORT),
        InlineCheck(
            label="alchemy/potions.py: healing_potion + strength_potion",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from alchemy import potions\n"
                "h = potions.healing_potion()\n"
                "s = potions.strength_potion()\n"
                "assert 'Healing potion' in h and 'Earth element created' "
                "in h and 'Air element created' in h, h\n"
                "assert 'Strength potion' in s and 'Fire element created' "
                "in s and 'Water element created' in s, s\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label="alchemy.heal is exposed as alias of healing_potion",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "import alchemy\n"
                "assert hasattr(alchemy, 'heal'), (\n"
                "    'alchemy.__init__.py must expose heal as a package alias'\n"
                ")\n"
                "result = alchemy.heal()\n"
                "assert 'Healing potion' in result, result\n"
                "print('OK')\n"
            ),
        ),
        _runpy_check(
            "ft_distillation_0: from potions import + brew both potions",
            "ft_distillation_0.py",
            contains=(
                "=== Distillation 0 ===",
                "Strength potion brewed with 'Fire element created' and "
                "'Water element created'",
                "Healing potion brewed with 'Earth element created' and "
                "'Air element created'",
            ),
        ),
        _runpy_check(
            "ft_distillation_1: import alchemy + strength + heal alias",
            "ft_distillation_1.py",
            contains=(
                "=== Distillation 1 ===",
                "Strength potion brewed with 'Fire element created'",
                "Healing potion brewed with 'Earth element created'",
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


_RECIPES_IMPORT_STYLE_CHECK = InlineCheck(
    label=(
        "alchemy/transmutation/recipes.py uses both an absolute "
        "and a relative import"
    ),
    code=(
        "import ast\n"
        "from pathlib import Path\n"
        "src = Path('alchemy/transmutation/recipes.py').read_text(\n"
        "    encoding='utf-8'\n"
        ")\n"
        "tree = ast.parse(src, filename='alchemy/transmutation/recipes.py')\n"
        "absolute = False\n"
        "relative = False\n"
        "for n in ast.walk(tree):\n"
        "    if isinstance(n, ast.Import):\n"
        "        absolute = True\n"
        "    elif isinstance(n, ast.ImportFrom):\n"
        "        if (n.level or 0) > 0:\n"
        "            relative = True\n"
        "        else:\n"
        "            absolute = True\n"
        "assert absolute and relative, (\n"
        "    f'recipes.py must use BOTH an absolute and a relative import; '\n"
        "    f'absolute={absolute}, relative={relative}'\n"
        ")\n"
        "print('OK')\n"
    ),
)


_LEAD_SUBSTRINGS = (
    "Recipe transmuting Lead to Gold",
    "Air element created",
    "Strength potion brewed with 'Fire element created' and "
    "'Water element created'",
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
        _no_eval_exec_check(_TRANSMUTATION_FILES + _SUPPORT),
        _RECIPES_IMPORT_STYLE_CHECK,
        InlineCheck(
            label="lead_to_gold() composes air + strength + fire",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from alchemy.transmutation import recipes\n"
                "got = recipes.lead_to_gold()\n"
                "for needle in (\n"
                "    'Recipe transmuting Lead to Gold',\n"
                "    'Air element created',\n"
                "    'Strength potion',\n"
                "    'Fire element created',\n"
                "):\n"
                "    assert needle in got, (needle, got)\n"
                "print('OK')\n"
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
        _no_eval_exec_check(_KABOOM_FILES + _SUPPORT),
        InlineCheck(
            label="light_spellbook records valid + rejects invalid spells",
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "from alchemy.grimoire.light_spellbook import (\n"
                "    light_spell_record, light_spell_allowed_ingredients,\n"
                ")\n"
                "allowed = light_spell_allowed_ingredients()\n"
                "for el in ('earth', 'air', 'fire', 'water'):\n"
                "    assert el in [a.lower() for a in allowed], (el, allowed)\n"
                "ok = light_spell_record('Fantasy', 'Earth, wind and fire')\n"
                "assert 'recorded' in ok.lower() and 'VALID' in ok, ok\n"
                "ko = light_spell_record('Bogus', 'mercury and lead')\n"
                "low = ko.lower()\n"
                "assert ('invalid' in low or 'rejected' in low), ko\n"
                "print('OK')\n"
            ),
        ),
        InlineCheck(
            label=(
                "dark_spellbook intentionally has a circular import "
                "(import fails)"
            ),
            code=(
                "import sys\n"
                "sys.path.insert(0, '.')\n"
                "raised = False\n"
                "try:\n"
                "    import alchemy.grimoire.dark_spellbook  # noqa: F401\n"
                "except (ImportError, AttributeError):\n"
                "    raised = True\n"
                "assert raised, (\n"
                "    'alchemy.grimoire.dark_spellbook must fail to import '\n"
                "    'due to circular dependency between dark_spellbook '\n"
                "    'and dark_validator'\n"
                ")\n"
                "print('OK')\n"
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
