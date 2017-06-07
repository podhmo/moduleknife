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
