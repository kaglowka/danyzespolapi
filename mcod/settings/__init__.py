# -* coding: utf-8 *-
import os
import importlib

my_module = importlib.import_module(os.getenv('DJANGO_SETTINGS_MODULE', 'mcod.settings.local'))
my_module_dict = my_module.__dict__

try:
    to_import = my_module.__all__
except(AttributeError):
    to_import = [name for name in my_module_dict if not name.startswith('_')]

globals().update({name: my_module_dict[name] for name in to_import})
