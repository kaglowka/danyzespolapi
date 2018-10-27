import sys
from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader

from mcod.lib.hacks.goodtables import spec as hacked_spec


class CustomLoader(SourceFileLoader):
    def exec_module(self, module):
        module.spec = hacked_spec.spec
        return module


class Finder(PathFinder):
    def __init__(self, module_name):
        self.module_name = module_name

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            spec = super().find_spec(fullname, path, target)
            return ModuleSpec(fullname,
                              CustomLoader(fullname, spec.origin))


def apply():
    sys.meta_path.insert(0, Finder('goodtables.spec'))
