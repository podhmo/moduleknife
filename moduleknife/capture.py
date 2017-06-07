import sys
DEFAULT_MODULES = set(sys.modules.keys())  # NOQA
import signal
import inspect
import contextlib


def _get_caller(frame=None, lv=2):
    frame = frame or inspect.currentframe()
    for _ in range(lv):
        frame = frame.f_back
        if frame is None:
            return None
    while "importlib" in frame.f_code.co_filename:
        frame = frame.f_back
    return frame


class CapturedLoaderFactory:
    def __init__(self, fn):
        self.fn = fn
        self.cls_map = {}

    def create_ext_loader_class(self, cls, fn):
        if cls in self.cls_map:
            return self.cls_map[cls]
        if getattr(cls, "_IS_CAPTURED_EXT_LOADER", False):
            return cls

        class ExtLoader(cls):
            _IS_CAPTURED_EXT_LOADER = True

            def exec_module(self, module):
                frame = _get_caller(lv=2)
                where = frame.f_code.co_filename
                filename = module.__file__
                fn(where, filename)
                return super().exec_module(module)

        self.cls_map[cls] = ExtLoader
        return ExtLoader

    def new_loaders(self, loaders):
        r = []
        for pair in loaders:
            r.append((pair[0], self.create_ext_loader_class(pair[1], self.fn)))
        return r

    def hookwrap(self, hook):
        if getattr(hook, "wrapped", False):
            return hook

        def wrap(filename):
            finder = hook(filename)
            finder._loaders = self.new_loaders(finder._loaders)
            return finder

        wrap.wrapped = True
        return wrap


def activate(fn, preserved=DEFAULT_MODULES):
    factory = CapturedLoaderFactory(fn)

    for k in list(sys.modules.keys()):
        if k not in preserved:
            del sys.modules[k]

    for finder in sys.path_importer_cache.values():
        if finder and hasattr(finder, "_loaders"):
            finder._loaders = factory.new_loaders(finder._loaders)

    for i in range(len(sys.path_hooks)):
        sys.path_hooks[i] = factory.hookwrap(sys.path_hooks[i])
    return factory


@contextlib.contextmanager
def capture(fn, preserved=None):
    preserved = preserved or DEFAULT_MODULES
    path_hooks = sys.path_hooks[:]
    loaders_map = {}
    for name, finder in sys.path_importer_cache.items():
        loaders_map[name] = getattr(finder, "_loaders", None)

    try:
        yield activate(fn, preserved)
    finally:
        sys.path_hooks = path_hooks
        for name, loaders in loaders_map.items():
            if loaders is not None:
                sys.path_importer_cache[name]._loaders = loaders
        # todo: recover for new imoported modules


SIGNALS = [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT, signal.SIGHUP]


@contextlib.contextmanager
def capture_with_signal_handle(fn, teardown=None, preserved=None, signals=SIGNALS, status=0):
    preserved = preserved or DEFAULT_MODULES

    def on_stop(signum, tb):
        if teardown is not None:
            teardown(signum, tb)
        else:
            print("trapped:", signum, file=sys.stderr)
        sys.exit(status)

    for s in signals:
        signal.signal(s, on_stop)

    with capture(fn, preserved=preserved) as factory:
        yield factory
