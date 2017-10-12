import sys
import os.path
import shutil
from magicalimport import import_symbol
from importlib.util import spec_from_file_location
from importlib.util import module_from_spec
from importlib.machinery import SourceFileLoader


def call_file_as_main_module(filepath):
    spec = spec_from_file_location("__main__", filepath)
    module = module_from_spec(spec)
    code = spec.loader.get_code(module.__name__)
    # todo: call_with_frames_removed
    exec(code, module.__dict__)


def call_command_as_main_module(cmd, filepath):
    return SourceFileLoader("__main__", filepath).load_module()


def call_file(fname, extras):
    sys.argv = [sys.argv[0]]
    sys.argv.extend(extras)

    if ":" in fname:
        return import_symbol(fname)()
    elif os.path.exists(fname) and not os.path.isdir(fname):
        return call_file_as_main_module(fname)

    cmd_path = shutil.which(fname)
    if cmd_path:
        return call_command_as_main_module(fname, cmd_path)
