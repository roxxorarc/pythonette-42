from pythonette.subjects.registry import Exercise, Module, Registry
from pythonette.subjects.module_00 import MODULE_00
from pythonette.subjects.module_01 import MODULE_01
from pythonette.subjects.module_02 import MODULE_02
from pythonette.subjects.module_03 import MODULE_03

ALL_MODULES: list[Module] = [MODULE_00, MODULE_01, MODULE_02, MODULE_03]
REGISTRY = Registry(ALL_MODULES)

__all__ = ["Exercise", "Module", "Registry", "ALL_MODULES", "REGISTRY"]
